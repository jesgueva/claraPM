"""
Assignment agent implementation using LangChain and py_trees.
"""

from langchain_core.runnables import RunnableSequence
from langchain.chat_models import init_chat_model
from langchain.prompts import PromptTemplate
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from fastapi import FastAPI, HTTPException
from logger.config import agent_logger

# Import configuration
from .config import openai_api_key, model_name, system_prompt

# Import behavior tree
from .behavior_tree import assignment_tree

# Import tools
from .tools import tools, analyze_task_assignment_fit

# Initialize the chat model compatible with Langraph
llm = init_chat_model(
    model=model_name,
    api_key=openai_api_key
)

agent_logger.info(f"Using OpenAI model: {model_name}")

# Create memory saver for the agent
checkpointer = InMemorySaver()

# Create the agent
try:
    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=system_prompt,
        checkpointer=checkpointer
    )
    agent_logger.info("Assignment agent initialization complete")
except Exception as e:
    agent_logger.error(f"Failed to initialize agent: {str(e)}")
    raise

async def process_task_assignment(task_id, developer_id):
    """
    Process a task assignment request using the LLM-powered agent
    
    Args:
        task_id: ID of the task to assign
        developer_id: ID of the developer to consider assigning to
        
    Returns:
        Assignment decision and explanation
    """
    try:
        # First, analyze the assignment using the behavior tree
        analysis = analyze_task_assignment_fit(task_id, developer_id)
        
        # Run the agent with the assignment query and include the analysis
        response = agent.invoke({
            "input": f"Analyze task {task_id} and determine if it should be assigned to developer {developer_id}. The behavior tree analysis shows: {analysis['recommendation']} with explanation: {analysis.get('explanation', 'No explanation available')}. Consider this along with the developer's current workload and availability."
        })
        
        if isinstance(response, dict) and "output" in response:
            return {
                "task_id": task_id,
                "developer_id": developer_id,
                "agent_response": response["output"],
                "behavior_tree_analysis": analysis,
                "processed": True
            }
        else:
            return {
                "error": "Agent processing failed",
                "task_id": task_id,
                "developer_id": developer_id
            }
    except Exception as e:
        agent_logger.error(f"Error in agent processing: {e}")
        return {"error": str(e)} 