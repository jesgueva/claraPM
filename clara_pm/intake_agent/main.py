# Import necessary libraries
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from langchain_community.llms import OpenAI
from langchain_community.chains import RunnableSequence
from langchain_community.prompts import PromptTemplate
import redis
from clara_pm.shared.models import SessionLocal, TaskSpec
from clara_pm.intake_agent.langchain_utils import process_task_prompt
import uuid

# Initialize FastAPI app
app = FastAPI()

# Initialize Redis connection
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

# Define a Pydantic model for the task prompt
class TaskPrompt(BaseModel):
    session_id: str = None
    prompt: str

# Dependency to get DB session
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Define the /intake endpoint
@app.post("/intake")
async def intake_task(task_prompt: TaskPrompt, db: Session = Depends(get_db)):
    # Generate a session ID if not provided
    if not task_prompt.session_id:
        task_prompt.session_id = str(uuid.uuid4())

    # Store the prompt in Redis
    redis_client.rpush(task_prompt.session_id, task_prompt.prompt)

    # Retrieve the conversation history
    conversation_history = redis_client.lrange(task_prompt.session_id, 0, -1)
    full_conversation = "\n".join(conversation_history)

    # Process the task prompt
    task_spec = process_task_prompt(full_conversation)

    # Store the task spec and conversation in the database if the task is complete
    if "finalize" in task_spec.lower():
        new_task_spec = TaskSpec(prompt=task_prompt.prompt, spec=task_spec)
        db.add(new_task_spec)
        db.commit()
        db.refresh(new_task_spec)

    return {"session_id": task_prompt.session_id, "message": "Task received and processed", "prompt": task_prompt.prompt, "spec": task_spec, "conversation": full_conversation} 