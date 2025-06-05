#!/usr/bin/env python3
"""
Main entry point for Clara Project Manager API
"""

from intake_agent.server import app

if __name__ == "__main__":
    import uvicorn
    from logger import system_logger
    
    system_logger.info("Starting Clara PM API server from main.py")
    uvicorn.run(app, host="0.0.0.0", port=8000) 