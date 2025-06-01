"""Color picker tool for sampling colors from the canvas."""

from PyQt6.QtGui import QColor
from PyQt6.QtCore import pyqtSignal, QObject

from .base import DrawingTool
from ...models import PixelArtModel
from ...exceptions import ValidationError


class ColorPickerToolSignals(QObject):
    """Signal container for ColorPickerTool."""
    color_picked = pyqtSignal(QColor)


class ColorPickerTool(DrawingTool):
    """Color picker tool for sampling colors from the canvas.
    
    Allows users to click on any pixel to sample its color and set it
    as the current drawing color. Emits a signal when a color is picked
    to notify the UI to update the current color.
    """
    
    
    def __init__(self, model: PixelArtModel):
        """Initialize color picker tool.
        
        Args:
            model: PixelArtModel to sample colors from
        """
        super().__init__("Color Picker", model, shortcut="I")
        self.signals = ColorPickerToolSignals()
        # Note: We'll need to connect the signal in the tool manager or main window
        
    def on_press(self, x: int, y: int, color: QColor) -> bool:
        """Sample color at specified coordinates.
        
        Args:
            x: X coordinate to sample color from
            y: Y coordinate to sample color from
            color: Current color parameter (ignored)
            
        Returns:
            bool: False since color picker doesn't need move events
        """
        try:
            sampled_color = self._model.get_pixel(x, y)
            self.signals.color_picked.emit(sampled_color)
            return False  # No move events needed for color picking
        except ValidationError:
            return False
    
    def on_move(self, x: int, y: int, color: QColor) -> None:
        """Color picker doesn't use move events.
        
        Args:
            x: X coordinate (ignored)
            y: Y coordinate (ignored)
            color: Color (ignored)
        """
        pass
    
    def on_release(self, x: int, y: int, color: QColor) -> None:
        """Color picker doesn't use release events.
        
        Args:
            x: X coordinate (ignored)
            y: Y coordinate (ignored)
            color: Color (ignored)
        """
        pass