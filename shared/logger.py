import logging
import json_log_formatter

# Configure JSON logging
formatter = json_log_formatter.JSONFormatter()

json_handler = logging.FileHandler(filename='logs/decision_logs.json')
json_handler.setFormatter(formatter)

logger = logging.getLogger('clara_pm_logger')
logger.addHandler(json_handler)
logger.setLevel(logging.INFO)

# Example function to log a decision
def log_decision(message: str, **kwargs):
    logger.info(message, extra={'props': kwargs})
