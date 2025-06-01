"""Brush tool for painting individual pixels."""

from PyQt6.QtGui import QColor

from .base import DrawingTool
from ...models import PixelArtModel
from ...exceptions import ValidationError


class BrushTool(DrawingTool):
    """Brush tool for painting individual pixels.
    
    Provides continuous painting functionality, allowing users to draw
    by clicking and dragging. Maintains drawing state to ensure smooth
    continuous strokes.
    """
    
    def __init__(self, model: PixelArtModel):
        """Initialize brush tool.
        
        Args:
            model: PixelArtModel to paint on
        """
        super().__init__("Brush", model)
        self._is_drawing = False
    
    def on_press(self, x: int, y: int, color: QColor) -> bool:
        """Start brush stroke at specified coordinates.
        
        Args:
            x: X coordinate to start painting
            y: Y coordinate to start painting
            color: Color to paint with
            
        Returns:
            bool: True to continue receiving move events, False otherwise
        """
        try:
            self._model.set_pixel(x, y, color)
            self._is_drawing = True
            return True  # Continue receiving move events
        except ValidationError:
            return False
    
    def on_move(self, x: int, y: int, color: QColor) -> None:
        """Continue brush stroke to new coordinates.
        
        Args:
            x: X coordinate to paint
            y: Y coordinate to paint
            color: Color to paint with
        """
        if self._is_drawing:
            try:
                self._model.set_pixel(x, y, color)
            except ValidationError:
                pass  # Ignore out-of-bounds moves
    
    def on_release(self, x: int, y: int, color: QColor) -> None:
        """End brush stroke.
        
        Args:
            x: Final X coordinate
            y: Final Y coordinate
            color: Final color
        """
        self._is_drawing = False