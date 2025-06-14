"""Data model for pixel art, managing canvas data and business logic."""

from typing import Tuple, Optional, List, Dict
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QColor

from ..constants import AppConstants
from ..validators import validate_canvas_dimensions
from ..exceptions import ValidationError
from ..commands import CommandHistory, SetPixelCommand
from ..i18n import tr_error


class PixelArtModel(QObject):
    """Data model for pixel art, managing canvas data and business logic.
    
    This class implements the Model component of the MVC architecture, handling
    all pixel data storage, manipulation, and business logic for the pixel art
    application. It provides signals for UI updates and maintains the integrity
    of the canvas data.
    
    Attributes:
        width: Canvas width in pixels (read-only)
        height: Canvas height in pixels (read-only) 
        current_file: Path to currently loaded file (read-only)
        is_modified: Whether the model has unsaved changes (read-only)
        
    Signals:
        pixel_changed(int, int, QColor): Emitted when a pixel color changes
        canvas_resized(int, int): Emitted when canvas dimensions change
        canvas_cleared(): Emitted when canvas is cleared
        model_loaded(): Emitted when a file is loaded into the model
        model_saved(str): Emitted when model is saved to file
    """
    
    # Signals for model changes
    pixel_changed = pyqtSignal(int, int, QColor)  # x, y, new_color
    canvas_resized = pyqtSignal(int, int)  # new_width, new_height
    canvas_cleared = pyqtSignal()
    model_loaded = pyqtSignal()
    model_saved = pyqtSignal(str)  # file_path
    
    def __init__(self, width: int = AppConstants.DEFAULT_CANVAS_WIDTH, 
                 height: int = AppConstants.DEFAULT_CANVAS_HEIGHT):
        """Initialize the pixel art model with specified dimensions.
        
        Creates a new pixel art model with the given canvas dimensions and
        initializes all pixels to the default background color. Sets up
        internal state for tracking modifications and file associations.
        
        Args:
            width: Canvas width in pixels (1-256, default: 32)
            height: Canvas height in pixels (1-256, default: 32)
            
        Raises:
            ValidationError: If width or height are outside valid range
        """
        super().__init__()
        validate_canvas_dimensions(width, height)
        
        self._width = width
        self._height = height
        self._pixels: Dict[Tuple[int, int], QColor] = {}
        self._current_file: Optional[str] = None
        self._is_modified = False
        
        # Command-based undo/redo system
        self._command_history = CommandHistory(AppConstants.MAX_UNDO_HISTORY)
        
        # Initialize with default background color (don't mark as modified)
        self._pixels.clear()  # Start with empty pixels dict
    
    @property
    def width(self) -> int:
        """Get canvas width in pixels.
        
        Returns:
            int: Canvas width (1-256 pixels)
        """
        return self._width
    
    @property
    def height(self) -> int:
        """Get canvas height in pixels.
        
        Returns:
            int: Canvas height (1-256 pixels)
        """
        return self._height
    
    @property
    def current_file(self) -> Optional[str]:
        """Get path to currently loaded file.
        
        Returns:
            Optional[str]: File path if a file is loaded, None otherwise
        """
        return self._current_file
    
    @property
    def is_modified(self) -> bool:
        """Check if model has unsaved changes.
        
        Returns:
            bool: True if there are unsaved changes, False otherwise
        """
        return self._is_modified
    
    def get_pixel(self, x: int, y: int) -> QColor:
        """Get color of pixel at coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            QColor at the specified coordinates
            
        Raises:
            ValidationError: If coordinates are out of bounds
        """
        if not (0 <= x < self._width and 0 <= y < self._height):
            raise ValidationError(tr_error(AppConstants.ERROR_COORDS_OUT_OF_BOUNDS))
        
        return self._pixels.get((x, y), QColor(AppConstants.DEFAULT_BG_COLOR))
    
    def set_pixel(self, x: int, y: int, color: QColor) -> bool:
        """Set color of pixel at coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            color: Color to set
            
        Returns:
            True if pixel was changed, False if it was already that color
            
        Raises:
            ValidationError: If coordinates are out of bounds or color is invalid
        """
        if not (0 <= x < self._width and 0 <= y < self._height):
            from ..utils.logging import log_error
            error_msg = tr_error(AppConstants.ERROR_COORDS_OUT_OF_BOUNDS)
            log_error("model", f"set_pixel validation failed: {error_msg}")
            raise ValidationError(error_msg)
        
        if not color.isValid():
            from ..utils.logging import log_error
            error_msg = tr_error(AppConstants.ERROR_INVALID_COLOR)
            log_error("model", f"set_pixel validation failed: {error_msg} - {color}")
            raise ValidationError(error_msg)
        
        old_color = self.get_pixel(x, y)
        if old_color == color:
            return False
        
        # Use command pattern for undo/redo
        command = SetPixelCommand(self, x, y, color)
        self._command_history.execute_command(command)
        return True
    
    def _set_pixel_direct(self, x: int, y: int, color: QColor) -> None:
        """Set pixel directly without undo/redo (used by commands).
        
        Args:
            x: X coordinate
            y: Y coordinate
            color: Color to set
        """
        # Memory optimization: remove default color pixels instead of storing them
        default_color = QColor(AppConstants.DEFAULT_BG_COLOR)
        if color == default_color:
            self._pixels.pop((x, y), None)  # Remove if exists
        else:
            self._pixels[(x, y)] = QColor(color)
        
        self._is_modified = True
        self.pixel_changed.emit(x, y, color)
    
    def get_all_pixels(self) -> Dict[Tuple[int, int], QColor]:
        """Get all pixels as a dictionary.
        
        Returns:
            Dictionary mapping coordinates to colors
        """
        return self._pixels.copy()
    
    def clear(self) -> None:
        """Clear entire canvas to default background color.
        
        Resets all pixels to the default background color (white) and marks
        the model as modified. Emits canvas_cleared signal to notify UI.
        Uses memory optimization by not storing default color pixels.
        """
        # Memory optimization: don't store default color pixels
        self._pixels.clear()
        
        self._is_modified = True
        self.canvas_cleared.emit()
    
    def resize(self, new_width: int, new_height: int) -> None:
        """Resize canvas, preserving existing pixels.
        
        Args:
            new_width: New canvas width
            new_height: New canvas height
            
        Raises:
            ValidationError: If dimensions are invalid
        """
        validate_canvas_dimensions(new_width, new_height)
        
        if new_width == self._width and new_height == self._height:
            return
        
        new_pixels = {}
        default_color = QColor(AppConstants.DEFAULT_BG_COLOR)
        
        # Copy existing pixels and fill new areas
        for x in range(new_width):
            for y in range(new_height):
                if x < self._width and y < self._height:
                    new_pixels[(x, y)] = self.get_pixel(x, y)
                else:
                    new_pixels[(x, y)] = default_color
        
        self._width = new_width
        self._height = new_height
        self._pixels = new_pixels
        self._is_modified = True
        
        self.canvas_resized.emit(new_width, new_height)
    
    def flood_fill(self, start_x: int, start_y: int, new_color: QColor) -> List[Tuple[int, int]]:
        """Perform flood fill starting from given coordinates.
        
        Args:
            start_x: Starting X coordinate
            start_y: Starting Y coordinate
            new_color: Color to fill with
            
        Returns:
            List of coordinates that were changed
            
        Raises:
            ValidationError: If coordinates are out of bounds or color is invalid
        """
        if not (0 <= start_x < self._width and 0 <= start_y < self._height):
            raise ValidationError(f"Start coordinates ({start_x}, {start_y}) out of bounds")
        
        if not new_color.isValid():
            raise ValidationError("Invalid fill color")
        
        target_color = self.get_pixel(start_x, start_y)
        if target_color == new_color:
            return []
        
        changed_pixels = []
        stack = [(start_x, start_y)]
        visited = set()
        
        while stack:
            x, y = stack.pop()
            if (x, y) in visited:
                continue
            if not (0 <= x < self._width and 0 <= y < self._height):
                continue
            if self.get_pixel(x, y) != target_color:
                continue
            
            visited.add((x, y))
            self._pixels[(x, y)] = QColor(new_color)
            changed_pixels.append((x, y))
            
            # Add neighboring pixels
            stack.extend([(x+1, y), (x-1, y), (x, y+1), (x, y-1)])
        
        if changed_pixels:
            self._is_modified = True
            # Emit signal for each changed pixel
            for x, y in changed_pixels:
                self.pixel_changed.emit(x, y, new_color)
        
        return changed_pixels
    
    def load_from_dict(self, data: Dict) -> None:
        """Load model from dictionary data.
        
        Args:
            data: Dictionary containing width, height, and pixels
            
        Raises:
            ValidationError: If data format is invalid
        """
        # Validate data structure
        from ..utils.logging import log_error, log_info
        log_info("model", f"Loading model from dictionary data")
        
        required_fields = ["width", "height", "pixels"]
        for field in required_fields:
            if field not in data:
                error_msg = f"Missing required field: {field}"
                log_error("model", f"Model load validation failed: {error_msg}")
                raise ValidationError(error_msg)
        
        width, height = data["width"], data["height"]
        try:
            validate_canvas_dimensions(width, height)
        except ValidationError as e:
            log_error("model", f"Model load validation failed: {str(e)}")
            raise
        
        if not isinstance(data["pixels"], dict):
            error_msg = "Pixels data must be a dictionary"
            log_error("model", f"Model load validation failed: {error_msg}")
            raise ValidationError(error_msg)
        
        # Parse and validate pixel data
        new_pixels = {}
        # Initialize all pixels with default background color first
        for x in range(width):
            for y in range(height):
                new_pixels[(x, y)] = QColor(AppConstants.DEFAULT_BG_COLOR)
        
        # Then override with loaded pixel data
        for coord_str, color_str in data["pixels"].items():
            try:
                x, y = map(int, coord_str.split(','))
                if not (0 <= x < width and 0 <= y < height):
                    raise ValueError(f"Pixel coordinate out of bounds: ({x}, {y})")
                
                color = QColor(color_str)
                if not color.isValid():
                    raise ValueError(f"Invalid color: {color_str}")
                
                new_pixels[(x, y)] = color
            except ValueError as e:
                error_msg = f"Invalid pixel data: {e}"
                log_error("model", f"Model load pixel validation failed: {error_msg}")
                raise ValidationError(error_msg)
        
        # Apply loaded data
        old_width, old_height = self._width, self._height
        self._width = width
        self._height = height
        self._pixels = new_pixels
        self._is_modified = False
        
        # Emit appropriate signals
        if old_width != width or old_height != height:
            self.canvas_resized.emit(width, height)
        
        self.model_loaded.emit()
    
    def to_dict(self) -> Dict:
        """Convert model to dictionary for serialization.
        
        Returns:
            Dictionary containing width, height, and pixels
        """
        return {
            "width": self._width,
            "height": self._height,
            "pixels": {f"{x},{y}": color.name().upper() for (x, y), color in self._pixels.items()}
        }
    
    def set_current_file(self, file_path: Optional[str]) -> None:
        """Set the current file path.
        
        Args:
            file_path: Path to current file, or None if no file
        """
        self._current_file = file_path
        if file_path:
            self._is_modified = False
            self.model_saved.emit(file_path)
    
    
    def can_undo(self) -> bool:
        """Check if undo is available."""
        return self._command_history.can_undo()
    
    def can_redo(self) -> bool:
        """Check if redo is available."""
        return self._command_history.can_redo()
    
    def undo(self) -> bool:
        """Undo the last operation."""
        return self._command_history.undo()
    
    def redo(self) -> bool:
        """Redo the last undone operation."""
        return self._command_history.redo()