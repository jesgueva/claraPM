import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import argparse
from datetime import datetime

from shared.models import SessionLocal, create_task, create_user, Task, User, Assignment


def clear_data(db):
    # Clear existing test data
    db.query(Assignment).delete()
    db.query(Task).delete()
    db.query(User).delete()
    db.commit()


def setup_test_data():
    db = SessionLocal()
    clear_data(db)

    # Create admin user
    admin = create_user(db, "admin", "admin@clarapm.com", "admin", "Admin User", role="admin")

    # Create test developers
    developers_raw = [
        {"username": "alice", "email": "alice@example.com", "full_name": "Alice Johnson", "password": "password", "role": "developer"},
        {"username": "bob", "email": "bob@example.com", "full_name": "Bob Smith", "password": "password", "role": "developer"},
        {"username": "charlie", "email": "charlie@example.com", "full_name": "Charlie Davis", "password": "password", "role": "developer"},
        {"username": "diana", "email": "diana@example.com", "full_name": "Diana Kim", "password": "password", "role": "developer"},
        {"username": "ethan", "email": "ethan@example.com", "full_name": "Ethan Rivera", "password": "password", "role": "developer"}
    ]

    developers = []
    for dev in developers_raw:
        user = create_user(db, dev["username"], dev["email"], dev["password"], dev["full_name"], dev["role"])
        developers.append(user)

    # Create test tasks (using admin as creator)
    tasks_data = [
        {
            "title": "Implement user authentication",
            "description": "Create user login and registration functionality with JWT tokens",
            "project_id": 1,
            "priority": "high",
            "role_required": "backend",
            "deadline": "2023-12-15",
            "created_by": "admin"
        },
        {
            "title": "Design product dashboard UI",
            "description": "Create mockups for the main product dashboard with data visualization",
            "project_id": 1,
            "priority": "medium",
            "role_required": "frontend",
            "deadline": "2023-12-10",
            "created_by": "admin"
        },
        {
            "title": "Optimize database queries",
            "description": "Improve performance of slow database queries on the user activity page",
            "project_id": 2,
            "priority": "high",
            "role_required": "backend",
            "deadline": "2023-12-05",
            "created_by": "admin"
        },
        {
            "title": "Write integration tests",
            "description": "Create integration tests for the payment processing module",
            "project_id": 2,
            "priority": "low",
            "role_required": "testing",
            "deadline": "2023-12-20",
            "created_by": "admin"
        },
        {
            "title": "Fix mobile responsiveness issues",
            "description": "Address UI breakage on small screens in the checkout process",
            "project_id": 1,
            "priority": "medium",
            "role_required": "frontend",
            "deadline": "2023-12-12",
            "created_by": "admin"
        }
    ]

    for task in tasks_data:
        deadline = datetime.strptime(task["deadline"], "%Y-%m-%d")
        create_task(db, task["title"], task["description"], admin.id, task["project_id"], task["priority"], task["role_required"], deadline, task["created_by"])

    db.commit()
    print(f"Successfully added {len(tasks_data)} tasks and {len(developers)} developers (plus admin) to SQLite DB")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Set up test data for assignment agent using SQLite')
    parser.add_argument('--clear', action='store_true', help='Clear existing data without adding new test data')
    args = parser.parse_args()

    db = SessionLocal()
    if args.clear:
        clear_data(db)
        print("Cleared all test data from SQLite DB")
    else:
        setup_test_data() 