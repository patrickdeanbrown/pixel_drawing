#!/usr/bin/env python3
"""
Pixel Drawing - A modern pixel art application for creating retro game assets.
Cross-platform GUI application built with PyQt6.
"""

import sys
import json
import os
import math
from abc import ABC, abstractmethod
from functools import partial
from typing import Tuple, Optional, List, Dict
from PIL import Image

from pixel_drawing.views.widgets import ColorButton

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QGroupBox, QSpinBox, QFileDialog, QMessageBox,
    QColorDialog, QToolBar, QStatusBar, QSizePolicy
)
from PyQt6.QtCore import Qt, QPoint, QRect, QSize, pyqtSignal, QObject
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QPixmap, QIcon, QAction, QFont
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtSvg import QSvgRenderer


class AppConstants:
    """Application constants and configuration values."""
    
    # Canvas defaults
    DEFAULT_CANVAS_WIDTH = 32
    DEFAULT_CANVAS_HEIGHT = 32
    DEFAULT_PIXEL_SIZE = 16
    MAX_CANVAS_SIZE = 256
    MIN_CANVAS_SIZE = 1
    
    # UI dimensions
    MIN_WINDOW_WIDTH = 1000
    MIN_WINDOW_HEIGHT = 700
    SIDE_PANEL_WIDTH = 250
    COLOR_BUTTON_SIZE = 24
    ICON_SIZE = 24
    COLOR_DISPLAY_WIDTH = 100
    COLOR_DISPLAY_HEIGHT = 30
    
    # Colors
    DEFAULT_BG_COLOR = "#FFFFFF"
    DEFAULT_FG_COLOR = "#000000"
    GRID_COLOR = "#CCCCCC"
    BORDER_COLOR = "#CCCCCC"
    HOVER_COLOR = "#0066CC"
    
    # UI settings
    RECENT_COLORS_COUNT = 6
    LARGE_CANVAS_THRESHOLD = 256
    
    # File formats
    PROJECT_FILE_FILTER = "JSON files (*.json)"
    PNG_FILE_FILTER = "PNG files (*.png)"


class PixelDrawingError(Exception):
    """Base exception for pixel drawing errors."""
    pass


class FileOperationError(PixelDrawingError):
    """File I/O related errors."""
    pass


class ValidationError(PixelDrawingError):
    """Input validation errors."""
    pass


def validate_canvas_dimensions(width: int, height: int) -> None:
    """Validate canvas dimensions are within acceptable limits.
    
    Args:
        width: Canvas width in pixels
        height: Canvas height in pixels
        
    Raises:
        ValidationError: If dimensions are invalid
    """
    if not isinstance(width, int) or not isinstance(height, int):
        raise ValidationError("Canvas dimensions must be integers")
    
    if width < AppConstants.MIN_CANVAS_SIZE or height < AppConstants.MIN_CANVAS_SIZE:
        raise ValidationError(f"Canvas dimensions must be at least {AppConstants.MIN_CANVAS_SIZE}x{AppConstants.MIN_CANVAS_SIZE}")
    
    if width > AppConstants.MAX_CANVAS_SIZE or height > AppConstants.MAX_CANVAS_SIZE:
        raise ValidationError(f"Canvas dimensions cannot exceed {AppConstants.MAX_CANVAS_SIZE}x{AppConstants.MAX_CANVAS_SIZE}")


def validate_file_path(file_path: str, operation: str = "access") -> None:
    """Validate file path for operations.
    
    Args:
        file_path: Path to validate
        operation: Type of operation ('read', 'write', 'access')
        
    Raises:
        FileOperationError: If file path is invalid for operation
    """
    if not file_path or not isinstance(file_path, str):
        raise FileOperationError("File path cannot be empty")
    
    if operation == "read":
        if not os.path.exists(file_path):
            raise FileOperationError(f"File does not exist: {file_path}")
        if not os.path.isfile(file_path):
            raise FileOperationError(f"Path is not a file: {file_path}")
        if not os.access(file_path, os.R_OK):
            raise FileOperationError(f"File is not readable: {file_path}")
    
    elif operation == "write":
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            raise FileOperationError(f"Directory does not exist: {directory}")
        if os.path.exists(file_path) and not os.access(file_path, os.W_OK):
            raise FileOperationError(f"File is not writable: {file_path}")
        if directory and not os.access(directory, os.W_OK):
            raise FileOperationError(f"Directory is not writable: {directory}")


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
        
        # Initialize with default background color
        self.clear()
    
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
            raise ValidationError(f"Coordinates ({x}, {y}) out of bounds")
        
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
            raise ValidationError(f"Coordinates ({x}, {y}) out of bounds")
        
        if not color.isValid():
            raise ValidationError("Invalid color")
        
        old_color = self.get_pixel(x, y)
        if old_color == color:
            return False
        
        # Memory optimization: remove default color pixels instead of storing them
        default_color = QColor(AppConstants.DEFAULT_BG_COLOR)
        if color == default_color:
            self._pixels.pop((x, y), None)  # Remove if exists
        else:
            self._pixels[(x, y)] = QColor(color)
        
        self._is_modified = True
        self.pixel_changed.emit(x, y, color)
        return True
    
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
        required_fields = ["width", "height", "pixels"]
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Missing required field: {field}")
        
        width, height = data["width"], data["height"]
        validate_canvas_dimensions(width, height)
        
        if not isinstance(data["pixels"], dict):
            raise ValidationError("Pixels data must be a dictionary")
        
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
                raise ValidationError(f"Invalid pixel data: {e}")
        
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


class DrawingTool(ABC):
    """Abstract base class for drawing tools."""
    
    def __init__(self, name: str, model: PixelArtModel):
        """Initialize drawing tool.
        
        Args:
            name: Tool name for display
            model: PixelArtModel to operate on
        """
        self._name = name
        self._model = model
    
    @property
    def name(self) -> str:
        """Get tool name."""
        return self._name
    
    @abstractmethod
    def on_press(self, x: int, y: int, color: QColor) -> bool:
        """Handle mouse press event.
        
        Args:
            x: X coordinate
            y: Y coordinate
            color: Current drawing color
            
        Returns:
            True if tool should continue receiving move events
        """
        pass
    
    @abstractmethod
    def on_move(self, x: int, y: int, color: QColor) -> None:
        """Handle mouse move event.
        
        Args:
            x: X coordinate
            y: Y coordinate
            color: Current drawing color
        """
        pass
    
    @abstractmethod
    def on_release(self, x: int, y: int, color: QColor) -> None:
        """Handle mouse release event.
        
        Args:
            x: X coordinate
            y: Y coordinate
            color: Current drawing color
        """
        pass


class BrushTool(DrawingTool):
    """Brush tool for painting individual pixels."""
    
    def __init__(self, model: PixelArtModel):
        """Initialize brush tool."""
        super().__init__("Brush", model)
        self._is_drawing = False
    
    def on_press(self, x: int, y: int, color: QColor) -> bool:
        """Start brush stroke."""
        try:
            self._model.set_pixel(x, y, color)
            self._is_drawing = True
            return True  # Continue receiving move events
        except ValidationError:
            return False
    
    def on_move(self, x: int, y: int, color: QColor) -> None:
        """Continue brush stroke."""
        if self._is_drawing:
            try:
                self._model.set_pixel(x, y, color)
            except ValidationError:
                pass  # Ignore out-of-bounds moves
    
    def on_release(self, x: int, y: int, color: QColor) -> None:
        """End brush stroke."""
        self._is_drawing = False


class FillTool(DrawingTool):
    """Fill bucket tool for flood fill operations."""
    
    def __init__(self, model: PixelArtModel):
        """Initialize fill tool."""
        super().__init__("Fill Bucket", model)
    
    def on_press(self, x: int, y: int, color: QColor) -> bool:
        """Perform flood fill."""
        try:
            changed_pixels = self._model.flood_fill(x, y, color)
            return False  # No move events needed for fill
        except ValidationError:
            return False
    
    def on_move(self, x: int, y: int, color: QColor) -> None:
        """Fill tool doesn't use move events."""
        pass
    
    def on_release(self, x: int, y: int, color: QColor) -> None:
        """Fill tool doesn't use release events."""
        pass


class ToolManager:
    """Manages available drawing tools and current tool selection."""
    
    def __init__(self, model: PixelArtModel):
        """Initialize tool manager.
        
        Args:
            model: PixelArtModel for tools to operate on
        """
        self._model = model
        self._tools: Dict[str, DrawingTool] = {}
        self._current_tool: Optional[DrawingTool] = None
        
        # Register default tools
        self.register_tool("brush", BrushTool(model))
        self.register_tool("fill", FillTool(model))
        
        # Set default tool
        self.set_current_tool("brush")
    
    def register_tool(self, tool_id: str, tool: DrawingTool) -> None:
        """Register a new tool.
        
        Args:
            tool_id: Unique identifier for the tool
            tool: DrawingTool instance
        """
        self._tools[tool_id] = tool
    
    def get_tool(self, tool_id: str) -> Optional[DrawingTool]:
        """Get tool by ID.
        
        Args:
            tool_id: Tool identifier
            
        Returns:
            DrawingTool instance or None if not found
        """
        return self._tools.get(tool_id)
    
    def get_available_tools(self) -> Dict[str, str]:
        """Get available tools.
        
        Returns:
            Dictionary mapping tool IDs to tool names
        """
        return {tool_id: tool.name for tool_id, tool in self._tools.items()}
    
    def set_current_tool(self, tool_id: str) -> bool:
        """Set the current active tool.
        
        Args:
            tool_id: Tool identifier
            
        Returns:
            True if tool was set successfully
        """
        tool = self.get_tool(tool_id)
        if tool:
            self._current_tool = tool
            return True
        return False
    
    @property
    def current_tool(self) -> Optional[DrawingTool]:
        """Get current active tool."""
        return self._current_tool
    
    def handle_press(self, x: int, y: int, color: QColor) -> bool:
        """Handle mouse press with current tool.
        
        Args:
            x: X coordinate
            y: Y coordinate
            color: Current drawing color
            
        Returns:
            True if tool should receive move events
        """
        if self._current_tool:
            return self._current_tool.on_press(x, y, color)
        return False
    
    def handle_move(self, x: int, y: int, color: QColor) -> None:
        """Handle mouse move with current tool."""
        if self._current_tool:
            self._current_tool.on_move(x, y, color)
    
    def handle_release(self, x: int, y: int, color: QColor) -> None:
        """Handle mouse release with current tool."""
        if self._current_tool:
            self._current_tool.on_release(x, y, color)


class PixelCanvas(QWidget):
    """Interactive canvas widget for pixel art drawing and editing.
    
    This widget provides the visual interface for pixel art creation, handling
    mouse interactions, rendering the pixel grid, and coordinating with drawing
    tools. It implements the View component of the MVC architecture.
    
    Features:
        - Real-time pixel drawing with brush and fill tools
        - Grid-based display with configurable pixel size
        - Mouse tracking for pixel coordinate display
        - Optimized rendering with partial update regions
        - Tool management and selection
        
    Signals:
        color_used(QColor): Emitted when a color is applied to canvas
        tool_changed(str): Emitted when active drawing tool changes  
        pixel_hovered(int, int): Emitted when mouse hovers over pixel coordinates
    """
    
    # Signals for decoupled communication
    color_used = pyqtSignal(QColor)  # Emitted when a color is actually used on canvas
    tool_changed = pyqtSignal(str)  # Emitted when drawing tool changes
    pixel_hovered = pyqtSignal(int, int)  # Emitted when mouse hovers over pixel
    
    def __init__(self, parent=None, model: Optional[PixelArtModel] = None, pixel_size: int = AppConstants.DEFAULT_PIXEL_SIZE):
        """Initialize pixel canvas with model and display settings.
        
        Sets up the canvas widget with the specified model and pixel size,
        initializes tool management, and connects model signals for updates.
        Enables mouse tracking for hover effects and coordinate display.
        
        Args:
            parent: Parent widget (typically the main application window)
            model: PixelArtModel to display and edit (creates default if None)
            pixel_size: Size of each logical pixel in screen pixels (default: 16)
        """
        super().__init__(parent)
        self.pixel_size = pixel_size
        self.current_color = QColor(AppConstants.DEFAULT_FG_COLOR)
        self._is_drawing = False
        
        # Set up model
        if model is None:
            model = PixelArtModel()
        self._model = model
        
        # Set up tool manager
        self._tool_manager = ToolManager(self._model)
        
        # Connect model signals
        self._model.pixel_changed.connect(self._on_pixel_changed)
        self._model.canvas_resized.connect(self._on_canvas_resized)
        self._model.canvas_cleared.connect(self._on_canvas_cleared)
        
        # Update widget size
        self._update_widget_size()
        
        # Enable mouse tracking
        self.setMouseTracking(True)
        
        # Performance optimizations
        self._grid_pen = QPen(QColor(AppConstants.GRID_COLOR), 1)
        self._cached_background = None
        self._last_canvas_size = (0, 0)
    
    @property
    def model(self) -> PixelArtModel:
        """Get the underlying model."""
        return self._model
    
    @property 
    def tool_manager(self) -> ToolManager:
        """Get the tool manager."""
        return self._tool_manager
    
    def _update_widget_size(self) -> None:
        """Update widget size based on model dimensions."""
        canvas_width = self._model.width * self.pixel_size
        canvas_height = self._model.height * self.pixel_size
        self.setFixedSize(canvas_width, canvas_height)
    
    def _on_pixel_changed(self, x: int, y: int, color: QColor) -> None:
        """Handle pixel changes from model."""
        # Update only the changed pixel region
        pixel_rect = QRect(x * self.pixel_size, y * self.pixel_size, 
                          self.pixel_size, self.pixel_size)
        self.update(pixel_rect)
        
        # Emit signal for color usage tracking
        self.color_used.emit(color)
    
    def _on_canvas_resized(self, new_width: int, new_height: int) -> None:
        """Handle canvas resize from model."""
        self._update_widget_size()
        self.update()
    
    def _on_canvas_cleared(self) -> None:
        """Handle canvas clear from model."""
        self.update()
    
    def paintEvent(self, event) -> None:
        """Paint the pixel grid with performance optimizations.
        
        Uses dirty region tracking and cached pen objects for optimal
        rendering performance, especially on large canvases.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        
        # Get update region to optimize drawing
        update_rect = event.rect()
        
        # Calculate which pixels need to be drawn
        start_x = max(0, update_rect.left() // self.pixel_size)
        start_y = max(0, update_rect.top() // self.pixel_size)
        end_x = min(self._model.width, (update_rect.right() // self.pixel_size) + 1)
        end_y = min(self._model.height, (update_rect.bottom() // self.pixel_size) + 1)
        
        # Performance optimization: batch similar operations
        painter.setPen(self._grid_pen)
        
        # Draw only the pixels in the update region
        for x in range(start_x, end_x):
            for y in range(start_y, end_y):
                color = self._model.get_pixel(x, y)
                x1 = x * self.pixel_size
                y1 = y * self.pixel_size
                
                # Fill pixel
                painter.fillRect(x1, y1, self.pixel_size, self.pixel_size, color)
                
                # Draw grid lines (pen already set above for performance)
                painter.drawRect(x1, y1, self.pixel_size, self.pixel_size)
    
    def get_pixel_coords(self, pos: QPoint) -> Tuple[int, int]:
        """Convert widget coordinates to pixel grid coordinates."""
        pixel_x = pos.x() // self.pixel_size
        pixel_y = pos.y() // self.pixel_size
        return pixel_x, pixel_y
    
    def set_current_tool(self, tool_id: str) -> bool:
        """Set the current drawing tool.
        
        Args:
            tool_id: Tool identifier
            
        Returns:
            True if tool was set successfully
        """
        success = self._tool_manager.set_current_tool(tool_id)
        if success:
            self.tool_changed.emit(tool_id)
        return success
    
    def get_current_tool_id(self) -> Optional[str]:
        """Get current tool ID."""
        current_tool = self._tool_manager.current_tool
        if current_tool:
            # Find tool ID by comparing tool instances
            for tool_id, tool in self._tool_manager._tools.items():
                if tool is current_tool:
                    return tool_id
        return None
    
    def mousePressEvent(self, event) -> None:
        """Handle mouse press events."""
        if event.button() == Qt.MouseButton.LeftButton:
            pixel_x, pixel_y = self.get_pixel_coords(event.pos())
            
            if 0 <= pixel_x < self._model.width and 0 <= pixel_y < self._model.height:
                self._is_drawing = self._tool_manager.handle_press(pixel_x, pixel_y, self.current_color)
    
    def mouseMoveEvent(self, event) -> None:
        """Handle mouse move events for continuous drawing and hover."""
        pixel_x, pixel_y = self.get_pixel_coords(event.pos())
        
        # Emit hover signal for status updates
        if 0 <= pixel_x < self._model.width and 0 <= pixel_y < self._model.height:
            self.pixel_hovered.emit(pixel_x, pixel_y)
        
        # Handle drawing
        if self._is_drawing:
            if 0 <= pixel_x < self._model.width and 0 <= pixel_y < self._model.height:
                self._tool_manager.handle_move(pixel_x, pixel_y, self.current_color)
    
    def mouseReleaseEvent(self, event) -> None:
        """Handle mouse release events."""
        if event.button() == Qt.MouseButton.LeftButton and self._is_drawing:
            pixel_x, pixel_y = self.get_pixel_coords(event.pos())
            if 0 <= pixel_x < self._model.width and 0 <= pixel_y < self._model.height:
                self._tool_manager.handle_release(pixel_x, pixel_y, self.current_color)
            self._is_drawing = False
    
    def wheelEvent(self, event) -> None:
        """Handle mouse wheel events for zooming.
        
        Args:
            event: QWheelEvent containing wheel delta and modifiers
        """
        # Only zoom when Ctrl is held
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            # Get wheel delta (positive = zoom in, negative = zoom out)
            delta = event.angleDelta().y()
            
            # Calculate new pixel size
            zoom_factor = 1.2 if delta > 0 else 1/1.2
            new_pixel_size = max(4, min(64, int(self.pixel_size * zoom_factor)))
            
            if new_pixel_size != self.pixel_size:
                self.pixel_size = new_pixel_size
                self._update_widget_size()
                self.update()
                
            event.accept()
        else:
            event.ignore()
    
    # Legacy methods for compatibility - delegate to model
    def clear_canvas(self) -> None:
        """Clear all pixels to white."""
        self._model.clear()
    
    def resize_canvas(self, new_width: int, new_height: int) -> None:
        """Resize the canvas while preserving existing pixels."""
        try:
            self._model.resize(new_width, new_height)
        except ValidationError as e:
            # Could emit an error signal here if needed
            pass


class FileService(QObject):
    """Service class for file I/O operations."""
    
    # Signals for file operations
    file_loaded = pyqtSignal(str)  # file_path
    file_saved = pyqtSignal(str)   # file_path
    file_exported = pyqtSignal(str)  # file_path
    operation_failed = pyqtSignal(str, str)  # operation, error_message
    
    def __init__(self) -> None:
        """Initialize file service."""
        super().__init__()
    
    def load_file(self, file_path: str, model: PixelArtModel) -> bool:
        """Load a pixel art file into the model.
        
        Args:
            file_path: Path to the file to load
            model: PixelArtModel to load data into
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate file path
            validate_file_path(file_path, "read")
            
            # Load and validate JSON data
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Load data into model
            model.load_from_dict(data)
            model.set_current_file(file_path)
            
            self.file_loaded.emit(file_path)
            return True
            
        except (FileOperationError, ValidationError, json.JSONDecodeError) as e:
            self.operation_failed.emit("load", str(e))
            return False
        except Exception as e:
            self.operation_failed.emit("load", f"Unexpected error: {str(e)}")
            return False
    
    def save_file(self, file_path: str, model: PixelArtModel) -> bool:
        """Save model data to a file.
        
        Args:
            file_path: Path to save the file to
            model: PixelArtModel to save data from
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure .json extension
            if not file_path.lower().endswith('.json'):
                file_path += '.json'
            
            # Validate file path for writing
            validate_file_path(file_path, "write")
            
            # Get data from model
            data = model.to_dict()
            
            # Write to temporary file first for safety
            temp_path = file_path + ".tmp"
            try:
                with open(temp_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                # Atomic move from temp to final location
                if os.path.exists(file_path):
                    backup_path = file_path + ".bak"
                    os.rename(file_path, backup_path)
                    try:
                        os.rename(temp_path, file_path)
                        os.remove(backup_path)  # Remove backup on success
                    except Exception:
                        os.rename(backup_path, file_path)  # Restore backup on failure
                        raise
                else:
                    os.rename(temp_path, file_path)
                
                model.set_current_file(file_path)
                self.file_saved.emit(file_path)
                return True
                
            finally:
                # Clean up temp file if it still exists
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    
        except (FileOperationError, ValidationError) as e:
            self.operation_failed.emit("save", str(e))
            return False
        except Exception as e:
            self.operation_failed.emit("save", f"Failed to save file: {str(e)}")
            return False
    
    def export_png(self, file_path: str, model: PixelArtModel) -> bool:
        """Export model as PNG image.
        
        Args:
            file_path: Path to save the PNG file
            model: PixelArtModel to export
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate file path for writing
            validate_file_path(file_path, "write")
            
            # Ensure .png extension
            if not file_path.lower().endswith('.png'):
                file_path += '.png'
            
            # Create PIL image
            img = Image.new("RGB", (model.width, model.height), "white")
            
            # Set pixels
            for x in range(model.width):
                for y in range(model.height):
                    color = model.get_pixel(x, y)
                    rgb = color.getRgb()[:3]  # Get RGB values
                    img.putpixel((x, y), rgb)
            
            # Save image
            img.save(file_path, "PNG", optimize=True)
            
            self.file_exported.emit(file_path)
            return True
            
        except (FileOperationError, ValidationError) as e:
            self.operation_failed.emit("export", str(e))
            return False
        except Exception as e:
            self.operation_failed.emit("export", f"Failed to export PNG: {str(e)}")
            return False






def main() -> None:
    """Main entry point."""
    from pixel_drawing.views import PixelDrawingApp
    
    app = QApplication(sys.argv)
    app.setApplicationName("Pixel Drawing")
    app.setOrganizationName("Pixel Drawing Team")
    
    window = PixelDrawingApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()