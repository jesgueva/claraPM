#!/usr/bin/env python3
"""
Run script for Clara Project Manager API
"""

from intake_agent.server import run_server
from intake_agent.logger import system_logger

if __name__ == "__main__":
    system_logger.info("Starting Clara PM from run script")
    run_server(host="0.0.0.0", port=8000) 