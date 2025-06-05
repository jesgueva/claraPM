"""
Tool functions for the assignment agent.
"""

import json
import uuid
import time
from logger.config import agent_logger
from .behavior_tree import assignment_tree
from shared.models import get_task, get_user, Assignment, get_db


def get_task_details(task_id, config=None):
    """Retrieve detailed information for a task given its ID from the database."""
    db = get_db()
    task = get_task(db, task_id)
    if not task:
        return {"error": f"Task with ID {task_id} not found"}
    result = {
        "id": task.id,
        "project_id": task.project_id,
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "role_required": task.role_required,
        "deadline": task.deadline.isoformat() if task.deadline else None,
        "created_by": task.created_by,
        "user_id": task.user_id
    }
    return result


def check_developer_availability(developer_id, config=None):
    """Check a developer's availability by counting current assignments and evaluating the user status."""
    db = get_db()
    user = get_user(db, developer_id)
    if not user:
        return {"error": f"Developer with ID {developer_id} not found"}
    task_count = db.query(Assignment).filter(Assignment.user_id == developer_id).count()
    availability = "available" if not user.disabled else "unavailable"
    return {
        "developer_id": developer_id,
        "availability": availability,
        "current_task_count": task_count
    }


def assign_task_to_developer(task_id, developer_id, config=None):
    """Assign a task to a developer by creating an assignment record in the database."""
    db = get_db()
    task = get_task(db, task_id)
    if not task:
        return {"error": f"Task with ID {task_id} not found"}
    user = get_user(db, developer_id)
    if not user:
        return {"error": f"Developer with ID {developer_id} not found"}
    if user.disabled:
        return {"error": f"Developer {developer_id} is not available"}
    assignment = Assignment(task_id=task_id, user_id=developer_id)
    db.add(assignment)
    db.commit()
    return {
        "success": True,
        "task_id": task_id,
        "developer_id": developer_id,
        "message": f"Task {task_id} successfully assigned to developer {developer_id}"
    }


def analyze_task_assignment_fit(task_id, developer_id, config=None):
    """Analyze the fit of a task assignment using a behavior tree based evaluation."""
    try:
        result = assignment_tree.analyze_assignment(task_id, developer_id)
        if "error" not in result:
            recommendation = result["recommendation"]
            skill_match = result["skill_match"]
            workload = result["workload"]
            explanations = {
                "Highly recommended match": f"Developer has excellent skill match ({skill_match:.0%}) and available capacity ({(1-workload):.0%} available).",
                "Good match": f"Developer has good skill match ({skill_match:.0%}) and reasonable capacity ({(1-workload):.0%} available).",
                "Consider other developers": f"Developer has limited skill match ({skill_match:.0%}) or high workload ({workload:.0%} of capacity used)."
            }
            result["explanation"] = explanations.get(recommendation, "No detailed explanation available.")
        return result
    except Exception as e:
        agent_logger.error(f"Error analyzing task assignment fit: {e}")
        return {"error": str(e)}


tools = [
    get_task_details,
    check_developer_availability,
    assign_task_to_developer,
    analyze_task_assignment_fit
] 