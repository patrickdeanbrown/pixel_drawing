"""Abstract base class for drawing tools."""

from abc import ABC, abstractmethod
from PyQt6.QtGui import QColor

from ...models import PixelArtModel


class DrawingTool(ABC):
    """Abstract base class for drawing tools.
    
    Defines the interface that all drawing tools must implement,
    providing a consistent API for tool interactions and enabling
    the Command pattern for potential undo/redo functionality.
    """
    
    def __init__(self, name: str, model: PixelArtModel):
        """Initialize drawing tool.
        
        Args:
            name: Tool name for display purposes
            model: PixelArtModel to operate on
        """
        self._name = name
        self._model = model
    
    @property
    def name(self) -> str:
        """Get tool display name.
        
        Returns:
            str: Human-readable tool name
        """
        return self._name
    
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