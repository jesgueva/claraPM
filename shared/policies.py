"""
Task assignment policies for determining workload and task matching.
"""

import logging

logger = logging.getLogger(__name__)

# Maximum task limits by role
MAX_TASK_LIMITS = {
    "frontend": 3,
    "backend": 4,
    "fullstack": 3,
    "qa": 5,
    "devops": 2,
    "default": 3  # Default limit for any other role
}

async def can_assign_more_tasks(developer_id: int, current_task_count: int, role: str = "default") -> bool:
    """
    Determine if a developer can be assigned more tasks based on their current workload.
    
    Args:
        developer_id: The ID of the developer
        current_task_count: The current number of assigned tasks
        role: The developer's role (frontend, backend, etc.)
    
    Returns:
        True if more tasks can be assigned, False otherwise
    """
    # Get the maximum task limit for this role
    max_tasks = MAX_TASK_LIMITS.get(role.lower(), MAX_TASK_LIMITS["default"])
    
    # Check if the developer has reached their limit
    can_assign = current_task_count < max_tasks
    
    logger.info(f"Developer {developer_id} has {current_task_count} tasks. Max allowed: {max_tasks}. Can assign more: {can_assign}")
    
    return can_assign

async def is_developer_qualified(developer_skills: list, task_required_skills: list) -> bool:
    """
    Determine if a developer has the required skills for a task.
    
    Args:
        developer_skills: List of the developer's skills
        task_required_skills: List of skills required for the task
    
    Returns:
        True if the developer has all required skills, False otherwise
    """
    # Convert lists to sets for efficient intersection
    dev_skills_set = set([s.lower() for s in developer_skills])
    task_skills_set = set([s.lower() for s in task_required_skills])
    
    # Check if all required skills are in the developer's skill set
    missing_skills = task_skills_set - dev_skills_set
    is_qualified = len(missing_skills) == 0
    
    logger.info(f"Developer skills: {dev_skills_set}, Task requires: {task_skills_set}")
    logger.info(f"Missing skills: {missing_skills}, Is qualified: {is_qualified}")
    
    return is_qualified

async def calculate_assignment_score(
    developer_skills: list,
    task_required_skills: list,
    current_task_count: int,
    task_priority: str
) -> float:
    """
    Calculate a score representing how good a match this developer is for this task.
    Higher scores indicate better matches.
    
    Args:
        developer_skills: List of the developer's skills
        task_required_skills: List of skills required for the task
        current_task_count: The current number of assigned tasks
        task_priority: The task priority (low, medium, high)
    
    Returns:
        A score from 0.0 to 1.0 representing the match quality
    """
    # Base score
    score = 0.0
    
    # Convert lists to sets for efficient operations
    dev_skills_set = set([s.lower() for s in developer_skills])
    task_skills_set = set([s.lower() for s in task_required_skills])
    
    # Calculate skill match percentage
    if task_skills_set:
        matching_skills = dev_skills_set.intersection(task_skills_set)
        skill_score = len(matching_skills) / len(task_skills_set)
    else:
        skill_score = 1.0  # No skills required means anyone can do it
    
    # Adjust for workload (lower task count is better)
    workload_score = 1.0 - (current_task_count / 10)  # Assumes max 10 tasks
    workload_score = max(0.1, workload_score)  # Ensure minimum score of 0.1
    
    # Adjust for priority
    priority_weight = {
        "low": 0.5,
        "medium": 0.75,
        "high": 1.0
    }.get(task_priority.lower(), 0.75)
    
    # Calculate final score (weighted average)
    score = (skill_score * 0.6) + (workload_score * 0.4)
    
    # Apply priority weight
    score = score * priority_weight
    
    logger.info(f"Assignment score: {score:.2f} (skill: {skill_score:.2f}, workload: {workload_score:.2f}, priority: {priority_weight})")
    
    return score
