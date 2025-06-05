"""
Logging utilities for the Clara PM system.
"""

import logging
import json
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("clara_pm")

system_logger = logging.getLogger("system_logger")
system_logger.setLevel(logging.INFO)
if not system_logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    system_logger.addHandler(handler)

# Directory for storing decision logs
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
DECISION_LOG_PATH = os.path.join(LOG_DIR, "assignment_decisions.log")

# Create logs directory if it doesn't exist
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def log_decision(decision: str, **kwargs):
    """
    Log a task assignment decision with additional metadata.
    
    Args:
        decision: The decision message
        **kwargs: Additional metadata to log (task_id, developer_id, etc.)
    """
    try:
        # Create log entry with timestamp
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "decision": decision,
            **kwargs
        }
        
        # Log to console
        logger.info(f"Decision: {decision} - {json.dumps(kwargs)}")
        
        # Write to decision log file
        with open(DECISION_LOG_PATH, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        logger.error(f"Error logging decision: {e}")

def get_recent_decisions(limit: int = 10):
    """
    Get the most recent task assignment decisions.
    
    Args:
        limit: Maximum number of decisions to return
        
    Returns:
        List of decision log entries
    """
    try:
        if not os.path.exists(DECISION_LOG_PATH):
            return []
            
        with open(DECISION_LOG_PATH, "r") as f:
            # Read all lines and parse JSON
            decisions = [json.loads(line) for line in f]
            
        # Return the most recent decisions (up to limit)
        return decisions[-limit:]
    except Exception as e:
        logger.error(f"Error getting recent decisions: {e}")
        return []

def clear_decision_logs():
    """
    Clear all decision logs.
    """
    try:
        if os.path.exists(DECISION_LOG_PATH):
            os.remove(DECISION_LOG_PATH)
            logger.info("Decision logs cleared")
    except Exception as e:
        logger.error(f"Error clearing decision logs: {e}")
