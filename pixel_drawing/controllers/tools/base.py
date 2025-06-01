"""Abstract base class for drawing tools."""

from abc import ABC, abstractmethod
from typing import Optional
from PyQt6.QtGui import QColor, QCursor
from PyQt6.QtCore import Qt

from ...models import PixelArtModel


class DrawingTool(ABC):
    """Abstract base class for drawing tools.
    
    Defines the interface that all drawing tools must implement,
    providing a consistent API for tool interactions and enabling
    the Command pattern for potential undo/redo functionality.
    
    Enhanced to support cursor management and tool metadata for
    professional tool switching and visual feedback.
    """
    
    def __init__(self, name: str, model: PixelArtModel, cursor: Optional[QCursor] = None, shortcut: str = ""):
        """Initialize drawing tool.
        
        Args:
            name: Tool name for display purposes
            model: PixelArtModel to operate on
            cursor: Custom cursor for this tool (None for default)
            shortcut: Keyboard shortcut key (e.g., "B" for brush)
        """
        self._name = name
        self._model = model
        self._cursor = cursor or QCursor(Qt.CursorShape.CrossCursor)
        self._shortcut = shortcut
        self._icon_path: Optional[str] = None
    
    @property
    def name(self) -> str:
        """Get tool display name.
        
        Returns:
            str: Human-readable tool name
        """
        return self._name
    
    @property
    def cursor(self) -> QCursor:
        """Get tool-specific cursor.
        
        Returns:
            QCursor: Cursor to display when this tool is active
        """
        return self._cursor
    
    @property
    def shortcut(self) -> str:
        """Get keyboard shortcut for this tool.
        
        Returns:
            str: Single character shortcut key
        """
        return self._shortcut
    
    @property 
    def icon_path(self) -> Optional[str]:
        """Get icon file path for this tool.
        
        Returns:
            Optional[str]: Path to tool icon file
        """
        return self._icon_path
    
    def set_icon_path(self, icon_path: str) -> None:
        """Set icon file path for this tool.
        
        Args:
            icon_path: Path to SVG or image file for tool icon
        """
        self._icon_path = icon_path
    
    @abstractmethod
    def on_press(self, x: int, y: int, color: QColor) -> bool:
        """Handle mouse press event.
        
        Args:
            x: X coordinate in canvas pixels
            y: Y coordinate in canvas pixels
            color: Current drawing color
            
        Returns:
            bool: True if tool should continue receiving move events
        """
        pass
    
    @abstractmethod
    def on_move(self, x: int, y: int, color: QColor) -> None:
        """Handle mouse move event.
        
        Args:
            x: X coordinate in canvas pixels
            y: Y coordinate in canvas pixels
            color: Current drawing color
        """
        pass
    
    @abstractmethod
    def on_release(self, x: int, y: int, color: QColor) -> None:
        """Handle mouse release event.
        
        Args:
            x: X coordinate in canvas pixels
            y: Y coordinate in canvas pixels
            color: Current drawing color
        """
        pass