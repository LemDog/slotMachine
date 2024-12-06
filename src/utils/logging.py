"""
📝 Logging configuration and utilities
"""

import logging
import os
import sys
from collections import deque
from datetime import datetime
from typing import Deque, List

def setup_logging(debug: bool = False) -> None:
    """
    🔧 Configure logging for the game
    
    Args:
        debug: Whether to enable debug logging
    """
    level = logging.DEBUG if debug else logging.INFO
    
    # Remove any existing handlers
    root = logging.getLogger()
    for handler in root.handlers[:]:
        root.removeHandler(handler)
    
    # Configure root logger
    root.setLevel(level)
    
    # Ensure logs directory exists
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # Configure file handler with formatter
    log_file = os.path.join(logs_dir, 'slot_machine.log')
    file_handler = logging.FileHandler(log_file)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    # Add only the file handler
    root.addHandler(file_handler)