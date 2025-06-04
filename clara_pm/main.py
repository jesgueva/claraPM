from fastapi import FastAPI
from langchain.chains import LLMChain
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
import os
from langchain.prompts import PromptTemplate
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

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

# Mount the static directory to serve static files
app.mount("/static", StaticFiles(directory="clara_pm/static"), name="static")

# Define a Pydantic model for the request body
class QueryRequest(BaseModel):
    input_text: str

@app.get("/")
async def serve_index():
    return FileResponse("clara_pm/static/index.html")

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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/query")
async def query_llm(request: QueryRequest):
    # Use the agent to process the input and generate a response
    response = agent.invoke(
        {"messages": [{"role": "user", "content": request.input_text}]},
        config={"configurable": {"thread_id": "1"}}  # Add thread_id for conversation tracking
    )
    return {"response": response}

# Placeholder for Langchain and Langraph integration
# TODO: Implement LLM interaction logic here 