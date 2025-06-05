# Assignment Agent

This assignment agent uses LangChain, LangGraph, and FastAPI to intelligently assign tasks to developers based on their skills and availability.

## Features

- LLM-powered task assignment decisions using LangChain/LangGraph
- Redis for storing task and developer information
- FastAPI endpoints for task assignment
- Behavior tree integration for task planning

## Prerequisites

- Python 3.8+
- Redis server running locally
- OpenAI API key

## Installation

1. Install required packages:

```bash
pip install fastapi uvicorn redis py-trees langchain langgraph openai python-dotenv
```

2. Set up environment variables:

Create a `.env` file in the project root with:

```
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o-mini  # or another available model
```

## Setup Test Data

Run the following command to populate Redis with test data:

```bash
python -m assignment_agent.setup_test_data
```

To clear existing data:

```bash
python -m assignment_agent.setup_test_data --clear
```

## Running the Server

Start the FastAPI server:

```bash
uvicorn assignment_agent.main:app --reload
```

## API Endpoints

### Traditional Task Assignment

```
POST /assign
```

Parameters:
- `task_id`: ID of the task to assign
- `developer_id`: ID of the developer to assign the task to

### Intelligent Task Assignment

```
POST /assign/intelligent
```

Parameters:
- `task_id`: ID of the task to assign
- `developer_id`: ID of the developer to assign the task to

This endpoint uses an LLM-powered agent to make an intelligent assignment decision based on task requirements and developer skills/availability.

## Example Usage

Assign a task using the intelligent endpoint:

```bash
curl -X POST "http://localhost:8000/assign/intelligent?task_id=1&developer_id=102"
```

## Architecture

The system consists of:

1. **FastAPI Application**: Provides API endpoints for task assignment
2. **LangChain/LangGraph Agent**: Makes intelligent assignment decisions
3. **Redis**: Stores task and developer information
4. **Behavior Trees**: Used for task planning and breakdown

## Contributing

Feel free to submit issues and pull requests. 