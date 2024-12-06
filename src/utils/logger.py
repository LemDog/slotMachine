"""
📝 Logging Setup - Keeping track of what's happening behind the scenes!

This module sets up logging for the game, which helps us (and you!) understand
what's happening when things don't go as planned. Think of it as the game's
diary where it writes down everything it does! 📔
"""

import logging
import os
from datetime import datetime

def setup_debug_logging() -> None:
    """
    🔍 Sets up detailed logging for debugging
    
    This function creates a special log file that records everything the game does.
    It's super helpful when we need to figure out why something unexpected happened!
    
    The log file will be created in a 'logs' directory with today's date, like:
    'logs/slot_machine_2024-01-20.log'
    
    Features:
    - 📁 Creates a logs directory if it doesn't exist
    - 📅 Uses the current date in the filename
    - 🎯 Records detailed information about what's happening
    - 🕒 Includes timestamps with each log entry
    """
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Create a fancy log filename with today's date
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = f"logs/slot_machine_{today}.log"
    
    # Create file handler with debug level
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    
    # Create console handler with info level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] 🎲 %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Get root logger and set its level to DEBUG
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # Remove any existing handlers
    logger.handlers = []
    
    # Add our handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Let's write our first log entry!
    logging.info("🎰 Game logging initialized - Let the fun begin! 🎉")
    logging.debug("🔍 Debug logging enabled - Recording detailed game information")