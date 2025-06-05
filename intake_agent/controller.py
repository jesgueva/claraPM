from pydantic import BaseModel
from fastapi import APIRouter
from intake_agent.langchain_service import agent
from intake_agent.logger import conversation_logger, system_logger
import uuid

router = APIRouter()

system_logger.info("Controller module initialized")

# Define a Pydantic model for the request body
class QueryRequest(BaseModel):
    input_text: str
    session_id: str = None

@router.post("/query")
async def query_llm(request: QueryRequest):
    # Generate a unique conversation ID if not provided
    session_id = request.session_id or str(uuid.uuid4())[:8]
    
    # Log the incoming request with conversation ID
    conversation_logger.info(f"[SESSION:{session_id}] Received query: {request.input_text}")
    
    # Use the agent to process the input and generate a response
    response = agent.invoke(
        {"messages": [{"role": "user", "content": request.input_text}]},
        config={"configurable": {"thread_id": session_id}}  # Use session_id for conversation tracking
    )
    
    # Log the response with same conversation ID
    conversation_logger.info(f"[SESSION:{session_id}] Generated response: {response}")
    
    return {"response": response, "session_id": session_id} 