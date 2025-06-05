#!/usr/bin/env python3
"""
Run script for Clara Assignment Agent API
"""

import uvicorn
from assignment_agent.main import app
from shared.logger import system_logger

if __name__ == "__main__":
    system_logger.info("Starting Clara Assignment Agent from run script")
    uvicorn.run(app, host="0.0.0.0", port=8001) 