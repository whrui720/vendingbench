"""Logging utilities for vendingbench."""
import logging
import sys
from typing import Optional


def setup_logger(
    name: str = "vendingbench",
    level: int = logging.INFO,
    log_file: Optional[str] = None
) -> logging.Logger:
    """Set up a logger for vendingbench.
    
    Args:
        name: Name of the logger
        level: Logging level
        log_file: Optional file to log to
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger
