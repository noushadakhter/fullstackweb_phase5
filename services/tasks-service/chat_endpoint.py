from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from . import models, db, agent
# from .dependencies import get_current_user # To protect the endpoint

router = APIRouter(tags=["Chat"])

@router.post("/api/{user_id}/chat")
def handle_chat(
    user_id: int,
    request: models.ChatRequest,
    session: Session = Depends(db.get_session),
    # current_user: models.User = Depends(get_current_user) # Protect endpoint
):
    # Authorization check: Ensure the user_id from path matches the logged-in user
    # if current_user.id != user_id:
    #     raise HTTPException(status_code=403, detail="Cannot access another user's conversation")

    conversation_id = request.conversation_id
    
    # Get or create conversation
    if conversation_id:
        conversation = session.get(models.Conversation, conversation_id)
        if not conversation or conversation.user_id != user_id:
            raise HTTPException(status_code=404, detail="Conversation not found or access denied")
    else:
        conversation = models.Conversation(user_id=user_id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        conversation_id = conversation.id

    # Save user message
    user_message = models.Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role="user",
        content=request.message
    )
    session.add(user_message)
    session.commit()

    # Run agent logic
    agent_result = agent.run_agent_conversation(
        user_id=user_id,
        conversation_id=conversation_id,
        message=request.message
    )

    # Save assistant message
    assistant_message = models.Message(
        conversation_id=conversation_id,
        user_id=user_id, # The user context for the whole conversation
        role="assistant",
        content=agent_result["response"]
    )
    session.add(assistant_message)
    session.commit()

    # Return final response
    return {
        "conversation_id": conversation_id,
        "response": agent_result["response"],
        "tool_calls": agent_result["tool_calls"]
    }
