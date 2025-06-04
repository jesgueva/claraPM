from langchain.chains import LLMChain
from langchain.chat_models import init_chat_model
from langchain.prompts import PromptTemplate
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the OpenAI API key
openai_api_key = os.getenv('OPENAI_API_KEY')

# Initialize the chat model compatible with Langraph
llm = init_chat_model(
    model="gpt-4o-mini",
    api_key=openai_api_key
)

# Define a simple prompt template
prompt_template = PromptTemplate.from_template("""
You are a project manager. Respond to the following query:
{input_text}
""")

# Create a simple LLM chain with the prompt template
llm_chain = LLMChain(llm=llm, prompt=prompt_template)

# Define a simple tool function
# This is a placeholder; replace with actual tools as needed
def simple_tool(input_text: str) -> str:
    """Process the input text and return a response."""
    return f"Processed: {input_text}"

# Create the agent with memory
checkpointer = InMemorySaver()
agent = create_react_agent(
    model=llm,
    tools=[simple_tool],
    prompt="You are a project manager. Respond to the following query:",
    checkpointer=checkpointer
) 