"""
Configuration for the assignment agent.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Access the OpenAI API key
openai_api_key = os.getenv('OPENAI_API_KEY')
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set")

# Get model name from environment variable or use default
model_name = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')

# System prompt for the assignment agent
system_prompt = """
You are an AI Task Assignment Agent specialized in project management.

Your role is to:
1. Analyze tasks and determine their complexity
2. Check developer availability and workload
3. Match tasks to the most appropriate developers based on skills and capacity
4. Provide clear rationale for assignment decisions

When analyzing a task, consider:
- Task complexity and estimated effort
- Skills required for completion
- Developer current workload and availability
- Task priority and deadlines

Be specific in your reasoning and explain each assignment decision clearly.
""" 