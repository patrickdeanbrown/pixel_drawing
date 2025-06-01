"""Fill bucket tool for flood fill operations."""

from PyQt6.QtGui import QColor

from .base import DrawingTool
from ...models import PixelArtModel
from ...exceptions import ValidationError
from ...constants import AppConstants
from ...i18n import tr_tool


class FillTool(DrawingTool):
    """Fill bucket tool for flood fill operations.
    
    Implements flood fill algorithm to fill connected areas of the same
    color with a new color. Operates on single click without requiring
    mouse move or release events.
    """
    
    def __init__(self, model: PixelArtModel):
        """Initialize fill tool.
        
        Args:
            model: PixelArtModel to perform flood fill on
        """
        super().__init__(tr_tool("fill"), model, shortcut="F")
        self.set_icon_path(AppConstants.ICON_FILL)
    
    def on_press(self, x: int, y: int, color: QColor) -> bool:
        """Perform flood fill operation at specified coordinates.
        
        Args:
            x: X coordinate to start flood fill
            y: Y coordinate to start flood fill
            color: Color to fill with
            
        Returns:
            bool: False since fill operations don't need move events
        """
        try:
            changed_pixels = self._model.flood_fill(x, y, color)
            return False  # No move events needed for fill
        except ValidationError:
            return False
    
    def on_move(self, x: int, y: int, color: QColor) -> None:
        """Fill tool doesn't use move events.
        
        Args:
            x: X coordinate (ignored)
            y: Y coordinate (ignored)
            color: Color (ignored)
        """
        pass
    
    def on_release(self, x: int, y: int, color: QColor) -> None:
        """Fill tool doesn't use release events.
        
        Args:
            x: X coordinate (ignored)
            y: Y coordinate (ignored)
            color: Color (ignored)
        """
        pass