"""Main application window for the Pixel Drawing application."""

import os
from functools import partial
from typing import Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QGroupBox, QSpinBox, QFileDialog, QMessageBox,
    QColorDialog, QToolBar, QScrollArea
)
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QRect, QTimer
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
from ..views.dialogs.preferences_dialog import PreferencesDialog
from ..utils.shortcuts import setup_keyboard_shortcuts
from ..utils.icon_cache import get_cached_icon, preload_app_icons
from ..utils.icon_effects import get_tool_icon
from ..utils.logging import log_info, log_debug
from ..enums import ToolType
from ..i18n import tr_window, tr_toolbar, tr_panel, tr_dialog, tr_status, tr_filter, tr_tool
from ..styles import (
    ModernDesignConstants, 
    apply_tool_button_style, 
    apply_primary_button_style,
    apply_secondary_button_style,
    apply_danger_button_style
)


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
        self.setWindowTitle(tr_window("app_title"))
        self.setMinimumSize(AppConstants.MIN_WINDOW_WIDTH, AppConstants.MIN_WINDOW_HEIGHT)
        
        # Set up keyboard shortcuts using utility function
        setup_keyboard_shortcuts(self)
        
        # Modern styling will be applied by style manager
    
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
        
        # Create canvas area with scroll capability
        self.scroll_area = QScrollArea()
        self.scroll_area.setFrameStyle(QFrame.Shape.StyledPanel)
        self.scroll_area.setWidgetResizable(False)  # Fixed size for pixel perfect rendering
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.canvas = PixelCanvas(self, self._model, AppConstants.DEFAULT_PIXEL_SIZE)
        # Connect canvas signals for decoupled communication
        self.canvas.color_used.connect(self._on_color_used)
        self.canvas.tool_changed.connect(self._on_tool_changed)
        self.canvas.pixel_hovered.connect(self._on_pixel_hovered)
        # Color used signal will handle color picker integration automatically
        
        self.scroll_area.setWidget(self.canvas)
        main_layout.addWidget(self.scroll_area, 1)
        
        # Create side panel
        self.create_side_panel(main_layout)
        
        # Create menu bar and toolbar  
        self.create_menu_bar()
        self.create_toolbar()
        
        # Create status bar
        self.statusBar().showMessage(AppConstants.STATUS_READY)
        
        # Preload icons for better performance
        preload_app_icons()

    def create_menu_bar(self) -> None:
        """Create the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu(tr_panel("file_menu"))
        
        # Add existing actions to file menu
        new_action = file_menu.addAction(tr_toolbar("new"))
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file)
        
        open_action = file_menu.addAction(tr_toolbar("open"))
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        
        file_menu.addSeparator()
        
        save_action = file_menu.addAction(tr_toolbar("save"))
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        
        save_as_action = file_menu.addAction(tr_toolbar("save_as"))
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_as_file)
        
        file_menu.addSeparator()
        
        export_action = file_menu.addAction(tr_toolbar("export_png"))
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_png)
        
        file_menu.addSeparator()
        
        quit_action = file_menu.addAction(tr_panel("quit"))
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        
        # Edit menu
        edit_menu = menubar.addMenu(tr_panel("edit_menu"))
        
        undo_action = edit_menu.addAction(tr_toolbar("undo"))
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.undo)
        
        redo_action = edit_menu.addAction(tr_toolbar("redo"))
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self.redo)
        
        edit_menu.addSeparator()
        
        clear_action = edit_menu.addAction(tr_panel("clear_canvas"))
        clear_action.setShortcut("Ctrl+Del")
        clear_action.triggered.connect(self.clear_canvas)
        
        # Settings menu
        settings_menu = menubar.addMenu(tr_panel("settings_menu"))
        
        preferences_action = settings_menu.addAction(tr_panel("preferences"))
        preferences_action.setShortcut("Ctrl+,")
        preferences_action.triggered.connect(self.show_preferences)
    
    def create_toolbar(self) -> None:
        """Create the toolbar."""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # File actions
        new_action = QAction(tr_toolbar("new"), self)
        new_action.triggered.connect(self.new_file)
        toolbar.addAction(new_action)
        
        open_action = QAction(tr_toolbar("open"), self)
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)
        
        save_action = QAction(tr_toolbar("save"), self)
        save_action.triggered.connect(self.save_file)
        toolbar.addAction(save_action)
        
        save_as_action = QAction(tr_toolbar("save_as"), self)
        save_as_action.triggered.connect(self.save_as_file)
        toolbar.addAction(save_as_action)
        
        toolbar.addSeparator()
        
        export_action = QAction(tr_toolbar("export_png"), self)
        export_action.triggered.connect(self.export_png)
        toolbar.addAction(export_action)
        
        toolbar.addSeparator()
        
        # Undo/Redo actions
        undo_action = QAction(tr_toolbar("undo"), self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.undo)
        toolbar.addAction(undo_action)
        
        redo_action = QAction(tr_toolbar("redo"), self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self.redo)
        toolbar.addAction(redo_action)
        
        toolbar.addSeparator()
        
        # Color display in toolbar
        color_widget = QWidget()
        color_layout = QHBoxLayout(color_widget)
        color_layout.setContentsMargins(5, 0, 5, 0)
        
        # Current color display (larger, clickable)
        self.toolbar_current_color = QPushButton()
        self.toolbar_current_color.setFixedSize(AppConstants.TOOLBAR_COLOR_BUTTON_WIDTH, AppConstants.TOOLBAR_COLOR_BUTTON_HEIGHT)
        self.toolbar_current_color.setStyleSheet(f"background-color: {self.current_color.name().upper()}; border: 1px solid #CCCCCC;")
        self.toolbar_current_color.setToolTip(tr_panel("current_color_tooltip"))
        self.toolbar_current_color.clicked.connect(self.choose_color)
        color_layout.addWidget(self.toolbar_current_color)
        
        # Background color display (smaller, informational)
        self.toolbar_bg_color = QLabel()
        self.toolbar_bg_color.setFixedSize(AppConstants.TOOLBAR_BG_COLOR_WIDTH, AppConstants.TOOLBAR_BG_COLOR_HEIGHT)
        self.toolbar_bg_color.setStyleSheet(f"background-color: {AppConstants.DEFAULT_BG_COLOR}; border: 1px solid #CCCCCC;")
        self.toolbar_bg_color.setToolTip(tr_panel("background_color_tooltip"))
        color_layout.addWidget(self.toolbar_bg_color)
        
        toolbar.addWidget(color_widget)
    
    def create_side_panel(self, main_layout) -> None:
        """Create the modern unified side panel with tools and options."""
        side_panel = QWidget()
        side_panel.setObjectName("sidePanel")
        side_panel.setFixedWidth(ModernDesignConstants.SIDE_PANEL_WIDTH)
        side_layout = QVBoxLayout(side_panel)
        side_layout.setSpacing(ModernDesignConstants.SPACING_LG)
        side_layout.setContentsMargins(
            ModernDesignConstants.SPACING_MD,
            ModernDesignConstants.SPACING_LG, 
            ModernDesignConstants.SPACING_MD,
            ModernDesignConstants.SPACING_LG
        )
        
        # Tools section
        tools_group = QGroupBox(tr_panel("tools_group"))
        tools_layout = QGridLayout(tools_group)  # Changed to grid layout
        tools_layout.setSpacing(ModernDesignConstants.TOOL_GRID_SPACING)
        
        # Create tool buttons dynamically from tool manager
        self.tool_buttons = {}
        tool_configs = {
            ToolType.BRUSH.value: {"icon": AppConstants.ICON_BRUSH, "tooltip": tr_tool("brush_tooltip"), "checked": True},
            ToolType.FILL.value: {"icon": AppConstants.ICON_FILL, "tooltip": tr_tool("fill_tooltip"), "checked": False},
            ToolType.ERASER.value: {"icon": AppConstants.ICON_ERASER, "tooltip": tr_tool("eraser_tooltip"), "checked": False},
            ToolType.COLOR_PICKER.value: {"icon": AppConstants.ICON_COLOR_PICKER, "tooltip": tr_tool("color_picker_tooltip"), "checked": False},
            ToolType.PAN.value: {"icon": AppConstants.ICON_PAN, "tooltip": tr_tool("pan_tooltip"), "checked": False}
        }
        
        row, col = 0, 0
        for tool_id, config in tool_configs.items():
            btn = QPushButton()
            
            # Apply modern tool button styling
            apply_tool_button_style(btn)
            
            icon = get_tool_icon(config["icon"], ModernDesignConstants.ICON_SIZE_TOOL)
            if icon:
                btn.setIcon(icon)
                log_debug("ui", f"Created tool button for {tool_id} with modern styling")
            
            btn.setIconSize(QSize(ModernDesignConstants.ICON_SIZE_TOOL, ModernDesignConstants.ICON_SIZE_TOOL))
            btn.setCheckable(True)
            btn.setChecked(config["checked"])
            btn.setToolTip(config["tooltip"])
            btn.setFixedSize(ModernDesignConstants.TOOL_BUTTON_SIZE, ModernDesignConstants.TOOL_BUTTON_SIZE)
            btn.clicked.connect(partial(self.set_tool, tool_id))
            
            self.tool_buttons[tool_id] = btn
            tools_layout.addWidget(btn, row, col)
            
            # Arrange in 2-column grid
            col += 1
            if col >= ModernDesignConstants.TOOL_GRID_COLUMNS:
                col = 0
                row += 1
        
        side_layout.addWidget(tools_group)
        
        # Color group
        self.create_color_panel(side_layout)
        
        # Canvas size group
        size_group = QGroupBox(tr_panel("canvas_size_group"))
        size_layout = QVBoxLayout(size_group)
        size_layout.setSpacing(ModernDesignConstants.SPACING_MD)
        
        # Width control
        width_layout = QHBoxLayout()
        width_label = QLabel(tr_panel("width_label"))
        width_label.setStyleSheet(f"color: {ModernDesignConstants.TEXT_PRIMARY}; font-weight: {ModernDesignConstants.FONT_WEIGHT_MEDIUM};")
        width_layout.addWidget(width_label)
        
        self.width_spin = QSpinBox()
        self.width_spin.setRange(AppConstants.MIN_CANVAS_SIZE, AppConstants.MAX_CANVAS_SIZE)
        self.width_spin.setValue(AppConstants.DEFAULT_CANVAS_WIDTH)
        self.width_spin.setFixedWidth(ModernDesignConstants.SPINBOX_WIDTH)
        width_layout.addWidget(self.width_spin)
        width_layout.addStretch()
        size_layout.addLayout(width_layout)
        
        # Height control
        height_layout = QHBoxLayout()
        height_label = QLabel(tr_panel("height_label"))
        height_label.setStyleSheet(f"color: {ModernDesignConstants.TEXT_PRIMARY}; font-weight: {ModernDesignConstants.FONT_WEIGHT_MEDIUM};")
        height_layout.addWidget(height_label)
        
        self.height_spin = QSpinBox()
        self.height_spin.setRange(AppConstants.MIN_CANVAS_SIZE, AppConstants.MAX_CANVAS_SIZE)
        self.height_spin.setValue(AppConstants.DEFAULT_CANVAS_HEIGHT)
        self.height_spin.setFixedWidth(ModernDesignConstants.SPINBOX_WIDTH)
        height_layout.addWidget(self.height_spin)
        height_layout.addStretch()
        size_layout.addLayout(height_layout)
        
        # Resize button
        resize_btn = QPushButton(tr_panel("resize_canvas"))
        resize_btn.setObjectName("resizeCanvasButton")
        apply_primary_button_style(resize_btn)
        resize_btn.clicked.connect(self.resize_canvas)
        size_layout.addWidget(resize_btn)
        
        side_layout.addWidget(size_group)
        
        # Actions group
        actions_group = QGroupBox(tr_panel("actions_group"))
        actions_layout = QVBoxLayout(actions_group)
        actions_layout.setSpacing(ModernDesignConstants.SPACING_MD)
        
        clear_btn = QPushButton(tr_panel("clear_canvas"))
        clear_btn.setObjectName("clearCanvasButton")
        apply_danger_button_style(clear_btn)
        clear_btn.clicked.connect(self.clear_canvas)
        actions_layout.addWidget(clear_btn)
        
        side_layout.addWidget(actions_group)
        
        side_layout.addStretch()
        main_layout.addWidget(side_panel)
    
    def create_color_panel(self, parent_layout) -> None:
        """Create the modern color selection panel."""
        color_group = QGroupBox(tr_panel("color_group"))
        color_layout = QVBoxLayout(color_group)
        color_layout.setSpacing(ModernDesignConstants.SPACING_MD)
        
        # Large current color display - clickable
        self.color_display = QPushButton()
        self.color_display.setObjectName("largeColorDisplay")
        self.color_display.setFixedSize(
            ModernDesignConstants.LARGE_COLOR_DISPLAY_SIZE, 
            ModernDesignConstants.LARGE_COLOR_DISPLAY_SIZE
        )
        self.color_display.setStyleSheet(
            f"""
            QPushButton#largeColorDisplay {{
                background-color: {self.current_color.name().upper()};
                border: 2px solid {ModernDesignConstants.BORDER_LIGHT};
                border-radius: {ModernDesignConstants.RADIUS_MEDIUM}px;
            }}
            QPushButton#largeColorDisplay:hover {{
                border-color: {ModernDesignConstants.PRIMARY_PURPLE};
                box-shadow: 0 2px 6px rgba(160, 32, 240, 0.2);
            }}
            """
        )
        self.color_display.setToolTip(tr_panel("current_color_tooltip"))
        self.color_display.clicked.connect(self.choose_color)
        color_layout.addWidget(self.color_display, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Color chooser button
        choose_btn = QPushButton(tr_panel("choose_color"))
        apply_secondary_button_style(choose_btn)
        choose_btn.clicked.connect(self.choose_color)
        color_layout.addWidget(choose_btn)
        
        # Recent colors section
        recent_label = QLabel(tr_panel("recent_colors"))
        recent_label.setObjectName("sectionSubtitle")
        recent_label.setStyleSheet(f"color: {ModernDesignConstants.TEXT_SECONDARY}; font-size: {ModernDesignConstants.FONT_SIZE_SMALL}px;")
        color_layout.addWidget(recent_label)
        
        # Recent colors in modern grid
        self.recent_buttons = []
        recent_layout = QGridLayout()
        recent_layout.setSpacing(ModernDesignConstants.COLOR_GRID_SPACING)
        
        # Arrange in 3x2 grid with modern styling
        for i in range(ModernDesignConstants.RECENT_COLORS_COUNT):
            btn = ColorButton(self.recent_colors[i])
            btn.setFixedSize(ModernDesignConstants.COLOR_SWATCH_SIZE, ModernDesignConstants.COLOR_SWATCH_SIZE)
            btn.setStyleSheet(
                f"""
                QPushButton {{
                    border: 2px solid {ModernDesignConstants.BORDER_LIGHT};
                    border-radius: {ModernDesignConstants.RADIUS_SMALL}px;
                }}
                QPushButton:hover {{
                    border-color: {ModernDesignConstants.PRIMARY_PURPLE};
                    box-shadow: 0 2px 4px rgba(160, 32, 240, 0.2);
                }}
                """
            )
            btn.clicked.connect(partial(self._on_recent_color_clicked, i))
            self.recent_buttons.append(btn)
            
            row = i // ModernDesignConstants.COLOR_GRID_COLUMNS
            col = i % ModernDesignConstants.COLOR_GRID_COLUMNS
            recent_layout.addWidget(btn, row, col)
        
        # Add recent colors container
        recent_container = QWidget()
        recent_container.setObjectName("recentColorsGrid")
        recent_container.setLayout(recent_layout)
        color_layout.addWidget(recent_container)
        
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
        
        # Update main color display with modern styling
        self.color_display.setStyleSheet(
            f"""
            QPushButton#largeColorDisplay {{
                background-color: {color.name().upper()};
                border: 2px solid {ModernDesignConstants.BORDER_LIGHT};
                border-radius: {ModernDesignConstants.RADIUS_MEDIUM}px;
            }}
            QPushButton#largeColorDisplay:hover {{
                border-color: {ModernDesignConstants.PRIMARY_PURPLE};
                box-shadow: 0 2px 6px rgba(160, 32, 240, 0.2);
            }}
            """
        )
        
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
        color = QColorDialog.getColor(self.current_color, self, tr_dialog("choose_color_title"))
        if color.isValid():
            self.set_color(color, add_to_recent=True)
    
    
    def new_file(self) -> None:
        """Create a new file."""
        if self._model.is_modified:
            reply = QMessageBox.question(self, tr_dialog("new_file_title"), tr_dialog("new_file_message"))
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
        self.setWindowTitle(tr_window("app_title"))
    
    def open_file(self) -> None:
        """Open a pixel art file."""
        file_path, _ = QFileDialog.getOpenFileName(self, tr_dialog("open_file_title"), "", tr_filter(AppConstants.PROJECT_FILE_FILTER))
        
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
        file_path, _ = QFileDialog.getSaveFileName(self, tr_dialog("save_file_title"), "", tr_filter(AppConstants.PROJECT_FILE_FILTER))
        
        if file_path:
            self._file_service.save_file(file_path, self._model)
    
    def export_png(self) -> None:
        """Export as PNG image."""
        file_path, _ = QFileDialog.getSaveFileName(self, tr_dialog("export_png_title"), "", tr_filter(AppConstants.PNG_FILE_FILTER))
        
        if file_path:
            self._file_service.export_png(file_path, self._model)
    
    
    def resize_canvas(self) -> None:
        """Resize the canvas with validation."""
        new_width = self.width_spin.value()
        new_height = self.height_spin.value()
        
        try:
            # Warn about large canvases
            if new_width > AppConstants.LARGE_CANVAS_THRESHOLD or new_height > AppConstants.LARGE_CANVAS_THRESHOLD:
                reply = QMessageBox.question(
                    self, 
                    tr_dialog("large_canvas_title"), 
                    tr_dialog("large_canvas_message", width=new_width, height=new_height),
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return
            
            # Perform resize through model
            self._model.resize(new_width, new_height)
            self.statusBar().showMessage(tr_status("canvas_resized", width=new_width, height=new_height))
            
        except ValidationError as e:
            from ..utils.logging import log_warning
            log_warning("ui", f"Canvas resize validation failed: {str(e)}")
            QMessageBox.warning(self, tr_dialog("invalid_dimensions_title"), str(e))
            # Reset spinboxes to current canvas size
            self.width_spin.setValue(self._model.width)
            self.height_spin.setValue(self._model.height)
    
    def clear_canvas(self) -> None:
        """Clear the canvas."""
        reply = QMessageBox.question(self, tr_dialog("clear_canvas_title"), tr_dialog("clear_canvas_message"))
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
        self.statusBar().showMessage(tr_status("tool_changed", tool_id=tool_id))
    
    def _on_pixel_hovered(self, x: int, y: int) -> None:
        """Handle pixel hover events."""
        color = self._model.get_pixel(x, y)
        self.statusBar().showMessage(tr_status("pixel_info", x=x, y=y, color=color.name().upper()))
    
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
        self.setWindowTitle(tr_window("app_with_file", filename=os.path.basename(file_path)))
    
    def _on_file_loaded(self, file_path: str) -> None:
        """Handle file loaded successfully."""
        self.statusBar().showMessage(tr_status("file_opened", filename=os.path.basename(file_path)))
        self.setWindowTitle(tr_window("app_with_file", filename=os.path.basename(file_path)))
    
    def _on_file_saved(self, file_path: str) -> None:
        """Handle file saved successfully."""
        self.statusBar().showMessage(tr_status("file_saved", filename=os.path.basename(file_path)))
        QMessageBox.information(self, tr_dialog("success_title"), tr_dialog("file_saved_message"))
    
    def _on_file_exported(self, file_path: str) -> None:
        """Handle file exported successfully."""
        self.statusBar().showMessage(tr_status("file_exported", filename=os.path.basename(file_path)))
        QMessageBox.information(self, tr_dialog("success_title"), tr_dialog("png_exported_message"))
    
    def _on_file_operation_failed(self, operation: str, error_message: str) -> None:
        """Handle file operation failures."""
        from ..utils.logging import log_error
        log_error("ui", f"File operation failed - {operation}: {error_message}")
        QMessageBox.critical(self, tr_dialog("error_title_template", operation=operation.title()), error_message)
    
    def show_preferences(self) -> None:
        """Show the preferences dialog."""
        dialog = PreferencesDialog(self)
        dialog.settings_changed.connect(self._on_settings_changed)
        dialog.language_changed.connect(self._on_language_preview)
        dialog.exec()
    
    def _on_settings_changed(self, settings: dict) -> None:
        """Handle settings changes from preferences dialog.
        
        Args:
            settings: Dictionary of changed settings
        """
        # Handle any settings that need immediate application
        # (language is already handled in the preferences dialog)
        log_info("ui", f"Settings changed: {settings}")
    
    def _on_language_preview(self, language_code: str) -> None:
        """Handle language preview changes.
        
        Args:
            language_code: Language code for preview
        """
        # This could be used for live preview in the future
        log_debug("ui", f"Language preview: {language_code}")
    
    def handle_pan_request(self, delta_x: int, delta_y: int) -> None:
        """Handle pan requests from canvas.
        
        Args:
            delta_x: Horizontal movement in pixels
            delta_y: Vertical movement in pixels
        """
        # Get current scroll positions
        h_scroll = self.scroll_area.horizontalScrollBar()
        v_scroll = self.scroll_area.verticalScrollBar()
        
        # Calculate new positions (invert delta for natural panning)
        new_h = h_scroll.value() - delta_x * self.canvas.pixel_size
        new_v = v_scroll.value() - delta_y * self.canvas.pixel_size
        
        # Apply new scroll positions
        h_scroll.setValue(new_h)
        v_scroll.setValue(new_v)
    
    
    def undo(self) -> None:
        """Undo the last operation."""
        if self._model.undo():
            self.statusBar().showMessage(AppConstants.STATUS_UNDONE, 2000)
    
    def redo(self) -> None:
        """Redo the last undone operation."""
        if self._model.redo():
            self.statusBar().showMessage(AppConstants.STATUS_REDONE, 2000)