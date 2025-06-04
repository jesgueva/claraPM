from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import redis
import logging
from .langchain_chain import process_message

# Initialize FastAPI app
app = FastAPI()

# Redis client setup
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

# Logger setup
logging.basicConfig(filename='logs/intake_log.json', level=logging.INFO, format='%(asctime)s %(message)s')

# Pydantic model for request body
class Message(BaseModel):
    user_id: str
    message: str

@app.post("/intake/message")
async def handle_message(message: Message):
    try:
        # Process the message using the updated process_message function
        response = process_message(message.user_id, message.message)
        
        # Log the interaction
        logging.info({"user_id": message.user_id, "message": message.message, "response": response})
        
        # Return the response
        return {"response": response}
    except Exception as e:
        logging.error(f"Error handling message: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error") 