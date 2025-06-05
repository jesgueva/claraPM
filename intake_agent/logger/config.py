import logging
import os
from logging.handlers import RotatingFileHandler

# Ensure logs directory exists
logs_dir = 'logs'
os.makedirs(logs_dir, exist_ok=True)

# Create a common formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def setup_logger(name, log_file, level=logging.INFO, max_size=10*1024*1024, backup_count=5, add_console=True):
    """
    Function to set up a logger with file and console handlers.
    
    Args:
        name: Logger name
        log_file: Path to log file
        level: Logging level
        max_size: Maximum size of log file before rotation (default: 10MB)
        backup_count: Number of backup files to keep (default: 5)
        add_console: Whether to add a console handler
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Explicitly set propagate to False to prevent duplicate logging
    logger.propagate = False
    
    # Remove existing handlers if any to prevent duplicates
    while logger.handlers:
        logger.handlers.pop()
    
    # Create rotating file handler with proper formatting
    file_handler = RotatingFileHandler(
        os.path.join(logs_dir, log_file),
        maxBytes=max_size,
        backupCount=backup_count
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Create console handler for development convenience
    if add_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger

# First, completely reset the logging system
logging.shutdown()
logging._handlerList.clear()  # Reset handler list

# Reset root logger first
root_logger = logging.getLogger()
root_logger.handlers = []
root_logger.setLevel(logging.INFO)
root_logger.propagate = False

# Set up general log file for the root logger
general_handler = RotatingFileHandler(
    os.path.join(logs_dir, 'general.log'),
    maxBytes=10*1024*1024,
    backupCount=5
)
general_handler.setFormatter(formatter)
root_logger.addHandler(general_handler)

# Add console handler to root logger
root_console = logging.StreamHandler()
root_console.setFormatter(formatter)
root_logger.addHandler(root_console)

# Create specialized loggers with their own files
db_logger = setup_logger('database', 'database.log', add_console=False)
conversation_logger = setup_logger('conversation', 'conversation.log', add_console=False)
agent_logger = setup_logger('agent', 'agent.log', add_console=False)
system_logger = setup_logger('system', 'system.log', add_console=False)

# Configure other common library loggers to avoid noise
for logger_name in ['urllib3', 'requests', 'fastapi', 'uvicorn']:
    lib_logger = logging.getLogger(logger_name)
    lib_logger.setLevel(logging.WARNING)
    lib_logger.propagate = False

# Log the logger initialization
system_logger.info("Logging system initialized with centralized file and console output") 