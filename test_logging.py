#!/usr/bin/env python3
"""
Test script to verify that all loggers are correctly writing to their respective log files.
"""

from intake_agent.logger import db_logger, conversation_logger, agent_logger, system_logger
import logging
import os
import time
import re

def test_all_loggers():
    """Test all loggers to ensure they're writing to files without duplication."""
    # Generate a unique timestamp for this test run
    timestamp = int(time.time())
    
    print(f"\n=== Testing loggers with timestamp: {timestamp} ===\n")
    
    # Test specific loggers with distinct messages
    system_logger.info(f"SYSTEM-{timestamp}: System logger test message")
    db_logger.info(f"DB-{timestamp}: Database logger test message")
    conversation_logger.info(f"CONV-{timestamp}: Conversation logger test message")
    agent_logger.info(f"AGENT-{timestamp}: Agent logger test message")
    
    # Test the root logger (should go to general.log only)
    root_logger = logging.getLogger()
    root_logger.info(f"ROOT-{timestamp}: Root logger test message")
    
    # Test a random module logger (should go to general.log only)
    random_logger = logging.getLogger("random_module")
    random_logger.info(f"RANDOM-{timestamp}: Random module logger test message")
    
    print("Logging test complete. Check the logs directory for the following files:")
    print("- logs/system.log")
    print("- logs/database.log")
    print("- logs/conversation.log")
    print("- logs/agent.log")
    print("- logs/general.log")
    
    # Check for duplicates
    check_for_duplicates(timestamp)

def check_for_duplicates(timestamp):
    """Check log files for duplicate entries with the given timestamp."""
    log_files = {
        'system.log': [],
        'database.log': [],
        'conversation.log': [],
        'agent.log': [],
        'general.log': []
    }
    
    # Read all log files and collect entries with our timestamp
    for log_file in log_files:
        file_path = os.path.join('logs', log_file)
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                for line in f:
                    if str(timestamp) in line:
                        log_files[log_file].append(line.strip())
    
    print("\n=== Detailed Log Analysis ===")
    
    for log_file, entries in log_files.items():
        print(f"\n{log_file} ({len(entries)} entries with timestamp {timestamp}):")
        for entry in entries:
            print(f"  - {entry}")
    
    print("\n=== Duplicate Check Summary ===")
    
    # Check for duplicates in each file
    has_duplicates = False
    for log_file, entries in log_files.items():
        unique_prefixes = set()
        duplicates = []
        
        for entry in entries:
            # Extract the prefix (SYSTEM-, DB-, etc.)
            match = re.search(r'(SYSTEM|DB|CONV|AGENT|ROOT|RANDOM)-\d+', entry)
            if match:
                prefix = match.group(0)
                if prefix in unique_prefixes:
                    duplicates.append(prefix)
                else:
                    unique_prefixes.add(prefix)
        
        if duplicates:
            print(f"- {log_file}: DUPLICATE DETECTED - {duplicates}")
            has_duplicates = True
        else:
            print(f"- {log_file}: OK ({len(entries)} unique entries)")
    
    if has_duplicates:
        print("\n⚠️ Duplicate log entries detected. Check the logger configuration.")
    else:
        print("\n✓ No duplicate log entries detected. Logging system is working correctly.")

if __name__ == "__main__":
    test_all_loggers() 