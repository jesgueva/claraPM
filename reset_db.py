#!/usr/bin/env python3
"""
Reset the database and initialize it with default data.
"""

import os
import sys
import sqlite3
from datetime import datetime

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from clara_pm.shared.models import (
    Base, engine, SessionLocal, 
    User, Task, Assignment, TaskSpec, ConversationSession, Message,
    create_user
)

def reset_database():
    """Reset the database and initialize it with default data."""
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    
    # Create a session
    db = SessionLocal()
    
    # Create default users
    print("Creating default users...")
    admin = create_user(db, "admin", "admin@clarapm.com", "admin", "Admin User", "admin")
    user = create_user(db, "user", "user@clarapm.com", "user", "Test User", "user")
    
    # Create some sample tasks
    print("Creating sample tasks...")
    task1 = Task(
        title="Implement user authentication",
        description="Add user login, registration, and JWT authentication to the app",
        project_id=1,
        priority="High",
        role_required="Developer",
        deadline=datetime(2023, 12, 31),
        created_by="admin",
        user_id=admin.id
    )
    
    task2 = Task(
        title="Design login UI",
        description="Create a user-friendly login interface with validation",
        project_id=1,
        priority="Medium",
        role_required="Designer",
        deadline=datetime(2023, 12, 15),
        created_by="admin",
        user_id=user.id
    )
    
    db.add(task1)
    db.add(task2)
    
    # Create sample conversation sessions
    print("Creating sample conversation sessions...")
    session1 = ConversationSession(
        session_id="admin-session-1",
        user_id=admin.id,
        title="Project Planning"
    )
    
    session2 = ConversationSession(
        session_id="user-session-1",
        user_id=user.id,
        title="Task Management"
    )
    
    db.add(session1)
    db.add(session2)
    
    # Add some messages to the sessions
    message1 = Message(
        session_id="admin-session-1",
        type="user",
        content="I need to plan a new project"
    )
    
    message2 = Message(
        session_id="admin-session-1",
        type="ai",
        content="I'd be happy to help you plan a new project. What's the project about?"
    )
    
    message3 = Message(
        session_id="user-session-1",
        type="user",
        content="What tasks are assigned to me?"
    )
    
    message4 = Message(
        session_id="user-session-1",
        type="ai",
        content="You have one task assigned: 'Design login UI' with a deadline of December 15, 2023."
    )
    
    db.add(message1)
    db.add(message2)
    db.add(message3)
    db.add(message4)
    
    # Commit the changes
    db.commit()
    
    print("Database has been reset and initialized with default data.")

if __name__ == "__main__":
    reset_database() 