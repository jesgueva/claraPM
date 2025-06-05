from fastapi import FastAPI, HTTPException
from shared.logger import log_decision
from .agent import process_task_assignment
from shared.models import SessionLocal, Task, Assignment, User
from .tools import assign_task_to_developer

app = FastAPI()

@app.post("/assign/intelligent")
async def assign_task_intelligent(task_id: int, developer_id: int):
    result = await process_task_assignment(task_id, developer_id)
    
    if "error" in result:
        log_decision(f"Assignment failed: {result['error']}", task_id=task_id, developer_id=developer_id)
        raise HTTPException(status_code=400, detail=result["error"])
    
    log_decision(f"AI Agent decision: {result.get('agent_response', '')[:100]}...", task_id=task_id, developer_id=developer_id)
    return result 

@app.post("/assign/intelligent/batch")
async def assign_all_intelligent():
    """Find all unassigned tasks and assign each one to an available developer based on the least number of current assignments."""
    db = SessionLocal()

    # Retrieve unassigned tasks: tasks that are not present in the Assignment table.
    unassigned_tasks = db.query(Task).filter(~Task.id.in_(db.query(Assignment.task_id))).all()
    
    # Retrieve available developers: users with role 'developer' and not disabled.
    available_developers = db.query(User).filter(User.role=='developer', User.disabled==False).all()
    
    if not unassigned_tasks:
        return {"message": "No unassigned tasks found."}
    
    if not available_developers:
        return {"message": "No available developers found."}
    
    # Build a dictionary mapping developer ID to their current assignment count
    developer_assignment_counts = {dev.id: db.query(Assignment).filter(Assignment.user_id == dev.id).count() for dev in available_developers}
    
    assignments_results = []
    
    # For each unassigned task, select the developer with the lowest assignment count and assign the task
    for task in unassigned_tasks:
        selected_dev_id = min(developer_assignment_counts, key=developer_assignment_counts.get)
        result = assign_task_to_developer(task.id, selected_dev_id)
        if result.get("success"):
            developer_assignment_counts[selected_dev_id] += 1
        assignments_results.append({"task_id": task.id, "developer_id": selected_dev_id, "result": result})
    
    db.commit()
    return {"assignments": assignments_results} 