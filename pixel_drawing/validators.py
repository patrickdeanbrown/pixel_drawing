"""Input validation functions for the pixel drawing application."""

import os
from .constants import AppConstants
from .exceptions import ValidationError, FileOperationError


def validate_canvas_dimensions(width: int, height: int) -> None:
    """Validate canvas dimensions are within acceptable limits.
    
    Args:
        width: Canvas width in pixels
        height: Canvas height in pixels
        
    Raises:
        ValidationError: If dimensions are invalid
    """
    if not isinstance(width, int) or not isinstance(height, int):
        raise ValidationError("Canvas dimensions must be integers")
    
    if width < AppConstants.MIN_CANVAS_SIZE or height < AppConstants.MIN_CANVAS_SIZE:
        raise ValidationError(f"Canvas dimensions must be at least {AppConstants.MIN_CANVAS_SIZE}x{AppConstants.MIN_CANVAS_SIZE}")
    
    if width > AppConstants.MAX_CANVAS_SIZE or height > AppConstants.MAX_CANVAS_SIZE:
        raise ValidationError(f"Canvas dimensions cannot exceed {AppConstants.MAX_CANVAS_SIZE}x{AppConstants.MAX_CANVAS_SIZE}")


def validate_file_path(file_path: str, operation: str = "access") -> None:
    """Validate file path for operations.
    
    Args:
        file_path: Path to validate
        operation: Type of operation ('read', 'write', 'access')
        
    Raises:
        FileOperationError: If file path is invalid for operation
    """
    if not file_path or not isinstance(file_path, str):
        raise FileOperationError("File path cannot be empty")
    
    if operation == "read":
        if not os.path.exists(file_path):
            raise FileOperationError(f"File does not exist: {file_path}")
        if not os.path.isfile(file_path):
            raise FileOperationError(f"Path is not a file: {file_path}")
        if not os.access(file_path, os.R_OK):
            raise FileOperationError(f"File is not readable: {file_path}")
    
    elif operation == "write":
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            raise FileOperationError(f"Directory does not exist: {directory}")
        if os.path.exists(file_path) and not os.access(file_path, os.W_OK):
            raise FileOperationError(f"File is not writable: {file_path}")
        if directory and not os.access(directory, os.W_OK):
            raise FileOperationError(f"Directory is not writable: {directory}")