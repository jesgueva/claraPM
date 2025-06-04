from langchain import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
import os
from dotenv import load_dotenv

load_dotenv()
# Set the OpenAI API key
openai_api_key = os.getenv('OPENAI_API_KEY')

# Initialize OpenAI model with API key
llm = OpenAI(temperature=0.5, openai_api_key=openai_api_key)

# Initialize memory for conversation
memory = ConversationBufferMemory()

# Create a conversation chain with OpenAI
conversation_chain = ConversationChain(llm=llm, memory=memory)

# Function to process user message and generate response
def process_message(user_id: str, message: str) -> str:
    # Generate response using the conversation chain
    response = conversation_chain.run(input=message)
    
    # Return the response
    return response 