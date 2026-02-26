"""
Helper utilities for the application.
"""
import logging
import uuid
from typing import Any, Dict

# Create logger
logger = logging.getLogger(__name__)


def generate_unique_id() -> str:
    """
    Generate a unique ID.
    
    Returns:
        Unique string ID
    """
    return str(uuid.uuid4())


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to remove unsafe characters.
    
    Args:
        filename: Original filename
    
    Returns:
        Sanitized filename
    """
    import re
    # Remove unsafe characters
    filename = re.sub(r'[^\w\s\-\.]', '', filename)
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    return filename


def create_response(success: bool, message: str = '', data: Any = None, status_code: int = 200) -> Dict[str, Any]:
    """
    Create a standardized API response.
    
    Args:
        success: Whether the operation was successful
        message: Response message
        data: Response data
        status_code: HTTP status code
    
    Returns:
        Response dictionary
    """
    response = {
        'success': success,
        'message': message
    }
    
    if data is not None:
        response['data'] = data
    
    return response, status_code


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
    
    Returns:
        Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def parse_bool(value: Any) -> bool:
    """
    Parse a boolean value from various formats.
    
    Args:
        value: Value to parse
    
    Returns:
        Boolean value
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes', 'on')
    return bool(value)
