"""
Safe logging utility with automatic secret masking
"""

from utils.secret_masker import mask_secrets, safe_log, safe_print


def log_info(message: str):
    """Log info message with secret masking"""
    safe_log(message, "INFO")


def log_warning(message: str):
    """Log warning message with secret masking"""
    safe_log(message, "WARNING")


def log_error(message: str):
    """Log error message with secret masking"""
    safe_log(message, "ERROR")


def log_debug(message: str):
    """Log debug message with secret masking"""
    safe_log(message, "DEBUG")


# Export safe_print for use throughout the codebase
__all__ = ['log_info', 'log_warning', 'log_error', 'log_debug', 'safe_print', 'mask_secrets']
