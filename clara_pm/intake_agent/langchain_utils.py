import os
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Set up OpenAI API key
os.environ['OPENAI_API_KEY'] = 'your-openai-api-key'

# Define a prompt template for LangChain
prompt_template = PromptTemplate(
    input_variables=["prompt"],
    template="""
    You are an AI assistant. Your task is to help refine the following task prompt until it is well-defined:
    {prompt}
    Please ask any necessary follow-up questions to clarify the task.
    """
)

# Initialize LangChain with OpenAI
llm_chain = LLMChain(
    llm=OpenAI(temperature=0.7),
    prompt=prompt_template
)

# Function to process task prompt using LangChain and OpenAI
def process_task_prompt(prompt):
    # Use LangChain to refine the task prompt
    refined_prompt = llm_chain.run(prompt)
    return refined_prompt 