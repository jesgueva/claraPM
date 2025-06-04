import redis

# Redis client setup
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

# Function to store conversation state
def store_conversation_state(user_id: str, message: str):
    redis_client.set(user_id, message)

# Function to retrieve conversation state
def get_conversation_state(user_id: str) -> str:
    return redis_client.get(user_id) 