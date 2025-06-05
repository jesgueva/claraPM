from fastapi import FastAPI, HTTPException
import py_trees
import redis
from shared.policies import can_assign_more_tasks
from shared.logger import log_decision

# Initialize FastAPI app
app = FastAPI()

# Connect to Redis
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

# Define a simple behavior tree for task planning
class TaskPlanner(py_trees.behaviour.Behaviour):
    def __init__(self, name):
        super(TaskPlanner, self).__init__(name)

    def update(self):
        # Placeholder logic for task planning
        # Here we would implement the logic to break down tasks into subtasks
        return py_trees.common.Status.SUCCESS

# Example function to create a behavior tree
async def create_behavior_tree(task_id: int):
    root = py_trees.composites.Sequence(name="Task Planner Sequence")
    task_planner = TaskPlanner(name="Task Planner")
    root.add_child(task_planner)
    return root

# Example function to check developer availability
async def check_developer_availability(developer_id: int):
    # Placeholder logic to check availability
    # Here we would query Redis to get the developer's availability status
    availability = redis_client.get(f"developer:{developer_id}:availability")
    return availability

# Example function to get the current task count for a developer
async def get_current_task_count(developer_id: int) -> int:
    # Placeholder logic to get the current task count
    # Here we would query a database or another source to get the task count
    task_count = redis_client.get(f"developer:{developer_id}:task_count")
    return int(task_count) if task_count else 0

# Update the assign_task function to log decisions
@app.post("/assign")
async def assign_task(task_id: int, developer_id: int):
    # Check developer availability
    availability = await check_developer_availability(developer_id)
    if not availability:
        log_decision("Developer not available", task_id=task_id, developer_id=developer_id)
        return {"message": "Developer not available", "task_id": task_id, "developer_id": developer_id}
    
    # Check if the developer can take more tasks
    current_task_count = await get_current_task_count(developer_id)
    if not await can_assign_more_tasks(developer_id, current_task_count):
        log_decision("Developer has reached the maximum task limit", task_id=task_id, developer_id=developer_id)
        return {"message": "Developer has reached the maximum task limit", "task_id": task_id, "developer_id": developer_id}
    
    # Log the task assignment decision
    log_decision("Task assigned", task_id=task_id, developer_id=developer_id)
    
    # Create and execute the behavior tree
    behavior_tree = await create_behavior_tree(task_id)
    behavior_tree.tick_once()
    return {"message": "Task assignment in progress", "task_id": task_id, "developer_id": developer_id} 