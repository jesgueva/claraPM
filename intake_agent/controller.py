from pydantic import BaseModel
from fastapi import APIRouter
from intake_agent.langchain_service import agent

router = APIRouter()

# Define a Pydantic model for the request body
class QueryRequest(BaseModel):
    input_text: str

@router.post("/query")
async def query_llm(request: QueryRequest):
    # Use the agent to process the input and generate a response
    response = agent.invoke(
        {"messages": [{"role": "user", "content": request.input_text}]},
        config={"configurable": {"thread_id": "1"}}  # Add thread_id for conversation tracking
    )
    return {"response": response} 