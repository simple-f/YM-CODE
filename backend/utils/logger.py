"""
Backend Utils Logger

Simple logger utility
"""

import logging

def get_logger(name: str) -> logging.Logger:
    """Get logger instance"""
    return logging.getLogger(name)
