"""Pan tool for moving the canvas viewport."""

from PyQt6.QtGui import QColor, QCursor
from PyQt6.QtCore import Qt, pyqtSignal, QPoint

from .base import DrawingTool
from ...models import PixelArtModel


class PanTool(DrawingTool):
    """Pan tool for moving the canvas viewport.
    
    Allows users to click and drag to move their view of the canvas,
    especially useful for large canvases that don't fit entirely in
    the viewport. Emits signals to coordinate with scrollable containers.
    """
    
    # Signal emitted when panning is requested
    pan_requested = pyqtSignal(int, int)  # delta_x, delta_y
    
    def __init__(self, model: PixelArtModel):
        """Initialize pan tool.
        
        Args:
            model: PixelArtModel (not directly modified by pan tool)
        """
        # Use hand cursor for pan tool
        hand_cursor = QCursor(Qt.CursorShape.OpenHandCursor)
        super().__init__("Pan", model, cursor=hand_cursor, shortcut="H")
        self._is_panning = False
        self._last_pan_point = QPoint()
        
    def on_press(self, x: int, y: int, color: QColor) -> bool:
        """Start panning from specified coordinates.
        
        Args:
            x: X coordinate where panning started
            y: Y coordinate where panning started
            color: Color parameter (ignored for pan tool)
            
        Returns:
            bool: True to continue receiving move events
        """
        self._is_panning = True
        self._last_pan_point = QPoint(x, y)
        return True  # Continue receiving move events
    
    def on_move(self, x: int, y: int, color: QColor) -> None:
        """Continue panning to new coordinates.
        
        Args:
            x: Current X coordinate
            y: Current Y coordinate  
            color: Color parameter (ignored for pan tool)
        """
        if self._is_panning:
            current_point = QPoint(x, y)
            delta = current_point - self._last_pan_point
            
            # Emit pan request with delta movement
            self.pan_requested.emit(delta.x(), delta.y())
            
            # Update last point for next move
            self._last_pan_point = current_point
    
    def on_release(self, x: int, y: int, color: QColor) -> None:
        """End panning operation.
        
        Args:
            x: Final X coordinate
            y: Final Y coordinate
            color: Color parameter (ignored)
        """
        self._is_panning = False