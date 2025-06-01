"""Eraser tool for removing pixels."""

from PyQt6.QtGui import QColor

from .base import DrawingTool
from ...models import PixelArtModel
from ...exceptions import ValidationError
from ...constants import AppConstants
from ...constants import AppConstants


class EraserTool(DrawingTool):
    """Eraser tool for removing pixels by setting them to background color.
    
    Provides continuous erasing functionality, allowing users to erase
    by clicking and dragging. Similar to brush tool but always uses
    the default background color.
    """
    
    def __init__(self, model: PixelArtModel):
        """Initialize eraser tool.
        
        Args:
            model: PixelArtModel to erase on
        """
        super().__init__("Eraser", model, shortcut="E")
        self.set_icon_path(AppConstants.ICON_ERASER)
        self._is_erasing = False
        # Eraser uses background color for "erasing"
        self._background_color = QColor(AppConstants.DEFAULT_BG_COLOR)
    
    def on_press(self, x: int, y: int, color: QColor) -> bool:
        """Start erasing at specified coordinates.
        
        Args:
            x: X coordinate to start erasing
            y: Y coordinate to start erasing  
            color: Color parameter (ignored, always uses background)
            
        Returns:
            bool: True to continue receiving move events, False otherwise
        """
        try:
            self._model.set_pixel(x, y, self._background_color)
            self._is_erasing = True
            return True  # Continue receiving move events
        except ValidationError:
            return False
    
    def on_move(self, x: int, y: int, color: QColor) -> None:
        """Continue erasing to new coordinates.
        
        Args:
            x: X coordinate to erase
            y: Y coordinate to erase
            color: Color parameter (ignored, always uses background)
        """
        if self._is_erasing:
            try:
                self._model.set_pixel(x, y, self._background_color)
            except ValidationError:
                pass  # Ignore out-of-bounds moves
    
    def on_release(self, x: int, y: int, color: QColor) -> None:
        """End erasing stroke.
        
        Args:
            x: Final X coordinate
            y: Final Y coordinate
            color: Color parameter (ignored)
        """
        self._is_erasing = False