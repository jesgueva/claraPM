"""
Test script to verify database access and task retrieval.
"""
from clara_pm.shared.models import SessionLocal, get_tasks

def test_retrieve_tasks():
    """Test retrieving tasks from the database."""
    db = SessionLocal()
    try:
        tasks = get_tasks(db)
        print(f"Found {len(tasks)} tasks in the database:")
        for task in tasks:
            print(f"Task #{task.id}: {task.title}")
            print(f"  Description: {task.description}")
            print(f"  Project ID: {task.project_id}")
            print(f"  Priority: {task.priority}")
            print(f"  Role: {task.role_required}")
            print(f"  Deadline: {task.deadline}")
            print(f"  Created by: {task.created_by}")
            print(f"  User ID: {task.user_id}")
            print("-" * 40)
    except Exception as e:
        print(f"Error retrieving tasks: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_retrieve_tasks() 