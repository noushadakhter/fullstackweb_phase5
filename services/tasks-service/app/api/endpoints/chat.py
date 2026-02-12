import os
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlmodel import Session
from typing import Optional, List

from backend.app.auth import get_current_user_id
from backend.app.database import get_session
from backend.app.crud import (
    create_conversation,
    get_conversation,
    create_message,
    get_messages_for_conversation
)
from backend.models import Role, Message as DBMessage, Conversation as DBConversation
from pydantic import BaseModel

from backend.app.agent_runner import AgentRunner # Import AgentRunner

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set.")
if not MCP_SERVER_URL:
    raise ValueError("MCP_SERVER_URL environment variable not set.")

# Initialize AgentRunner globally
agent_runner = AgentRunner(openai_api_key=OPENAI_API_KEY, mcp_server_url=MCP_SERVER_URL)

class ChatRequest(BaseModel):
    conversation_id: Optional[int] = None
    message: str

class ChatResponse(BaseModel):
    conversation_id: int
    response: str
    tool_calls: List # Will contain details of tool calls by the agent

router = APIRouter()

@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat_endpoint(
    user_id: str = Path(..., description="The ID of the user."),
    request: ChatRequest = Depends(),
    authenticated_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Handles chat interactions with the AI chatbot.
    """
    # Verify that the user_id in the path matches the authenticated user_id
    if user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User ID in path does not match authenticated user."
        )

    conversation: Optional[DBConversation] = None
    if request.conversation_id:
        conversation = crud.get_conversation(session, request.conversation_id, user_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found."
            )
    else:
        # Create a new conversation if no conversation_id is provided
        conversation = crud.create_conversation(session, user_id)

    # Save user message
    crud.create_message(session, user_id, conversation.id, Role.USER, request.message)

    # Fetch conversation history for the agent
    history: List[DBMessage] = crud.get_messages_for_conversation(session, conversation.id, user_id)

    # Run the agent with MCP tools
    agent_response = await agent_runner.run_agent_with_mcp_tools(
        session=session,
        user_id=user_id,
        conversation=conversation,
        user_message_content=request.message,
        history=history
    )

    # Save assistant message
    crud.create_message(session, user_id, conversation.id, Role.ASSISTANT, agent_response["response"])

    return ChatResponse(
        conversation_id=conversation.id,
        response=agent_response["response"],
        tool_calls=agent_response["tool_calls"]
    )