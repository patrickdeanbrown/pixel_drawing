"""Pixel Drawing - A modern pixel art application for creating retro game assets.

Cross-platform GUI application built with PyQt6 following MVC architecture.
"""

from .constants import AppConstants
from .exceptions import PixelDrawingError, FileOperationError, ValidationError
from .models import PixelArtModel
from .controllers import DrawingTool, BrushTool, FillTool, ToolManager
from .services import FileService
from .views import PixelCanvas, PixelDrawingApp, ColorButton

__version__ = "1.0.0"
__author__ = "Pixel Drawing Team"

__all__ = [
    # Core classes
    'PixelDrawingApp',
    'PixelArtModel',
    'PixelCanvas',
    
    # Tools and controllers
    'DrawingTool',
    'BrushTool', 
    'FillTool',
    'ToolManager',
    
    # Services
    'FileService',
    
    # UI Components
    'ColorButton',
    
    # Configuration and exceptions
    'AppConstants',
    'PixelDrawingError',
    'FileOperationError', 
    'ValidationError',
]