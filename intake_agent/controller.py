from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from intake_agent.langchain_service import agent
from intake_agent.logger import conversation_logger, system_logger
from intake_agent.auth import (
    Token, User, authenticate_user, create_access_token, 
    get_current_active_user, users_db, ACCESS_TOKEN_EXPIRE_MINUTES
)
import uuid
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta

router = APIRouter()
system_logger.info("Controller module initialized")

# In-memory storage for conversation state
# Format: {username: {session_id: [messages]}}
user_conversation_store = {}

class Message(BaseModel):
    role: str
    content: str

class QueryRequest(BaseModel):
    input_text: str
    session_id: Optional[str] = None
    new_conversation: bool = False
    messages: Optional[List[Message]] = None

class UserSession(BaseModel):
    session_id: str
    created_at: datetime
    last_activity: datetime
    title: Optional[str] = None

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate user and provide access token."""
    user = authenticate_user(users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    system_logger.info(f"User {user.username} logged in successfully")
    return {"access_token": access_token, "token_type": "bearer"}

def _get_or_create_session(username: str, session_id: Optional[str], new_conversation: bool, provided_messages: Optional[List[Message]]):
    """Helper function to get or create a conversation session."""
    # Initialize user's conversation store if it doesn't exist
    if username not in user_conversation_store:
        user_conversation_store[username] = {}
    
    # Generate a new session ID if needed
    if new_conversation or not session_id:
        session_id = str(uuid.uuid4())[:8]
        conversation_logger.info(f"[USER:{username}][SESSION:{session_id}] Starting new conversation")
        messages = []
    else:
        conversation_logger.info(f"[USER:{username}][SESSION:{session_id}] Continuing existing conversation")
        
        # Use provided messages or retrieve existing ones
        if provided_messages:
            messages = [{"role": msg.role, "content": msg.content} for msg in provided_messages]
        else:
            user_sessions = user_conversation_store[username]
            
            if session_id not in user_sessions:
                conversation_logger.warning(f"[USER:{username}][SESSION:{session_id}] Session not found, creating new")
                session_id = str(uuid.uuid4())[:8]
                messages = []
            else:
                messages = user_sessions[session_id]
    
    return session_id, messages

def _extract_ai_content(response):
    """Extract AI content from the agent's response."""
    ai_content = ""
    
    if isinstance(response, dict):
        if "messages" in response:
            try:
                # Try to find AI messages
                ai_messages = []
                for msg in response["messages"]:
                    # Handle different message object types
                    if hasattr(msg, "type") and msg.type == "ai":
                        ai_messages.append(msg)
                    elif hasattr(msg, "get") and msg.get("type") == "ai":
                        ai_messages.append(msg)
                    elif hasattr(msg, "role") and msg.role == "assistant":
                        ai_messages.append(msg)
                    elif isinstance(msg, dict) and msg.get("role") == "assistant":
                        ai_messages.append(msg)
                
                if ai_messages:
                    last_ai_message = ai_messages[-1]
                    # Extract content based on message type
                    if hasattr(last_ai_message, "content"):
                        ai_content = last_ai_message.content
                    elif isinstance(last_ai_message, dict) and "content" in last_ai_message:
                        ai_content = last_ai_message["content"]
                elif len(response["messages"]) > 0:
                    # If no AI messages found but messages exist, use the last one
                    last_message = response["messages"][-1]
                    if hasattr(last_message, "content"):
                        ai_content = last_message.content
                    elif isinstance(last_message, dict) and "content" in last_message:
                        ai_content = last_message["content"]
            except Exception as e:
                conversation_logger.error(f"Error extracting AI message: {e}")
                ai_content = f"I encountered an error processing your request: {str(e)}"
        elif "content" in response:
            ai_content = response["content"]
        elif "response" in response:
            ai_content = response["response"]
        else:
            ai_content = str(response)
    else:
        ai_content = str(response)
    
    # If we still couldn't extract content, use a default message
    if not ai_content:
        ai_content = "I'm sorry, I couldn't process your request properly. Please try again."
    
    return ai_content

def _generate_session_title(messages):
    """Generate a title for a new conversation."""
    if len(messages) >= 2:  # Has first user message and AI response
        try:
            first_user_msg = messages[0]["content"]
            if len(first_user_msg) > 30:
                return first_user_msg[:30] + "..."
            return first_user_msg
        except Exception as e:
            conversation_logger.error(f"Error generating title: {e}")
    
    return "New Conversation"

def _format_messages(messages):
    """Format messages for frontend display."""
    formatted_messages = []
    for msg in messages:
        msg_type = "user" if msg["role"] == "user" else "ai"
        formatted_messages.append({"type": msg_type, "content": msg["content"]})
    return formatted_messages

@router.post("/query")
async def query_llm(request: QueryRequest, current_user: User = Depends(get_current_active_user)):
    """Process a query with the LLM agent, maintaining user-specific session state."""
    username = current_user.username
    
    # Get or create session
    session_id, messages = _get_or_create_session(
        username,
        request.session_id,
        request.new_conversation,
        request.messages
    )
    
    # Log the incoming request
    conversation_logger.info(f"[USER:{username}][SESSION:{session_id}] Received query: {request.input_text}")
    
    # Add the user message to the history
    messages.append({"role": "user", "content": request.input_text})
    
    try:
        # Use the agent to process the input
        response = agent.invoke(
            {"messages": messages},
            config={
                "configurable": {
                    "thread_id": f"{username}_{session_id}",
                    "username": username  # Pass username to be used by tools
                }
            }
        )
        
        # Extract the AI's response
        ai_content = _extract_ai_content(response)
        
        # Add the AI's response to the conversation history
        messages.append({"role": "assistant", "content": ai_content})
        
        # Store the updated conversation history
        user_conversation_store[username][session_id] = messages
        
        # Generate a title for new conversations
        session_title = None
        if len(messages) == 2:  # Just created with first exchange
            session_title = _generate_session_title(messages)
        
        # Log the conversation state
        conversation_logger.info(f"[USER:{username}][SESSION:{session_id}] Conversation updated. Messages: {len(messages)}")
        conversation_logger.info(f"[USER:{username}][SESSION:{session_id}] Response: {ai_content}")
        
        # Format the messages for the frontend
        formatted_messages = _format_messages(messages)
        
        # Return the response data
        return {
            "response": ai_content,
            "session_id": session_id,
            "messages": formatted_messages,
            "title": session_title
        }
    except Exception as e:
        conversation_logger.error(f"[USER:{username}][SESSION:{session_id}] Error: {str(e)}")
        return {
            "response": f"I'm sorry, there was an error processing your request: {str(e)}",
            "session_id": session_id,
            "messages": [
                {"type": "user", "content": request.input_text},
                {"type": "ai", "content": f"I'm sorry, there was an error processing your request: {str(e)}"}
            ],
            "error": str(e)
        }

@router.get("/sessions")
async def get_user_sessions(current_user: User = Depends(get_current_active_user)):
    """Retrieve all sessions for the current user."""
    username = current_user.username
    
    if username not in user_conversation_store:
        return {"sessions": []}
    
    # Create a list of sessions with metadata
    sessions = []
    for session_id, messages in user_conversation_store[username].items():
        # Generate a title based on the first user message
        title = f"Session {session_id}"
        if messages and len(messages) > 0:
            try:
                first_message = messages[0]["content"]
                if len(first_message) > 30:
                    title = first_message[:30] + "..."
                else:
                    title = first_message
            except (KeyError, TypeError):
                pass
        
        # Get last message preview if available
        last_message_preview = None
        if messages and len(messages) > 0 and "content" in messages[-1]:
            content = messages[-1]["content"]
            last_message_preview = content[:50] + "..." if len(content) > 50 else content
        
        sessions.append({
            "session_id": session_id,
            "title": title,
            "message_count": len(messages),
            "last_message": last_message_preview
        })
    
    return {"sessions": sessions}

@router.get("/sessions/{session_id}")
async def get_session(session_id: str, current_user: User = Depends(get_current_active_user)):
    """Retrieve the conversation history for a specific session."""
    username = current_user.username
    
    if username not in user_conversation_store or session_id not in user_conversation_store[username]:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Format the messages for the frontend
    messages = user_conversation_store[username][session_id]
    formatted_messages = _format_messages(messages)
    
    return {
        "session_id": session_id, 
        "messages": formatted_messages
    }

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str, current_user: User = Depends(get_current_active_user)):
    """Delete a session and its conversation history."""
    username = current_user.username
    
    if username not in user_conversation_store or session_id not in user_conversation_store[username]:
        raise HTTPException(status_code=404, detail="Session not found")
    
    del user_conversation_store[username][session_id]
    conversation_logger.info(f"[USER:{username}][SESSION:{session_id}] Session deleted")
    
    return {"success": True, "message": "Session deleted", "session_id": session_id} 