# Define a policy for maximum tasks per developer
MAX_TASKS_PER_DEVELOPER = 3

# Example function to check if a developer can take more tasks
async def can_assign_more_tasks(developer_id: int, current_task_count: int) -> bool:
    return current_task_count < MAX_TASKS_PER_DEVELOPER

# Define other policies as needed, such as work hours, etc.
# For now, we'll focus on the max tasks per developer policy.
