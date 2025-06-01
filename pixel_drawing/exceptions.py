"""Custom exception hierarchy for pixel drawing application."""


class PixelDrawingError(Exception):
    """Base exception for pixel drawing errors.
    
    All custom exceptions in the pixel drawing application should inherit
    from this base class to provide a consistent exception hierarchy.
    """
    pass


class FileOperationError(PixelDrawingError):
    """File I/O related errors.
    
    Raised when file operations such as loading, saving, or exporting
    encounter issues like missing files, permission errors, or invalid
    file formats.
    """
    pass


class ValidationError(PixelDrawingError):
    """Input validation errors.
    
    Raised when user input or internal data validation fails, such as
    invalid canvas dimensions, color values, or coordinate ranges.
    """
    pass