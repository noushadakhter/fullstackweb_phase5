import json
from typing import List, Dict, Any, Optional

from openai import OpenAI
from openai.types.beta.threads import Message as OpenAIMessage
from openai.types.beta.threads.runs import ToolCall
from sqlmodel import Session

from backend.app import crud
from backend.models import Role, Message as DBMessage, Conversation as DBConversation
from mcp_server.tools import ALL_TOOLS # Import the MCP tools

class AgentRunner:
    def __init__(self, openai_api_key: str, mcp_server_url: str):
        self.client = OpenAI(api_key=openai_api_key)
        self.mcp_server_url = mcp_server_url
        self.assistant = self._create_or_retrieve_assistant()
        self.available_tools = {tool.name: tool for tool in ALL_TOOLS} # Map tool names to FastMCP Tool objects

    def _create_or_retrieve_assistant(self):
        # In a production setup, you'd store the assistant ID and retrieve it.
        # For this example, we'll recreate or just define.
        # More robust handling needed for persistent assistants.

        # Check if an assistant with the desired name already exists
        # assistants = self.client.beta.assistants.list(limit=10)
        # for existing_assistant in assistants.data:
        #     if existing_assistant.name == "Todo AI Chatbot Assistant":
        #         print(f"Using existing assistant: {existing_assistant.id}")
        #         return existing_assistant

        print("Creating a new OpenAI Assistant...")
        tool_schemas = [tool.openapi_schema for tool in ALL_TOOLS]
        
        # Manually convert Tool objects to dict as OpenAI client expects dict for tools
        openai_tools_format = []
        for tool in ALL_TOOLS:
            openai_tools_format.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters.model_json_schema()
                }
            })

        assistant = self.client.beta.assistants.create(
            name="Todo AI Chatbot Assistant",
            instructions=(
                "You are a helpful AI assistant for managing todo lists. "
                "You can add, list, complete, delete, and update tasks. "
                "Always confirm actions with the user before performing them, "
                "and ask for necessary details (e.g., user_id, task_id, title, description). "
                "Use the provided tools to interact with the todo list."
                "When listing tasks, specify 'all', 'pending', or 'completed' status if not provided."
                "Ensure user_id is always passed to tools."
            ),
            model="gpt-4o", # Or gpt-3.5-turbo-1106, gpt-4-turbo, gpt-4o, etc.
            tools=openai_tools_format # Pass the converted tool format
        )
        print(f"Created new assistant with ID: {assistant.id}")
        return assistant

    async def run_agent_with_mcp_tools(
        self,
        session: Session,
        user_id: str,
        conversation: DBConversation,
        user_message_content: str,
        history: List[DBMessage]
    ) -> Dict[str, Any]:
        
        thread_id = conversation.id # Use conversation_id as thread_id for OpenAI Assistant
        
        # Ensure the thread exists or create a new one for the assistant
        try:
            thread = self.client.beta.threads.retrieve(thread_id=str(thread_id))
        except Exception:
            thread = self.client.beta.threads.create(
                messages=[
                    {
                        "role": "user",
                        "content": user_message_content,
                    }
                ]
            )
            thread_id = thread.id # Update thread_id if a new thread was created


        # Add the user message to the thread if it's not already the first message of a new thread
        # Or if the thread already exists
        if not thread.messages: # If it's a brand new empty thread that we just created
             self.client.beta.threads.messages.create(
                thread_id=str(thread_id),
                role="user",
                content=user_message_content,
            )
        else:
            # Check if the last message in the thread is the same as the user_message_content
            # This is to avoid adding duplicate user messages if the thread was just created with the message
            last_thread_message = self.client.beta.threads.messages.list(thread_id=str(thread_id), limit=1).data
            if not last_thread_message or last_thread_message[0].content[0].text.value != user_message_content:
                self.client.beta.threads.messages.create(
                    thread_id=str(thread_id),
                    role="user",
                    content=user_message_content,
                )

        # Run the assistant
        run = self.client.beta.threads.runs.create(
            thread_id=str(thread_id),
            assistant_id=self.assistant.id,
            # We don't provide extra instructions here as they are set in the assistant itself.
        )

        # Polling loop for run status
        while run.status in ['queued', 'in_progress', 'cancelling']:
            run = self.client.beta.threads.runs.retrieve(
                thread_id=str(thread_id),
                run_id=run.id
            )
            # In a real app, you might want a delay here to avoid hammering the API
            # time.sleep(0.5)

        if run.status == 'requires_action':
            tool_outputs = []
            for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                
                print(f"Agent requested to call tool: {function_name} with args: {arguments}")
                
                if function_name in self.available_tools:
                    # Dynamically call the tool function
                    # Ensure user_id is passed, and session for CRUD operations
                    arguments['user_id'] = user_id # Ensure user_id from context is passed
                    
                    # Need to ensure the session is passed correctly for actual execution
                    # For now, we'll mock the session injection, but in a real setup
                    # the tool execution environment would provide the session.
                    
                    try:
                        # FastMCP tool functions are defined as `async def func(params, session)`
                        # We need to map the arguments from OpenAI's ToolCall to our ToolParam BaseModel
                        tool_param_model = self.available_tools[function_name].parameters
                        
                        # Create an instance of the ToolParam BaseModel from arguments
                        param_instance = tool_param_model(**arguments)
                        
                        # Call the tool function with the parameter instance and the session
                        tool_result = await self.available_tools[function_name].func(param_instance, session)
                        output = json.dumps(tool_result.model_dump())
                        print(f"Tool {function_name} executed, output: {output}")
                    except HTTPException as e:
                        output = json.dumps({"error": e.detail, "status_code": e.status_code})
                        print(f"Tool {function_name} execution failed: {output}")
                    except Exception as e:
                        output = json.dumps({"error": str(e), "status_code": 500})
                        print(f"Tool {function_name} execution failed: {output}")
                else:
                    output = json.dumps({"error": f"Tool {function_name} not found."})
                    print(f"Tool {function_name} not found.")
                
                tool_outputs.append({
                    "tool_call_id": tool_call.id,
                    "output": output,
                })
            
            # Submit tool outputs and poll again
            run = self.client.beta.threads.runs.submit_tool_outputs(
                thread_id=str(thread_id),
                run_id=run.id,
                tool_outputs=tool_outputs
            )

            while run.status in ['queued', 'in_progress', 'cancelling']:
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=str(thread_id),
                    run_id=run.id
                )
                # time.sleep(0.5)

        if run.status == 'completed':
            messages = self.client.beta.threads.messages.list(
                thread_id=str(thread_id)
            )
            
            assistant_response_message = None
            tool_calls_performed = []
            
            # Find the last assistant message and any tool calls it made
            for msg in reversed(messages.data): # Iterate in reverse to get most recent
                if msg.run_id == run.id and msg.role == "assistant":
                    assistant_response_message = msg
                    break
            
            if assistant_response_message and assistant_response_message.content:
                response_text = ""
                for content_block in assistant_response_message.content:
                    if content_block.type == "text":
                        response_text += content_block.text.value
                    elif content_block.type == "tool_calls":
                        # This part is for messages containing tool calls (not tool_outputs)
                        # The OpenAI API represents these as specific content blocks
                        for tool_call_obj in content_block.tool_calls:
                            tool_calls_performed.append({
                                "name": tool_call_obj.function.name,
                                "arguments": json.loads(tool_call_obj.function.arguments)
                            })
                
                return {
                    "response": response_text,
                    "tool_calls": tool_calls_performed, # This might be empty if no tool calls were made in the response
                    "thread_id": int(thread_id)
                }
            else:
                return {
                    "response": "No relevant assistant response found.",
                    "tool_calls": [],
                    "thread_id": int(thread_id)
                }
        else:
            return {
                "response": f"Run finished with status: {run.status}. Please try again.",
                "tool_calls": [],
                "thread_id": int(thread_id)
            }
