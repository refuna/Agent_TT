#!/usr/bin/env python3
"""
Shared logging setup utilities
"""

import logging
import sys
from typing import Optional

def setup_logging(
    level: str = "INFO",
    format_str: Optional[str] = None,
    server_name: Optional[str] = None
) -> logging.Logger:
    """Setup standardized logging configuration"""

    if format_str is None:
        if server_name:
            format_str = f"%(asctime)s - {server_name} - %(levelname)s - %(message)s"
        else:
            format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_str,
        handlers=[
            logging.StreamHandler(sys.stderr)
        ]
    )

    # Return logger for the calling module
    if server_name:
        return logging.getLogger(server_name)
    else:
        return logging.getLogger(__name__)

def get_logger(name: str) -> logging.Logger:
    """Get a logger with consistent formatting"""
    return logging.getLogger(name)