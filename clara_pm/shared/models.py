from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from datetime import datetime

# Define the SQLite database
DATABASE_URL = "sqlite:///clara_pm.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define the Task model
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, index=True)
    title = Column(String, index=True)
    description = Column(String)
    priority = Column(String)
    role_required = Column(String)
    deadline = Column(DateTime)
    created_by = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="tasks")

# Define the User model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    tasks = relationship("Task", back_populates="user")

# Define the Assignment model
class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    task = relationship("Task")
    user = relationship("User")

# Define the TaskSpec model
class TaskSpec(Base):
    __tablename__ = "task_specs"

    id = Column(Integer, primary_key=True, index=True)
    prompt = Column(String, nullable=False)
    spec = Column(String, nullable=False)

# Create the database tables
Base.metadata.create_all(bind=engine)

# Create a new task with additional fields
def create_task(db: Session, title: str, description: str, user_id: int, project_id: int, priority: str, role_required: str, deadline: datetime, created_by: str):
    new_task = Task(title=title, description=description, user_id=user_id, project_id=project_id, priority=priority, role_required=role_required, deadline=deadline, created_by=created_by)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

# Get a task by ID
def get_task(db: Session, task_id: int):
    return db.query(Task).filter(Task.id == task_id).first()

# Get all tasks
def get_tasks(db: Session):
    return db.query(Task).all()

# Update a task
def update_task(db: Session, task_id: int, title: str = None, description: str = None):
    task = get_task(db, task_id)
    if task:
        if title:
            task.title = title
        if description:
            task.description = description
        db.commit()
        db.refresh(task)
    return task

# Delete a task
def delete_task(db: Session, task_id: int):
    task = get_task(db, task_id)
    if task:
        db.delete(task)
        db.commit()
    return task

# Create a new user
def create_user(db: Session, name: str):
    new_user = User(name=name)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# Get a user by ID
def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

# Get all users
def get_users(db: Session):
    return db.query(User).all()

# Update a user
def update_user(db: Session, user_id: int, name: str = None):
    user = get_user(db, user_id)
    if user and name:
        user.name = name
        db.commit()
        db.refresh(user)
    return user

# Delete a user
def delete_user(db: Session, user_id: int):
    user = get_user(db, user_id)
    if user:
        db.delete(user)
        db.commit()
    return user
