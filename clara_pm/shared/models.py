from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from datetime import datetime
from passlib.context import CryptContext

# Password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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

# Define the User model with authentication fields
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    disabled = Column(Boolean, default=False)
    role = Column(String, default="user")  # admin, user, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

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

# Define the Session model for conversation history
class ConversationSession(Base):
    __tablename__ = "conversation_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, default="New Conversation")
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    user = relationship("User")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")

# Define the Message model for storing conversation messages
class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("conversation_sessions.session_id"))
    type = Column(String)  # "user" or "ai"
    content = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    session = relationship("ConversationSession", back_populates="messages")

# Create the database tables
Base.metadata.create_all(bind=engine)

# Password hashing and verification
def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

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

# Create a new user with authentication
def create_user(db: Session, username: str, email: str, password: str, full_name: str, role: str = "user"):
    hashed_password = get_password_hash(password)
    new_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        full_name=full_name,
        role=role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# Get a user by ID
def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

# Get a user by username
def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

# Get a user by email
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

# Get all users
def get_users(db: Session):
    return db.query(User).all()

# Update a user
def update_user(db: Session, user_id: int, **kwargs):
    user = get_user(db, user_id)
    if user:
        for key, value in kwargs.items():
            if key == 'password':
                setattr(user, 'hashed_password', get_password_hash(value))
            elif hasattr(user, key):
                setattr(user, key, value)
        user.last_login = datetime.utcnow()
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

# Authenticate user
def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    update_user(db, user.id)  # Update last_login
    return user

# Initialize some default users if they don't exist
def init_default_users(db: Session):
    # Check if admin user exists
    admin = get_user_by_username(db, "admin")
    if not admin:
        create_user(db, "admin", "admin@clarapm.com", "admin", "Admin User", "admin")
    
    # Check if test user exists
    user = get_user_by_username(db, "user")
    if not user:
        create_user(db, "user", "user@clarapm.com", "user", "Test User", "user")

# Create a database session
def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

# Do not initialize users here - let the reset_db.py script do it
