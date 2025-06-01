"""Main application window for the Pixel Drawing application."""

import os
from functools import partial
from typing import Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QGroupBox, QSpinBox, QFileDialog, QMessageBox,
    QColorDialog, QToolBar
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPainter, QColor, QPixmap, QIcon, QAction, QFont
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtSvg import QSvgRenderer

from ..constants import AppConstants
from ..exceptions import ValidationError
from ..models.pixel_art_model import PixelArtModel
from ..services.file_service import FileService
from ..controllers.tools.manager import ToolManager
from ..views.canvas import PixelCanvas
from ..views.widgets.color_button import ColorButton
from ..utils.shortcuts import setup_keyboard_shortcuts


class PixelDrawingApp(QMainWindow):
    """Main application window for the Pixel Drawing application.
    
    This class implements the Controller and main View components of the MVC
    architecture, coordinating between the pixel art model, canvas display,
    and user interface elements. It manages the application lifecycle,
    file operations, tool selection, and user interactions.
    
    Features:
        - Complete pixel art creation and editing interface
        - File operations (new, open, save, export)
        - Tool selection (brush, fill bucket)
        - Color selection with recent colors palette
        - Canvas resizing and clearing
        - Modern Qt-based UI with professional styling
        
    Architecture:
        - Uses PixelArtModel for data management
        - PixelCanvas for drawing interface
        - FileService for I/O operations
        - Signal/slot pattern for decoupled communication
    """
    
    def __init__(self):
        super().__init__()
        
        # Initialize core components
        self._model = PixelArtModel()
        self._file_service = FileService()
        
        # UI state
        self.current_color = QColor(AppConstants.DEFAULT_FG_COLOR)
        self.recent_colors = [QColor(AppConstants.DEFAULT_BG_COLOR)] * AppConstants.RECENT_COLORS_COUNT
        
        # Set up connections
        self._setup_connections()
        
        # Set up UI
        self.setup_ui()
        self.setWindowTitle("Pixel Drawing - Retro Game Asset Creator")
        self.setMinimumSize(AppConstants.MIN_WINDOW_WIDTH, AppConstants.MIN_WINDOW_HEIGHT)
        
        # Set up keyboard shortcuts using utility function
        setup_keyboard_shortcuts(self)
        
        # Apply modern styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F0F0F0;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #CCCCCC;
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
                background-color: #FFFFFF;
                border: 1px solid #CCCCCC;
                border-radius: 3px;
                padding: 5px;
                min-width: 60px;
            }
            QPushButton:hover {
                background-color: #E6F3FF;
                border-color: #0066CC;
            }
            QPushButton:pressed {
                background-color: #CCE7FF;
            }
        """)
    
    def _setup_connections(self) -> None:
        """Set up signal/slot connections between components."""
        # Model signals
        self._model.model_loaded.connect(self._on_model_loaded)
        self._model.model_saved.connect(self._on_model_saved)
        
        # File service signals
        self._file_service.file_loaded.connect(self._on_file_loaded)
        self._file_service.file_saved.connect(self._on_file_saved)
        self._file_service.file_exported.connect(self._on_file_exported)
        self._file_service.operation_failed.connect(self._on_file_operation_failed)
    
    def setup_ui(self) -> None:
        """Set up the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Create canvas area
        canvas_frame = QFrame()
        canvas_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        canvas_layout = QVBoxLayout(canvas_frame)
        
        self.canvas = PixelCanvas(self, self._model, AppConstants.DEFAULT_PIXEL_SIZE)
        # Connect canvas signals for decoupled communication
        self.canvas.color_used.connect(self._on_color_used)
        self.canvas.tool_changed.connect(self._on_tool_changed)
        self.canvas.pixel_hovered.connect(self._on_pixel_hovered)
        # Color used signal will handle color picker integration automatically
        canvas_layout.addWidget(self.canvas, alignment=Qt.AlignmentFlag.AlignCenter)
        
        main_layout.addWidget(canvas_frame, 1)
        
        # Create side panel
        self.create_side_panel(main_layout)
        
        # Create toolbar
        self.create_toolbar()
        
        # Create status bar
        self.statusBar().showMessage("Ready")
    
    def create_toolbar(self) -> None:
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
        
        toolbar.addSeparator()
        
        # Color display in toolbar
        color_widget = QWidget()
        color_layout = QHBoxLayout(color_widget)
        color_layout.setContentsMargins(5, 0, 5, 0)
        
        # Current color display (larger)
        self.toolbar_current_color = QLabel()
        self.toolbar_current_color.setFixedSize(32, 24)
        self.toolbar_current_color.setStyleSheet(f"background-color: {self.current_color.name().upper()}; border: 1px solid #CCCCCC;")
        self.toolbar_current_color.setToolTip("Current Color")
        color_layout.addWidget(self.toolbar_current_color)
        
        # Background color display (smaller, overlapped)
        self.toolbar_bg_color = QLabel()
        self.toolbar_bg_color.setFixedSize(20, 16)
        self.toolbar_bg_color.setStyleSheet(f"background-color: {AppConstants.DEFAULT_BG_COLOR}; border: 1px solid #CCCCCC;")
        self.toolbar_bg_color.setToolTip("Background Color")
        color_layout.addWidget(self.toolbar_bg_color)
        
        toolbar.addWidget(color_widget)
    
    def create_side_panel(self, main_layout) -> None:
        """Create the side panel with tools and options."""
        side_panel = QWidget()
        side_panel.setMaximumWidth(AppConstants.SIDE_PANEL_WIDTH)
        side_layout = QVBoxLayout(side_panel)
        
        # Tools group
        tools_group = QGroupBox("Tools")
        tools_layout = QVBoxLayout(tools_group)
        
        # Create tool buttons dynamically from tool manager
        self.tool_buttons = {}
        tool_configs = {
            "brush": {"icon": "icons/paint-brush.svg", "tooltip": "Brush Tool (B)", "checked": True},
            "fill": {"icon": "icons/paint-bucket.svg", "tooltip": "Fill Bucket Tool (F)", "checked": False},
            "eraser": {"icon": "icons/eraser.svg", "tooltip": "Eraser Tool (E)", "checked": False},
            "picker": {"icon": "icons/eyedropper.svg", "tooltip": "Color Picker Tool (I)", "checked": False},
            "pan": {"icon": "icons/hand.svg", "tooltip": "Pan Tool (H)", "checked": False}
        }
        
        for tool_id, config in tool_configs.items():
            btn = QPushButton()
            btn.setIcon(self.create_svg_icon(config["icon"]))
            btn.setIconSize(QSize(AppConstants.ICON_SIZE, AppConstants.ICON_SIZE))
            btn.setCheckable(True)
            btn.setChecked(config["checked"])
            btn.setToolTip(config["tooltip"])
            btn.setFixedSize(AppConstants.ICON_SIZE + 16, AppConstants.ICON_SIZE + 16)
            btn.clicked.connect(partial(self.set_tool, tool_id))
            self.tool_buttons[tool_id] = btn
            tools_layout.addWidget(btn)
        
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
    
    def create_color_panel(self, parent_layout) -> None:
        """Create the color selection panel."""
        color_group = QGroupBox("Color")
        color_layout = QVBoxLayout(color_group)
        
        # Current color display
        self.color_display = QLabel()
        self.color_display.setFixedSize(AppConstants.COLOR_DISPLAY_WIDTH, AppConstants.COLOR_DISPLAY_HEIGHT)
        self.color_display.setStyleSheet(f"background-color: {self.current_color.name().upper()}; border: 1px solid #CCCCCC;")
        color_layout.addWidget(self.color_display, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Color chooser button
        choose_btn = QPushButton("Choose Color")
        choose_btn.clicked.connect(self.choose_color)
        color_layout.addWidget(choose_btn)
        
        # Recent colors in compact grid
        recent_label = QLabel("Recent Colors:")
        recent_label.setFont(QFont("Arial", 8))
        color_layout.addWidget(recent_label)
        
        self.recent_buttons = []
        recent_layout = QGridLayout()
        recent_layout.setSpacing(2)  # Tight spacing for compact look
        
        # Arrange in 3x2 grid
        for i in range(AppConstants.RECENT_COLORS_COUNT):
            btn = ColorButton(self.recent_colors[i])
            btn.clicked.connect(partial(self._on_recent_color_clicked, i))
            self.recent_buttons.append(btn)
            row = i // 3
            col = i % 3
            recent_layout.addWidget(btn, row, col)
        
        color_layout.addLayout(recent_layout)
        
        parent_layout.addWidget(color_group)
    
    def set_tool(self, tool_id: str) -> None:
        """Set the current drawing tool."""
        success = self.canvas.set_current_tool(tool_id)
        if success:
            # Update button states
            for btn_id, btn in self.tool_buttons.items():
                btn.setChecked(btn_id == tool_id)
    
    def set_color(self, color: QColor, add_to_recent: bool = False) -> None:
        """Set the current color and optionally update recent colors."""
        if add_to_recent and color != self.current_color and color not in self.recent_colors:
            self.recent_colors.insert(0, color)
            self.recent_colors = self.recent_colors[:6]
            self.update_recent_colors()
        
        self.current_color = color
        self.canvas.current_color = color
        self.color_display.setStyleSheet(f"background-color: {color.name().upper()}; border: 1px solid #CCCCCC;")
        # Update toolbar color display
        if hasattr(self, 'toolbar_current_color'):
            self.toolbar_current_color.setStyleSheet(f"background-color: {color.name().upper()}; border: 1px solid #CCCCCC;")
    
    def _on_recent_color_clicked(self, index: int, checked: bool = False) -> None:
        """Handle recent color button clicks."""
        if 0 <= index < len(self.recent_colors):
            self.set_color(self.recent_colors[index], add_to_recent=True)
    
    def update_recent_colors(self) -> None:
        """Update recent color buttons."""
        for i, btn in enumerate(self.recent_buttons):
            btn.set_color(self.recent_colors[i])
            btn.clicked.disconnect()
            btn.clicked.connect(partial(self._on_recent_color_clicked, i))
    
    def choose_color(self) -> None:
        """Open color chooser dialog."""
        color = QColorDialog.getColor(self.current_color, self, "Choose Color")
        if color.isValid():
            self.set_color(color, add_to_recent=True)
    
    
    def new_file(self) -> None:
        """Create a new file."""
        if self._model.is_modified:
            reply = QMessageBox.question(self, "New File", "Are you sure? Unsaved changes will be lost.")
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        # Create new model
        self._model = PixelArtModel()
        self.canvas._model = self._model
        self.canvas._tool_manager = ToolManager(self._model)
        
        # Reconnect signals
        self._model.model_loaded.connect(self._on_model_loaded)
        self._model.model_saved.connect(self._on_model_saved)
        
        # Update canvas
        self.canvas._update_widget_size()
        self.canvas.update()
        
        # Update UI
        self.width_spin.setValue(self._model.width)
        self.height_spin.setValue(self._model.height)
        self.setWindowTitle("Pixel Drawing - Retro Game Asset Creator")
    
    def open_file(self) -> None:
        """Open a pixel art file."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Pixel Art File", "", AppConstants.PROJECT_FILE_FILTER)
        
        if file_path:
            self._file_service.load_file(file_path, self._model)
    
    def save_file(self) -> None:
        """Save the current pixel art."""
        if self._model.current_file:
            self._file_service.save_file(self._model.current_file, self._model)
        else:
            self.save_as_file()
    
    def save_as_file(self) -> None:
        """Save with a new filename."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Pixel Art File", "", AppConstants.PROJECT_FILE_FILTER)
        
        if file_path:
            self._file_service.save_file(file_path, self._model)
    
    def export_png(self) -> None:
        """Export as PNG image."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Export as PNG", "", AppConstants.PNG_FILE_FILTER)
        
        if file_path:
            self._file_service.export_png(file_path, self._model)
    
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
    
    def resize_canvas(self) -> None:
        """Resize the canvas with validation."""
        new_width = self.width_spin.value()
        new_height = self.height_spin.value()
        
        try:
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
            
            # Perform resize through model
            self._model.resize(new_width, new_height)
            self.statusBar().showMessage(f"Canvas resized to {new_width}x{new_height}")
            
        except ValidationError as e:
            QMessageBox.warning(self, "Invalid Dimensions", str(e))
            # Reset spinboxes to current canvas size
            self.width_spin.setValue(self._model.width)
            self.height_spin.setValue(self._model.height)
    
    def clear_canvas(self) -> None:
        """Clear the canvas."""
        reply = QMessageBox.question(self, "Clear Canvas", "Are you sure you want to clear the canvas?")
        if reply == QMessageBox.StandardButton.Yes:
            self._model.clear()
    
    # Signal handlers
    def _on_color_used(self, color: QColor) -> None:
        """Handle color usage on canvas."""
        if color != self.current_color and color not in self.recent_colors:
            self.recent_colors.insert(0, color)
            self.recent_colors = self.recent_colors[:AppConstants.RECENT_COLORS_COUNT]
            self.update_recent_colors()
    
    def _on_color_used(self, color: QColor) -> None:
        """Handle color used on canvas (including from color picker)."""
        self.set_color(color, add_to_recent=True)
    
    def _on_tool_changed(self, tool_id: str) -> None:
        """Handle tool changes."""
        self.statusBar().showMessage(f"Tool: {tool_id}")
    
    def _on_pixel_hovered(self, x: int, y: int) -> None:
        """Handle pixel hover events."""
        color = self._model.get_pixel(x, y)
        self.statusBar().showMessage(f"Pixel ({x}, {y}): {color.name().upper()}")
    
    def _on_model_loaded(self) -> None:
        """Handle model loaded."""
        # Update UI to reflect loaded model
        self.width_spin.setValue(self._model.width)
        self.height_spin.setValue(self._model.height)
        
        # Force canvas to update size and redraw
        self.canvas._update_widget_size()
        self.canvas.update()  # Full redraw of entire canvas
    
    def _on_model_saved(self, file_path: str) -> None:
        """Handle model saved."""
        self.setWindowTitle(f"Pixel Drawing - {os.path.basename(file_path)}")
    
    def _on_file_loaded(self, file_path: str) -> None:
        """Handle file loaded successfully."""
        self.statusBar().showMessage(f"Opened: {os.path.basename(file_path)}")
        self.setWindowTitle(f"Pixel Drawing - {os.path.basename(file_path)}")
    
    def _on_file_saved(self, file_path: str) -> None:
        """Handle file saved successfully."""
        self.statusBar().showMessage(f"Saved: {os.path.basename(file_path)}")
        QMessageBox.information(self, "Success", "File saved successfully!")
    
    def _on_file_exported(self, file_path: str) -> None:
        """Handle file exported successfully."""
        self.statusBar().showMessage(f"Exported: {os.path.basename(file_path)}")
        QMessageBox.information(self, "Success", "PNG exported successfully!")
    
    def _on_file_operation_failed(self, operation: str, error_message: str) -> None:
        """Handle file operation failures."""
        QMessageBox.critical(self, f"{operation.title()} Error", error_message)