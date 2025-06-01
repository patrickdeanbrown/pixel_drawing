"""Input validation functions for the pixel drawing application."""

import os
from .constants import AppConstants
from .exceptions import ValidationError, FileOperationError
from .i18n import tr_error


def validate_canvas_dimensions(width: int, height: int) -> None:
    """Validate canvas dimensions are within acceptable limits.
    
    Args:
        width: Canvas width in pixels
        height: Canvas height in pixels
        
    Raises:
        ValidationError: If dimensions are invalid
    """
    if not isinstance(width, int) or not isinstance(height, int):
        raise ValidationError(tr_error("dimensions_must_be_integers"))
    
    if width < AppConstants.MIN_CANVAS_SIZE or height < AppConstants.MIN_CANVAS_SIZE:
        raise ValidationError(tr_error("dimensions_too_small", min_size=AppConstants.MIN_CANVAS_SIZE))
    
    if width > AppConstants.MAX_CANVAS_SIZE or height > AppConstants.MAX_CANVAS_SIZE:
        raise ValidationError(tr_error("dimensions_too_large", max_size=AppConstants.MAX_CANVAS_SIZE))


def validate_file_path(file_path: str, operation: str = "access") -> None:
    """Validate file path for operations.
    
    Args:
        file_path: Path to validate
        operation: Type of operation ('read', 'write', 'access')
        
    Raises:
        FileOperationError: If file path is invalid for operation
    """
    if not file_path or not isinstance(file_path, str):
        raise FileOperationError(tr_error("file_path_empty"))
    
    if operation == "read":
        if not os.path.exists(file_path):
            raise FileOperationError(tr_error("file_not_exists", path=file_path))
        if not os.path.isfile(file_path):
            raise FileOperationError(tr_error("path_not_file", path=file_path))
        if not os.access(file_path, os.R_OK):
            raise FileOperationError(tr_error("file_not_readable", path=file_path))
    
    elif operation == "write":
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            raise FileOperationError(tr_error("directory_not_exists", path=directory))
        if os.path.exists(file_path) and not os.access(file_path, os.W_OK):
            raise FileOperationError(tr_error("file_not_writable", path=file_path))
        if directory and not os.access(directory, os.W_OK):
            raise FileOperationError(tr_error("directory_not_writable", path=directory))