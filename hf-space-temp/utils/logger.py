"""
logger.py - Centralized Logging Configuration

Configures structured console logging formats and logging levels for
all system nodes, modules, and API handlers.
"""

import logging
import sys


def setup_logger(name: str = "rootmind") -> logging.Logger:
    """
    Initializes and configures a standard logger handler.
    
    Args:
        name (str): The namespace key of the target logger module.

    Returns:
        logging.Logger: Configured logger object.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
