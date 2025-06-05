from langchain_core.runnables import RunnableSequence
from langchain.chat_models import init_chat_model
from langchain.prompts import PromptTemplate
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
import os
from dotenv import load_dotenv
from shared.models import create_task, SessionLocal, delete_task, get_tasks
from datetime import datetime
from intake_agent.logger import db_logger, agent_logger

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

# Create a runnable sequence with the prompt and llm
llm_chain = RunnableSequence(prompt_template, llm)

# Create the agent with memory
checkpointer = InMemorySaver()

# Import the system prompt from a separate file
from .system_prompt import system_prompt

# Function to save tasks to the database
def save_tasks_to_db(tasks, username=None, config=None):
    """
    Save a list of tasks to the database using the create_task function.
    
    Args:
        tasks: List of task dictionaries to save
        username: Optional username of the current user, used for created_by if not specified
        config: Configuration passed from agent, may contain username
    """
    # Extract username from config if provided
    if not username and config and 'username' in config:
        username = config['username']
    
    db = SessionLocal()
    try:
        # Validate that we received a list
        if not isinstance(tasks, list):
            error_msg = f"Expected a list of tasks, but received: {type(tasks)}"
            db_logger.error(error_msg)
            raise ValueError(error_msg)
            
        for i, task in enumerate(tasks):
            try:
                # Verify required fields are present (except created_by which can be set from username)
                required_fields = ['title', 'description', 'user_id', 'project_id', 
                                  'priority', 'role_required']
                missing_fields = [field for field in required_fields if field not in task]
                
                if missing_fields:
                    error_msg = f"Missing required fields: {', '.join(missing_fields)}"
                    db_logger.error(f"Task {i+1}: {error_msg}")
                    raise KeyError(error_msg)
                
                # Set created_by to username if not specified in task
                if 'created_by' not in task or not task['created_by']:
                    if username:
                        task['created_by'] = username
                        db_logger.info(f"Setting created_by to current user: {username}")
                    else:
                        task['created_by'] = 'system'
                        
                # Convert deadline string to datetime object if it exists
                deadline = None
                if 'deadline' in task and task['deadline']:
                    try:
                        # Parse ISO format date string (YYYY-MM-DD)
                        deadline = datetime.strptime(task['deadline'], '%Y-%m-%d').date()
                    except ValueError as e:
                        error_msg = f"Invalid deadline format in task {i+1}: {task['deadline']}"
                        db_logger.error(f"{error_msg}. Deadline should be in YYYY-MM-DD format")
                        raise ValueError(f"Invalid deadline format: {e}")
                
                # Create the task with provided values
                create_task(
                    db,
                    title=task['title'],
                    description=task['description'],
                    user_id=task['user_id'],
                    project_id=task['project_id'],
                    priority=task['priority'],
                    role_required=task['role_required'],
                    deadline=deadline,  # Now a properly converted datetime object
                    created_by=task['created_by']
                )
                db_logger.info(f"Successfully saved task {i+1}: {task['title']}")
            except KeyError as ke:
                db_logger.error(f"Error in task {i+1}: {ke}")
                db_logger.error(f"Task data: {task}")
                db_logger.error("Tasks must follow the required format with fields: title, description, user_id, project_id, priority, role_required")
                db.rollback()
                raise
            except Exception as task_error:
                db_logger.error(f"Error saving task {i+1}: {task_error}")
                db_logger.error(f"Task data: {task}")
                db.rollback()
                raise
    except Exception as e:
        db_logger.error(f"An error occurred while saving tasks: {e}")
        db.rollback()  # Rollback any pending transactions
    finally:
        db.close()

# Function to delete a task by ID
def delete_task_by_id(task_id):
    """Delete a task from the database by its ID."""
    db = SessionLocal()
    try:
        db_logger.info(f"Attempting to delete task with ID: {task_id}")
        delete_task(db, task_id)
        db_logger.info(f"Successfully deleted task with ID: {task_id}")
    except Exception as e:
        db_logger.error(f"An error occurred while deleting task ID {task_id}: {e}")
    finally:
        db.close()

# Function to retrieve tasks by name or description
def retrieve_tasks_by_name_or_description(search_term):
    """Retrieve tasks from the database that match the given name or description."""
    db = SessionLocal()
    try:
        db_logger.info(f"Searching for tasks with term: '{search_term}'")
        tasks = get_tasks(db)
        matching_tasks = [task for task in tasks if search_term.lower() in task.title.lower() or search_term.lower() in task.description.lower()]
        db_logger.info(f"Found {len(matching_tasks)} tasks matching '{search_term}'")
        return matching_tasks
    except Exception as e:
        db_logger.error(f"An error occurred while retrieving tasks with search term '{search_term}': {e}")
        return []
    finally:
        db.close()

# List of tools for the agent
tools = [
    save_tasks_to_db,
    delete_task_by_id,
    retrieve_tasks_by_name_or_description
]

# Log agent initialization
agent_logger.info("Initializing ReAct agent with tools and system prompt")

# Create the agent
agent = create_react_agent(
    model=llm,
    tools=tools,
    prompt=system_prompt,
    checkpointer=checkpointer
)

agent_logger.info("Agent initialization complete")