#!/usr/bin/env python3
"""
Pixel Drawing - A modern pixel art application for creating retro game assets.
Cross-platform GUI application built with PyQt6.
"""

import sys
import json
import os
import math
from typing import Tuple, Optional, List
from PIL import Image

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QGroupBox, QSpinBox, QFileDialog, QMessageBox,
    QColorDialog, QToolBar, QStatusBar, QSizePolicy
)
from PyQt6.QtCore import Qt, QPoint, QRect, QSize, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QPixmap, QIcon, QAction, QFont


class PixelCanvas(QWidget):
    """Canvas widget for pixel art drawing with grid and zoom functionality."""
    
    def __init__(self, parent=None, width: int = 32, height: int = 32, pixel_size: int = 16):
        super().__init__(parent)
        self.grid_width = width
        self.grid_height = height
        self.pixel_size = pixel_size
        self.current_color = QColor("#000000")
        self.current_tool = "brush"
        
        # Initialize pixel data
        self.pixels = {}
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                self.pixels[(x, y)] = QColor("#FFFFFF")
        
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
            painter.setPen(QPen(QColor("#CCCCCC"), 1))
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
        self.pixels[(x, y)] = QColor(self.current_color)
        self.update()  # Trigger repaint
    
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
    
    def clear_canvas(self):
        """Clear all pixels to white."""
        for key in self.pixels:
            self.pixels[key] = QColor("#FFFFFF")
        self.update()
    
    def resize_canvas(self, new_width: int, new_height: int):
        """Resize the canvas while preserving existing pixels."""
        new_pixels = {}
        
        # Copy existing pixels and fill new areas with white
        for x in range(new_width):
            for y in range(new_height):
                if x < self.grid_width and y < self.grid_height:
                    new_pixels[(x, y)] = self.pixels.get((x, y), QColor("#FFFFFF"))
                else:
                    new_pixels[(x, y)] = QColor("#FFFFFF")
        
        self.grid_width = new_width
        self.grid_height = new_height
        self.pixels = new_pixels
        
        # Resize the widget
        canvas_width = self.grid_width * self.pixel_size
        canvas_height = self.grid_height * self.pixel_size
        self.setFixedSize(canvas_width, canvas_height)
        
        self.update()


class ColorButton(QPushButton):
    """Custom color button with hover effects."""
    
    def __init__(self, color: QColor, parent=None):
        super().__init__(parent)
        self.color = color
        self.setFixedSize(24, 24)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color.name()};
                border: 1px solid #CCCCCC;
                border-radius: 2px;
            }}
            QPushButton:hover {{
                border: 3px solid #0066CC;
            }}
        """)
    
    def set_color(self, color: QColor):
        """Update the button color."""
        self.color = color
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color.name()};
                border: 1px solid #CCCCCC;
                border-radius: 2px;
            }}
            QPushButton:hover {{
                border: 3px solid #0066CC;
            }}
        """)


class ColorWheel(QWidget):
    """Custom color wheel widget using QPainter."""
    
    color_selected = pyqtSignal(QColor)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(150, 150)
        self.current_hue = 0.0
        
    def paintEvent(self, event):
        """Paint the color wheel."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        center = self.width() // 2
        outer_radius = center - 10
        inner_radius = 20
        
        # Draw color wheel
        for angle in range(360):
            # Calculate hue
            adjusted_angle = (90 - angle) % 360
            hue = adjusted_angle / 360.0
            
            for radius in range(inner_radius, outer_radius, 2):
                # Calculate saturation
                saturation = min(1.0, (radius - inner_radius) / (outer_radius - inner_radius))
                
                # Convert HSV to RGB
                color = QColor.fromHsvF(hue, saturation, 1.0)
                
                # Calculate position
                x1 = center + radius * math.cos(math.radians(angle))
                y1 = center + radius * math.sin(math.radians(angle))
                x2 = center + (radius + 2) * math.cos(math.radians(angle))
                y2 = center + (radius + 2) * math.sin(math.radians(angle))
                
                # Draw segment - convert to integers
                painter.setPen(QPen(color, 3))
                painter.drawLine(int(x1), int(y1), int(x2), int(y2))
        
        # Draw white center
        painter.setBrush(QBrush(QColor("white")))
        painter.setPen(QPen(QColor("#CCCCCC"), 2))
        painter.drawEllipse(center - inner_radius, center - inner_radius, 
                          inner_radius * 2, inner_radius * 2)
    
    def mousePressEvent(self, event):
        """Handle color wheel clicks."""
        center = self.width() // 2
        x = event.pos().x() - center
        y = event.pos().y() - center
        
        distance = math.sqrt(x*x + y*y)
        inner_radius = 20
        outer_radius = center - 10
        
        if distance < inner_radius:
            # White center
            self.color_selected.emit(QColor("#FFFFFF"))
        elif distance < outer_radius:
            # Color wheel area
            angle_rad = math.atan2(y, x)
            angle_deg = math.degrees(angle_rad)
            
            if angle_deg < 0:
                angle_deg += 360
            
            adjusted_angle = (90 - angle_deg) % 360
            hue = adjusted_angle / 360.0
            saturation = min(1.0, (distance - inner_radius) / (outer_radius - inner_radius))
            
            self.current_hue = hue
            color = QColor.fromHsvF(hue, saturation, 1.0)
            self.color_selected.emit(color)


class PixelDrawingApp(QMainWindow):
    """Main application class for the Pixel Drawing app."""
    
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.current_color = QColor("#000000")
        self.recent_colors = [QColor("#FFFFFF")] * 6
        
        self.setup_ui()
        self.setWindowTitle("Pixel Drawing - Retro Game Asset Creator")
        self.setMinimumSize(800, 600)
        
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
        
        self.canvas = PixelCanvas(self, 32, 32, 16)
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
        side_panel.setMaximumWidth(250)
        side_layout = QVBoxLayout(side_panel)
        
        # Tools group
        tools_group = QGroupBox("Tools")
        tools_layout = QVBoxLayout(tools_group)
        
        self.brush_btn = QPushButton("Brush")
        self.brush_btn.setCheckable(True)
        self.brush_btn.setChecked(True)
        self.brush_btn.clicked.connect(lambda: self.set_tool("brush"))
        tools_layout.addWidget(self.brush_btn)
        
        self.fill_btn = QPushButton("Fill Bucket")
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
        self.width_spin.setRange(1, 256)
        self.width_spin.setValue(32)
        width_layout.addWidget(self.width_spin)
        size_layout.addLayout(width_layout)
        
        height_layout = QHBoxLayout()
        height_layout.addWidget(QLabel("Height:"))
        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 256)
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
        self.color_display.setFixedSize(100, 30)
        self.color_display.setStyleSheet(f"background-color: {self.current_color.name()}; border: 1px solid #ccc;")
        color_layout.addWidget(self.color_display, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Color chooser button
        choose_btn = QPushButton("Choose Color")
        choose_btn.clicked.connect(self.choose_color)
        color_layout.addWidget(choose_btn)
        
        # Base colors
        base_label = QLabel("Base Colors:")
        base_label.setFont(QFont("Arial", 8))
        color_layout.addWidget(base_label)
        
        base_colors = [
            "#000000", "#FFFFFF", "#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF",
            "#800000", "#808080", "#800080", "#008000", "#000080", "#808000", "#FFA500", "#FFC0CB"
        ]
        
        base_grid = QGridLayout()
        for i, color_hex in enumerate(base_colors):
            row = i // 8
            col = i % 8
            color_btn = ColorButton(QColor(color_hex))
            color_btn.clicked.connect(lambda checked, c=color_hex: self.set_color(QColor(c)))
            base_grid.addWidget(color_btn, row, col)
        
        color_layout.addLayout(base_grid)
        
        # Recent colors
        recent_label = QLabel("Recent Colors:")
        recent_label.setFont(QFont("Arial", 8))
        color_layout.addWidget(recent_label)
        
        self.recent_buttons = []
        recent_layout = QHBoxLayout()
        for i in range(6):
            btn = ColorButton(self.recent_colors[i])
            btn.clicked.connect(lambda checked, idx=i: self.set_color(self.recent_colors[idx]))
            self.recent_buttons.append(btn)
            recent_layout.addWidget(btn)
        
        color_layout.addLayout(recent_layout)
        
        # Color wheel
        wheel_label = QLabel("Color Wheel:")
        wheel_label.setFont(QFont("Arial", 8))
        color_layout.addWidget(wheel_label)
        
        self.color_wheel = ColorWheel()
        self.color_wheel.color_selected.connect(self.set_color)
        color_layout.addWidget(self.color_wheel, alignment=Qt.AlignmentFlag.AlignCenter)
        
        parent_layout.addWidget(color_group)
    
    def set_tool(self, tool):
        """Set the current drawing tool."""
        self.canvas.current_tool = tool
        
        # Update button states
        self.brush_btn.setChecked(tool == "brush")
        self.fill_btn.setChecked(tool == "fill")
    
    def set_color(self, color: QColor):
        """Set the current color and update recent colors."""
        if color != self.current_color and color not in self.recent_colors:
            self.recent_colors.insert(0, color)
            self.recent_colors = self.recent_colors[:6]
            self.update_recent_colors()
        
        self.current_color = color
        self.canvas.current_color = color
        self.color_display.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #ccc;")
    
    def update_recent_colors(self):
        """Update recent color buttons."""
        for i, btn in enumerate(self.recent_buttons):
            btn.set_color(self.recent_colors[i])
            btn.clicked.disconnect()
            btn.clicked.connect(lambda checked, idx=i: self.set_color(self.recent_colors[idx]))
    
    def choose_color(self):
        """Open color chooser dialog."""
        color = QColorDialog.getColor(self.current_color, self, "Choose Color")
        if color.isValid():
            self.set_color(color)
    
    def new_file(self):
        """Create a new file."""
        reply = QMessageBox.question(self, "New File", "Are you sure? Unsaved changes will be lost.")
        if reply == QMessageBox.StandardButton.Yes:
            self.canvas.clear_canvas()
            self.current_file = None
            self.setWindowTitle("Pixel Drawing - Retro Game Asset Creator")
    
    def open_file(self):
        """Open a pixel art file."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Pixel Art File", "", "JSON files (*.json)")
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                # Restore canvas and pixels
                self.canvas.grid_width = data["width"]
                self.canvas.grid_height = data["height"]
                self.canvas.pixels = {tuple(map(int, k.split(','))): QColor(v) 
                                    for k, v in data["pixels"].items()}
                
                # Update UI
                self.width_spin.setValue(data["width"])
                self.height_spin.setValue(data["height"])
                
                # Resize canvas widget
                canvas_width = self.canvas.grid_width * self.canvas.pixel_size
                canvas_height = self.canvas.grid_height * self.canvas.pixel_size
                self.canvas.setFixedSize(canvas_width, canvas_height)
                
                self.canvas.update()
                self.current_file = file_path
                self.setWindowTitle(f"Pixel Drawing - {os.path.basename(file_path)}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open file: {str(e)}")
    
    def save_file(self):
        """Save the current pixel art."""
        if self.current_file:
            self._save_to_file(self.current_file)
        else:
            self.save_as_file()
    
    def save_as_file(self):
        """Save with a new filename."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Pixel Art File", "", "JSON files (*.json)")
        
        if file_path:
            self._save_to_file(file_path)
            self.current_file = file_path
            self.setWindowTitle(f"Pixel Drawing - {os.path.basename(file_path)}")
    
    def _save_to_file(self, file_path: str):
        """Save pixel data to file."""
        try:
            data = {
                "width": self.canvas.grid_width,
                "height": self.canvas.grid_height,
                "pixels": {f"{x},{y}": color.name() for (x, y), color in self.canvas.pixels.items()}
            }
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            QMessageBox.information(self, "Success", "File saved successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")
    
    def export_png(self):
        """Export as PNG image."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Export as PNG", "", "PNG files (*.png)")
        
        if file_path:
            try:
                # Create PIL image
                img = Image.new("RGB", (self.canvas.grid_width, self.canvas.grid_height), "white")
                
                for (x, y), color in self.canvas.pixels.items():
                    rgb = color.getRgb()[:3]  # Get RGB values
                    img.putpixel((x, y), rgb)
                
                img.save(file_path)
                QMessageBox.information(self, "Success", "PNG exported successfully!")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export PNG: {str(e)}")
    
    def resize_canvas(self):
        """Resize the canvas."""
        new_width = self.width_spin.value()
        new_height = self.height_spin.value()
        
        if new_width > 256 or new_height > 256:
            reply = QMessageBox.question(self, "Large Canvas", 
                                       "Large canvases may affect performance. Continue?")
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        self.canvas.resize_canvas(new_width, new_height)
    
    def clear_canvas(self):
        """Clear the canvas."""
        reply = QMessageBox.question(self, "Clear Canvas", "Are you sure you want to clear the canvas?")
        if reply == QMessageBox.StandardButton.Yes:
            self.canvas.clear_canvas()


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