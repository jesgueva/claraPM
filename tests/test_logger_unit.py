#!/usr/bin/env python3
"""
Unit tests for the logger module
"""

import unittest
import os
import sys
import shutil
import logging

# Add the parent directory to the path so we can import the intake_agent module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from logger import db_logger, conversation_logger, agent_logger, system_logger

class TestLogger(unittest.TestCase):
    """Test cases for the logger module"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a test logs directory
        self.test_logs_dir = "test_logs"
        if os.path.exists(self.test_logs_dir):
            shutil.rmtree(self.test_logs_dir)
        os.makedirs(self.test_logs_dir, exist_ok=True)
        
        # Save original handlers to restore later
        self.original_handlers = {
            'db': db_logger.handlers.copy(),
            'conversation': conversation_logger.handlers.copy(),
            'agent': agent_logger.handlers.copy(),
            'system': system_logger.handlers.copy()
        }
        
        # Clear existing handlers
        db_logger.handlers.clear()
        conversation_logger.handlers.clear()
        agent_logger.handlers.clear()
        system_logger.handlers.clear()
        
        # Add test file handlers
        db_handler = logging.FileHandler(os.path.join(self.test_logs_dir, "database.log"))
        db_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        db_logger.addHandler(db_handler)
        
        conv_handler = logging.FileHandler(os.path.join(self.test_logs_dir, "conversation.log"))
        conv_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        conversation_logger.addHandler(conv_handler)
        
        agent_handler = logging.FileHandler(os.path.join(self.test_logs_dir, "agent.log"))
        agent_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        agent_logger.addHandler(agent_handler)
        
        system_handler = logging.FileHandler(os.path.join(self.test_logs_dir, "system.log"))
        system_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        system_logger.addHandler(system_handler)
    
    def tearDown(self):
        """Clean up after tests"""
        # Close all handlers
        for logger in [db_logger, conversation_logger, agent_logger, system_logger]:
            for handler in logger.handlers:
                handler.close()
            logger.handlers.clear()
        
        # Restore original handlers
        db_logger.handlers = self.original_handlers['db']
        conversation_logger.handlers = self.original_handlers['conversation']
        agent_logger.handlers = self.original_handlers['agent']
        system_logger.handlers = self.original_handlers['system']
        
        # Remove test logs directory
        if os.path.exists(self.test_logs_dir):
            shutil.rmtree(self.test_logs_dir)
    
    def test_loggers_exist(self):
        """Test that all loggers exist"""
        self.assertIsNotNone(db_logger)
        self.assertIsNotNone(conversation_logger)
        self.assertIsNotNone(agent_logger)
        self.assertIsNotNone(system_logger)
    
    def test_loggers_write_to_files(self):
        """Test that loggers write to their respective files"""
        test_message = "Test message for logger"
        
        # Write test messages
        db_logger.info(f"DB: {test_message}")
        conversation_logger.info(f"CONV: {test_message}")
        agent_logger.info(f"AGENT: {test_message}")
        system_logger.info(f"SYSTEM: {test_message}")
        
        # Check that files exist and contain the messages
        for log_type, prefix in [
            ('database', 'DB'),
            ('conversation', 'CONV'),
            ('agent', 'AGENT'),
            ('system', 'SYSTEM')
        ]:
            log_file = os.path.join(self.test_logs_dir, f"{log_type}.log")
            self.assertTrue(os.path.exists(log_file), f"Log file {log_file} does not exist")
            
            with open(log_file, 'r') as f:
                content = f.read()
                self.assertIn(f"{prefix}: {test_message}", content, 
                             f"Message not found in {log_type} log")
    
    def test_no_duplicate_logs(self):
        """Test that logs are not duplicated"""
        test_message = "Duplicate test message"
        
        # Write test message
        db_logger.info(test_message)
        
        # Check that message appears exactly once
        log_file = os.path.join(self.test_logs_dir, "database.log")
        with open(log_file, 'r') as f:
            content = f.read()
            # Count occurrences of the test message
            count = content.count(test_message)
            self.assertEqual(count, 1, f"Expected 1 occurrence, found {count}")
    
    def test_different_log_levels(self):
        """Test different log levels"""
        # Write messages at different levels
        db_logger.debug("Debug message")
        db_logger.info("Info message")
        db_logger.warning("Warning message")
        db_logger.error("Error message")
        
        # Check that appropriate messages appear in log
        log_file = os.path.join(self.test_logs_dir, "database.log")
        with open(log_file, 'r') as f:
            content = f.read()
            # Debug should not appear by default (INFO level)
            self.assertNotIn("DEBUG - Debug message", content)
            # These should appear
            self.assertIn("INFO - Info message", content)
            self.assertIn("WARNING - Warning message", content)
            self.assertIn("ERROR - Error message", content)

if __name__ == "__main__":
    unittest.main() 