#!/usr/bin/env python3
"""
Pixel Drawing - A modern pixel art application for creating retro game assets.
Cross-platform GUI application built with PyQt6.
"""

import sys
import json
import os
import math
from functools import partial
from typing import Tuple, Optional, List
from PIL import Image

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QGroupBox, QSpinBox, QFileDialog, QMessageBox,
    QColorDialog, QToolBar, QStatusBar, QSizePolicy
)
from PyQt6.QtCore import Qt, QPoint, QRect, QSize, pyqtSignal
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


class PixelCanvas(QWidget):
    """Canvas widget for pixel art drawing with grid and zoom functionality."""
    
    # Signals for decoupled communication
    color_used = pyqtSignal(QColor)  # Emitted when a color is actually used on canvas
    canvas_modified = pyqtSignal()  # Emitted when canvas content changes
    
    def __init__(self, parent=None, width: int = AppConstants.DEFAULT_CANVAS_WIDTH, height: int = AppConstants.DEFAULT_CANVAS_HEIGHT, pixel_size: int = AppConstants.DEFAULT_PIXEL_SIZE):
        super().__init__(parent)
        self.grid_width = width
        self.grid_height = height
        self.pixel_size = pixel_size
        self.current_color = QColor(AppConstants.DEFAULT_FG_COLOR)
        self.current_tool = "brush"
        
        # Initialize pixel data
        self.pixels = {}
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                self.pixels[(x, y)] = QColor(AppConstants.DEFAULT_BG_COLOR)
        
        # Set widget size
        canvas_width = self.grid_width * self.pixel_size
        canvas_height = self.grid_height * self.pixel_size
        self.setFixedSize(canvas_width, canvas_height)
        
        # Enable mouse tracking
        self.setMouseTracking(True)
        self.drawing = False
    
    def paintEvent(self, event):
        """Paint the pixel grid."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        
        # Draw pixels
        for (x, y), color in self.pixels.items():
            x1 = x * self.pixel_size
            y1 = y * self.pixel_size
            
            # Fill pixel
            painter.fillRect(x1, y1, self.pixel_size, self.pixel_size, color)
            
            # Draw grid lines
            painter.setPen(QPen(QColor(AppConstants.GRID_COLOR), 1))
            painter.drawRect(x1, y1, self.pixel_size, self.pixel_size)
    
    def get_pixel_coords(self, pos: QPoint) -> Tuple[int, int]:
        """Convert widget coordinates to pixel grid coordinates."""
        pixel_x = pos.x() // self.pixel_size
        pixel_y = pos.y() // self.pixel_size
        return pixel_x, pixel_y
    
    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if event.button() == Qt.MouseButton.LeftButton:
            pixel_x, pixel_y = self.get_pixel_coords(event.pos())
            
            if 0 <= pixel_x < self.grid_width and 0 <= pixel_y < self.grid_height:
                if self.current_tool == "brush":
                    self.paint_pixel(pixel_x, pixel_y)
                    self.drawing = True
                elif self.current_tool == "fill":
                    self.fill_bucket(pixel_x, pixel_y)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events for continuous drawing."""
        if self.drawing and self.current_tool == "brush":
            pixel_x, pixel_y = self.get_pixel_coords(event.pos())
            if 0 <= pixel_x < self.grid_width and 0 <= pixel_y < self.grid_height:
                self.paint_pixel(pixel_x, pixel_y)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release events."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False
    
    def paint_pixel(self, x: int, y: int):
        """Paint a single pixel with the current color."""
        old_color = self.pixels.get((x, y))
        self.pixels[(x, y)] = QColor(self.current_color)
        self.update()  # Trigger repaint
        
        # Emit signals for decoupled communication
        if old_color != self.current_color:
            self.color_used.emit(self.current_color)
            self.canvas_modified.emit()
    
    def fill_bucket(self, start_x: int, start_y: int):
        """Fill connected pixels of the same color."""
        target_color = self.pixels[(start_x, start_y)]
        if target_color == self.current_color:
            return
        
        stack = [(start_x, start_y)]
        visited = set()
        
        while stack:
            x, y = stack.pop()
            if (x, y) in visited:
                continue
            if x < 0 or x >= self.grid_width or y < 0 or y >= self.grid_height:
                continue
            if self.pixels[(x, y)] != target_color:
                continue
            
            visited.add((x, y))
            self.pixels[(x, y)] = QColor(self.current_color)
            
            # Add neighboring pixels to stack
            stack.extend([(x+1, y), (x-1, y), (x, y+1), (x, y-1)])
        
        self.update()
        
        # Emit signals for decoupled communication  
        self.color_used.emit(self.current_color)
        self.canvas_modified.emit()
    
    def clear_canvas(self):
        """Clear all pixels to white."""
        for key in self.pixels:
            self.pixels[key] = QColor(AppConstants.DEFAULT_BG_COLOR)
        self.update()
        self.canvas_modified.emit()
    
    def resize_canvas(self, new_width: int, new_height: int):
        """Resize the canvas while preserving existing pixels."""
        new_pixels = {}
        
        # Copy existing pixels and fill new areas with white
        for x in range(new_width):
            for y in range(new_height):
                if x < self.grid_width and y < self.grid_height:
                    new_pixels[(x, y)] = self.pixels.get((x, y), QColor(AppConstants.DEFAULT_BG_COLOR))
                else:
                    new_pixels[(x, y)] = QColor(AppConstants.DEFAULT_BG_COLOR)
        
        self.grid_width = new_width
        self.grid_height = new_height
        self.pixels = new_pixels
        
        # Resize the widget
        canvas_width = self.grid_width * self.pixel_size
        canvas_height = self.grid_height * self.pixel_size
        self.setFixedSize(canvas_width, canvas_height)
        
        self.update()
        self.canvas_modified.emit()


class ColorButton(QPushButton):
    """Custom color button with hover effects."""
    
    def __init__(self, color: QColor, parent=None):
        super().__init__(parent)
        self.color = color
        self.setFixedSize(AppConstants.COLOR_BUTTON_SIZE, AppConstants.COLOR_BUTTON_SIZE)
        self._update_stylesheet()
    
    def _update_stylesheet(self):
        """Update the button stylesheet with current color."""
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.color.name()};
                border: 1px solid {AppConstants.BORDER_COLOR};
                border-radius: 2px;
            }}
            QPushButton:hover {{
                border: 3px solid {AppConstants.HOVER_COLOR};
            }}
        """)
    
    def set_color(self, color: QColor):
        """Update the button color."""
        self.color = color
        self._update_stylesheet()



class PixelDrawingApp(QMainWindow):
    """Main application class for the Pixel Drawing app."""
    
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.current_color = QColor(AppConstants.DEFAULT_FG_COLOR)
        self.recent_colors = [QColor(AppConstants.DEFAULT_BG_COLOR)] * AppConstants.RECENT_COLORS_COUNT
        
        self.setup_ui()
        self.setWindowTitle("Pixel Drawing - Retro Game Asset Creator")
        self.setMinimumSize(AppConstants.MIN_WINDOW_WIDTH, AppConstants.MIN_WINDOW_HEIGHT)
        
        # Apply modern styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 5px;
                min-width: 60px;
            }
            QPushButton:hover {
                background-color: #e6f3ff;
                border-color: #0066cc;
            }
            QPushButton:pressed {
                background-color: #cce7ff;
            }
        """)
    
    def setup_ui(self):
        """Set up the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Create canvas area
        canvas_frame = QFrame()
        canvas_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        canvas_layout = QVBoxLayout(canvas_frame)
        
        self.canvas = PixelCanvas(self, AppConstants.DEFAULT_CANVAS_WIDTH, AppConstants.DEFAULT_CANVAS_HEIGHT, AppConstants.DEFAULT_PIXEL_SIZE)
        # Connect canvas signals for decoupled communication
        self.canvas.color_used.connect(self._on_color_used)
        self.canvas.canvas_modified.connect(self._on_canvas_modified)
        canvas_layout.addWidget(self.canvas, alignment=Qt.AlignmentFlag.AlignCenter)
        
        main_layout.addWidget(canvas_frame, 1)
        
        # Create side panel
        self.create_side_panel(main_layout)
        
        # Create toolbar
        self.create_toolbar()
        
        # Create status bar
        self.statusBar().showMessage("Ready")
    
    def create_toolbar(self):
        """Create the toolbar."""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # File actions
        new_action = QAction("New", self)
        new_action.triggered.connect(self.new_file)
        toolbar.addAction(new_action)
        
        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)
        
        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_file)
        toolbar.addAction(save_action)
        
        save_as_action = QAction("Save As", self)
        save_as_action.triggered.connect(self.save_as_file)
        toolbar.addAction(save_as_action)
        
        toolbar.addSeparator()
        
        export_action = QAction("Export PNG", self)
        export_action.triggered.connect(self.export_png)
        toolbar.addAction(export_action)
    
    def create_side_panel(self, main_layout):
        """Create the side panel with tools and options."""
        side_panel = QWidget()
        side_panel.setMaximumWidth(AppConstants.SIDE_PANEL_WIDTH)
        side_layout = QVBoxLayout(side_panel)
        
        # Tools group
        tools_group = QGroupBox("Tools")
        tools_layout = QVBoxLayout(tools_group)
        
        # Create brush tool button with icon
        self.brush_btn = QPushButton("Brush")
        self.brush_btn.setIcon(self.create_svg_icon("icons/paint-brush.svg"))
        self.brush_btn.setIconSize(QSize(AppConstants.ICON_SIZE, AppConstants.ICON_SIZE))
        self.brush_btn.setCheckable(True)
        self.brush_btn.setChecked(True)
        self.brush_btn.clicked.connect(lambda: self.set_tool("brush"))
        tools_layout.addWidget(self.brush_btn)
        
        # Create fill tool button with icon
        self.fill_btn = QPushButton("Fill Bucket")
        self.fill_btn.setIcon(self.create_svg_icon("icons/paint-bucket.svg"))
        self.fill_btn.setIconSize(QSize(AppConstants.ICON_SIZE, AppConstants.ICON_SIZE))
        self.fill_btn.setCheckable(True)
        self.fill_btn.clicked.connect(lambda: self.set_tool("fill"))
        tools_layout.addWidget(self.fill_btn)
        
        side_layout.addWidget(tools_group)
        
        # Color group
        self.create_color_panel(side_layout)
        
        # Canvas size group
        size_group = QGroupBox("Canvas Size")
        size_layout = QVBoxLayout(size_group)
        
        width_layout = QHBoxLayout()
        width_layout.addWidget(QLabel("Width:"))
        self.width_spin = QSpinBox()
        self.width_spin.setRange(AppConstants.MIN_CANVAS_SIZE, AppConstants.MAX_CANVAS_SIZE)
        self.width_spin.setValue(32)
        width_layout.addWidget(self.width_spin)
        size_layout.addLayout(width_layout)
        
        height_layout = QHBoxLayout()
        height_layout.addWidget(QLabel("Height:"))
        self.height_spin = QSpinBox()
        self.height_spin.setRange(AppConstants.MIN_CANVAS_SIZE, AppConstants.MAX_CANVAS_SIZE)
        self.height_spin.setValue(32)
        height_layout.addWidget(self.height_spin)
        size_layout.addLayout(height_layout)
        
        resize_btn = QPushButton("Resize Canvas")
        resize_btn.clicked.connect(self.resize_canvas)
        size_layout.addWidget(resize_btn)
        
        side_layout.addWidget(size_group)
        
        # Actions group
        actions_group = QGroupBox("Actions")
        actions_layout = QVBoxLayout(actions_group)
        
        clear_btn = QPushButton("Clear Canvas")
        clear_btn.clicked.connect(self.clear_canvas)
        actions_layout.addWidget(clear_btn)
        
        side_layout.addWidget(actions_group)
        
        side_layout.addStretch()
        main_layout.addWidget(side_panel)
    
    def create_color_panel(self, parent_layout):
        """Create the color selection panel."""
        color_group = QGroupBox("Color")
        color_layout = QVBoxLayout(color_group)
        
        # Current color display
        self.color_display = QLabel()
        self.color_display.setFixedSize(AppConstants.COLOR_DISPLAY_WIDTH, AppConstants.COLOR_DISPLAY_HEIGHT)
        self.color_display.setStyleSheet(f"background-color: {self.current_color.name()}; border: 1px solid #ccc;")
        color_layout.addWidget(self.color_display, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Color chooser button
        choose_btn = QPushButton("Choose Color")
        choose_btn.clicked.connect(self.choose_color)
        color_layout.addWidget(choose_btn)
        
        # Recent colors
        recent_label = QLabel("Recent Colors:")
        recent_label.setFont(QFont("Arial", 8))
        color_layout.addWidget(recent_label)
        
        self.recent_buttons = []
        recent_layout = QHBoxLayout()
        for i in range(AppConstants.RECENT_COLORS_COUNT):
            btn = ColorButton(self.recent_colors[i])
            # Fix lambda closure bug by creating a proper closure with functools.partial
            btn.clicked.connect(partial(self._on_recent_color_clicked, i))
            self.recent_buttons.append(btn)
            recent_layout.addWidget(btn)
        
        color_layout.addLayout(recent_layout)
        
        parent_layout.addWidget(color_group)
    
    def set_tool(self, tool):
        """Set the current drawing tool."""
        self.canvas.current_tool = tool
        
        # Update button states
        self.brush_btn.setChecked(tool == "brush")
        self.fill_btn.setChecked(tool == "fill")
    
    def set_color(self, color: QColor, add_to_recent: bool = False):
        """Set the current color and optionally update recent colors."""
        if add_to_recent and color != self.current_color and color not in self.recent_colors:
            self.recent_colors.insert(0, color)
            self.recent_colors = self.recent_colors[:6]
            self.update_recent_colors()
        
        self.current_color = color
        self.canvas.current_color = color
        self.color_display.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #ccc;")
    
    def _on_recent_color_clicked(self, index: int, checked: bool = False) -> None:
        """Handle recent color button clicks."""
        if 0 <= index < len(self.recent_colors):
            self.set_color(self.recent_colors[index], add_to_recent=True)
    
    def update_recent_colors(self):
        """Update recent color buttons."""
        for i, btn in enumerate(self.recent_buttons):
            btn.set_color(self.recent_colors[i])
            btn.clicked.disconnect()
            btn.clicked.connect(partial(self._on_recent_color_clicked, i))
    
    def choose_color(self):
        """Open color chooser dialog."""
        color = QColorDialog.getColor(self.current_color, self, "Choose Color")
        if color.isValid():
            self.set_color(color, add_to_recent=True)
    
    
    def new_file(self):
        """Create a new file."""
        reply = QMessageBox.question(self, "New File", "Are you sure? Unsaved changes will be lost.")
        if reply == QMessageBox.StandardButton.Yes:
            self.canvas.clear_canvas()
            self.current_file = None
            self.setWindowTitle("Pixel Drawing - Retro Game Asset Creator")
    
    def open_file(self):
        """Open a pixel art file."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Pixel Art File", "", AppConstants.PROJECT_FILE_FILTER)
        
        if not file_path:
            return
            
        try:
            # Validate file path
            validate_file_path(file_path, "read")
            
            # Load and validate JSON data
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate required fields
            required_fields = ["width", "height", "pixels"]
            for field in required_fields:
                if field not in data:
                    raise FileOperationError(f"Invalid file format: missing '{field}' field")
            
            # Validate canvas dimensions
            width, height = data["width"], data["height"]
            validate_canvas_dimensions(width, height)
            
            # Validate pixels data
            if not isinstance(data["pixels"], dict):
                raise FileOperationError("Invalid file format: 'pixels' must be a dictionary")
            
            # Parse pixel data
            pixels = {}
            for coord_str, color_str in data["pixels"].items():
                try:
                    x, y = map(int, coord_str.split(','))
                    if not (0 <= x < width and 0 <= y < height):
                        raise ValueError(f"Pixel coordinate out of bounds: ({x}, {y})")
                    pixels[(x, y)] = QColor(color_str)
                    if not pixels[(x, y)].isValid():
                        raise ValueError(f"Invalid color: {color_str}")
                except ValueError as e:
                    raise FileOperationError(f"Invalid pixel data: {e}")
            
            # Apply loaded data
            self.canvas.grid_width = width
            self.canvas.grid_height = height
            self.canvas.pixels = pixels
            
            # Update UI
            self.width_spin.setValue(width)
            self.height_spin.setValue(height)
            
            # Resize canvas widget
            canvas_width = self.canvas.grid_width * self.canvas.pixel_size
            canvas_height = self.canvas.grid_height * self.canvas.pixel_size
            self.canvas.setFixedSize(canvas_width, canvas_height)
            
            self.canvas.update()
            self.current_file = file_path
            self.setWindowTitle(f"Pixel Drawing - {os.path.basename(file_path)}")
            self.statusBar().showMessage(f"Opened: {os.path.basename(file_path)}")
            
        except (FileOperationError, ValidationError, json.JSONDecodeError) as e:
            QMessageBox.critical(self, "File Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Unexpected error opening file: {str(e)}")
    
    def save_file(self):
        """Save the current pixel art."""
        if self.current_file:
            self._save_to_file(self.current_file)
        else:
            self.save_as_file()
    
    def save_as_file(self):
        """Save with a new filename."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Pixel Art File", "", AppConstants.PROJECT_FILE_FILTER)
        
        if file_path:
            self._save_to_file(file_path)
            self.current_file = file_path
            self.setWindowTitle(f"Pixel Drawing - {os.path.basename(file_path)}")
    
    def _save_to_file(self, file_path: str):
        """Save pixel data to file.
        
        Args:
            file_path: Path to save the file to
            
        Raises:
            FileOperationError: If file cannot be saved
        """
        try:
            # Validate file path for writing
            validate_file_path(file_path, "write")
            
            # Prepare data
            data = {
                "width": self.canvas.grid_width,
                "height": self.canvas.grid_height,
                "pixels": {f"{x},{y}": color.name() for (x, y), color in self.canvas.pixels.items()}
            }
            
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
                
                self.statusBar().showMessage(f"Saved: {os.path.basename(file_path)}")
                QMessageBox.information(self, "Success", "File saved successfully!")
                
            finally:
                # Clean up temp file if it still exists
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    
        except (FileOperationError, ValidationError) as e:
            QMessageBox.critical(self, "File Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")
    
    def export_png(self):
        """Export as PNG image."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Export as PNG", "", AppConstants.PNG_FILE_FILTER)
        
        if not file_path:
            return
            
        try:
            # Validate file path for writing
            validate_file_path(file_path, "write")
            
            # Ensure .png extension
            if not file_path.lower().endswith('.png'):
                file_path += '.png'
            
            # Create PIL image
            img = Image.new("RGB", (self.canvas.grid_width, self.canvas.grid_height), "white")
            
            # Set pixels
            for (x, y), color in self.canvas.pixels.items():
                if 0 <= x < self.canvas.grid_width and 0 <= y < self.canvas.grid_height:
                    rgb = color.getRgb()[:3]  # Get RGB values
                    img.putpixel((x, y), rgb)
            
            # Save image
            img.save(file_path, "PNG", optimize=True)
            
            self.statusBar().showMessage(f"Exported: {os.path.basename(file_path)}")
            QMessageBox.information(self, "Success", "PNG exported successfully!")
            
        except (FileOperationError, ValidationError) as e:
            QMessageBox.critical(self, "Export Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export PNG: {str(e)}")
    
    def create_svg_icon(self, svg_path: str) -> QIcon:
        """Create a QIcon from an SVG file."""
        if not os.path.exists(svg_path):
            return QIcon()  # Return empty icon if file doesn't exist
        
        renderer = QSvgRenderer(svg_path)
        pixmap = QPixmap(AppConstants.ICON_SIZE, AppConstants.ICON_SIZE)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        
        return QIcon(pixmap)
    
    def resize_canvas(self):
        """Resize the canvas with validation."""
        new_width = self.width_spin.value()
        new_height = self.height_spin.value()
        
        try:
            # Validate dimensions
            validate_canvas_dimensions(new_width, new_height)
            
            # Warn about large canvases
            if new_width > AppConstants.LARGE_CANVAS_THRESHOLD or new_height > AppConstants.LARGE_CANVAS_THRESHOLD:
                reply = QMessageBox.question(
                    self, 
                    "Large Canvas", 
                    f"Canvas size {new_width}x{new_height} may affect performance. Continue?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return
            
            # Perform resize
            self.canvas.resize_canvas(new_width, new_height)
            self.statusBar().showMessage(f"Canvas resized to {new_width}x{new_height}")
            
        except ValidationError as e:
            QMessageBox.warning(self, "Invalid Dimensions", str(e))
            # Reset spinboxes to current canvas size
            self.width_spin.setValue(self.canvas.grid_width)
            self.height_spin.setValue(self.canvas.grid_height)
    
    def clear_canvas(self):
        """Clear the canvas."""
        reply = QMessageBox.question(self, "Clear Canvas", "Are you sure you want to clear the canvas?")
        if reply == QMessageBox.StandardButton.Yes:
            self.canvas.clear_canvas()
    
    def _on_color_used(self, color: QColor) -> None:
        """Handle color usage on canvas (slot for canvas.color_used signal)."""
        if color != self.current_color and color not in self.recent_colors:
            self.recent_colors.insert(0, color)
            self.recent_colors = self.recent_colors[:AppConstants.RECENT_COLORS_COUNT]
            self.update_recent_colors()
    
    def _on_canvas_modified(self) -> None:
        """Handle canvas modifications (slot for canvas.canvas_modified signal)."""
        # Mark document as modified (could be used for save state tracking)
        # For now, just update status bar
        self.statusBar().showMessage("Canvas modified")


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("Pixel Drawing")
    app.setOrganizationName("Pixel Drawing Team")
    
    window = PixelDrawingApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()