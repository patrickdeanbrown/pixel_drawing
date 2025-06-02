"""Interactive canvas widget for pixel art drawing and editing."""

from typing import Tuple, Optional
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPoint, QRect, pyqtSignal, QTimer
from PyQt6.QtGui import QPainter, QPen, QColor, QKeyEvent, QFocusEvent, QAccessible

from ..models import PixelArtModel
from ..controllers.tools import ToolManager
from ..constants import AppConstants
from ..exceptions import ValidationError
from ..utils.cursors import CursorManager
from ..utils.dirty_rectangles import DirtyRegionManager
from ..enums import ToolType
from ..accessibility import KeyboardNavigationMixin, CanvasKeyboardNavigation, AccessibilityUtils
from ..accessibility.screen_reader import ScreenReaderSupport
from ..i18n import tr_status


class PixelCanvas(QWidget, KeyboardNavigationMixin):
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
        
        # Initialize accessibility components
        self._screen_reader = ScreenReaderSupport(self)
        self._canvas_navigation = None  # Will be initialized after model setup
        
        # Set up model
        if model is None:
            model = PixelArtModel()
        self._model = model
        
        # Set up tool manager
        self._tool_manager = ToolManager(self._model)
        
        # Set up cursor manager
        self._cursor_manager = CursorManager()
        
        # Connect tool manager signals
        self._tool_manager.tool_changed.connect(self._on_tool_changed)
        
        # Connect model signals
        self._model.pixel_changed.connect(self._on_pixel_changed)
        self._model.canvas_resized.connect(self._on_canvas_resized)
        self._model.canvas_cleared.connect(self._on_canvas_cleared)
        
        # Connect tool signals
        self._connect_tool_signals()
        
        # Update widget size
        self._update_widget_size()
        
        # Enable mouse tracking
        self.setMouseTracking(True)
        
        # Initialize accessibility features
        self._setup_accessibility()
        self._setup_keyboard_navigation()
        
        # Performance optimizations
        self._grid_pen = QPen(QColor(AppConstants.GRID_COLOR), 1)
        self._cached_background = None
        self._last_canvas_size = (0, 0)
        self._update_timer = QTimer()
        self._update_timer.setSingleShot(True)
        self._update_timer.timeout.connect(self._delayed_update)
        self._dirty_region_manager = DirtyRegionManager(pixel_size, AppConstants.DIRTY_RECT_MERGE_THRESHOLD)
    
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
        """Handle pixel changes from model with batched updates."""
        # Add to dirty region manager for optimized updates
        self._dirty_region_manager.mark_pixel_dirty(x, y)
        
        # Start or restart the update timer for smooth batching
        if not self._update_timer.isActive():
            self._update_timer.start(AppConstants.UPDATE_TIMER_INTERVAL)
    
    def _delayed_update(self) -> None:
        """Process batched pixel updates for better performance."""
        # Get optimized update rectangles from dirty region manager
        update_rects = self._dirty_region_manager.get_update_rectangles()
        
        # Update each optimized region
        for rect in update_rects:
            self.update(rect)
    
    def _on_canvas_resized(self, new_width: int, new_height: int) -> None:
        """Handle canvas resize from model."""
        self._update_widget_size()
        self.update()
        
        # Update accessibility description
        self.setAccessibleDescription(tr_status("canvas_description", 
                                               width=new_width, 
                                               height=new_height))
        
        # Update keyboard navigation bounds
        if self._canvas_navigation:
            self._canvas_navigation.set_canvas_dimensions(new_width, new_height)
    
    def _on_canvas_cleared(self) -> None:
        """Handle canvas clear from model."""
        self.update()
    
    def paintEvent(self, event) -> None:
        """Paint the pixel grid with performance optimizations.
        
        Uses dirty region tracking and cached pen objects for optimal
        rendering performance, especially on large canvases.
        """
        import time
        start_time = time.time()
        
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
        
        # Log rendering performance
        duration_ms = (time.time() - start_time) * 1000
        pixel_count = (end_x - start_x) * (end_y - start_y)
        update_size = f"{update_rect.width()}x{update_rect.height()}"
        
        from ..utils.logging import log_performance
        if duration_ms > 10:  # Only log slow renders
            log_performance("canvas_render", duration_ms, f"Region: {update_size}, Pixels: {pixel_count}, Zoom: {self.pixel_size}x")
    
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
            self._update_cursor_for_tool(tool_id)
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
            
            # Log coordinate transformation for debugging
            from ..utils.logging import log_debug
            log_debug("canvas", f"Mouse press: screen({event.pos().x()},{event.pos().y()}) -> pixel({pixel_x},{pixel_y}) [pixel_size={self.pixel_size}]")
            
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
                old_pixel_size = self.pixel_size
                self.pixel_size = new_pixel_size
                
                # Update dirty region manager with new pixel size
                self._dirty_region_manager = DirtyRegionManager(
                    new_pixel_size, 
                    AppConstants.DIRTY_RECT_MERGE_THRESHOLD
                )
                
                self._update_widget_size()
                self.update()
                
                # Log zoom operation for debugging
                from ..utils.logging import log_canvas_event
                log_canvas_event("zoom", f"Pixel size changed: {old_pixel_size} -> {new_pixel_size}")
                
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
    
    def _on_tool_changed(self, tool_id: str) -> None:
        """Handle tool changes from tool manager."""
        self._update_cursor_for_tool(tool_id)
        self.tool_changed.emit(tool_id)
    
    def _update_cursor_for_tool(self, tool_id: str) -> None:
        """Update cursor based on current tool."""
        current_tool = self._tool_manager.current_tool
        if current_tool:
            # Try to get custom cursor from icon first
            icon_path = current_tool.icon_path
            if icon_path:
                cursor = self._cursor_manager.get_cursor(tool_id, icon_path)
            else:
                cursor = current_tool.cursor
            self.setCursor(cursor)
    
    def _connect_tool_signals(self) -> None:
        """Connect signals from individual tools."""
        # Color picker signal
        color_picker = self._tool_manager.get_tool("picker")
        if color_picker and hasattr(color_picker, 'signals'):
            color_picker.signals.color_picked.connect(self._on_color_picked)
        
        # Pan tool signal
        pan_tool = self._tool_manager.get_tool("pan")
        if pan_tool and hasattr(pan_tool, 'signals'):
            pan_tool.signals.pan_requested.connect(self._on_pan_requested)
    
    def _on_color_picked(self, color: QColor) -> None:
        """Handle color picked from canvas."""
        self.current_color = color
        self.color_used.emit(color)
    
    def _on_pan_requested(self, delta_x: int, delta_y: int) -> None:
        """Handle pan request from pan tool."""
        # For now, we'll emit this as a signal for the parent to handle
        # In a full implementation, this would interact with scroll areas
        parent = self.parent()
        if hasattr(parent, 'handle_pan_request'):
            parent.handle_pan_request(delta_x, delta_y)
    
    def _setup_accessibility(self) -> None:
        """Set up accessibility features for the canvas."""
        # Set accessibility properties
        self.setAccessibleName(tr_status("drawing_canvas"))
        self.setAccessibleDescription(tr_status("canvas_description", 
                                               width=self._model.width, 
                                               height=self._model.height))
        
        # Enable focus for keyboard navigation
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Set up screen reader announcements
        self._screen_reader.announcement_requested.connect(self._on_accessibility_announcement)
    
    def _setup_keyboard_navigation(self) -> None:
        """Set up keyboard navigation for the canvas."""
        # Initialize canvas keyboard navigation
        self._canvas_navigation = CanvasKeyboardNavigation(
            self._model.width, 
            self._model.height, 
            self
        )
        
        # Connect navigation signals
        self._canvas_navigation.cursor_moved.connect(self._on_keyboard_cursor_moved)
        self._canvas_navigation.pixel_activated.connect(self._on_keyboard_pixel_activated)
        self._canvas_navigation.navigation_announced.connect(self._screen_reader.announce)
        
        # Enable keyboard navigation on the mixin
        self.enable_keyboard_navigation(
            cursor_moved_callback=self._on_cursor_moved_callback,
            action_callback=self._on_action_callback
        )
    
    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle keyboard events for accessibility and navigation."""
        # Handle tool shortcuts first
        if self._canvas_navigation and self._canvas_navigation.handle_tool_shortcut(event.text()):
            tool_name = self._canvas_navigation._current_tool
            self.set_current_tool(tool_name)
            event.accept()
            return
        
        # Handle navigation keys
        if self.handle_keyboard_navigation(event):
            event.accept()
            return
        
        # Handle escape to exit keyboard navigation mode
        if event.key() == Qt.Key.Key_Escape:
            self.clearFocus()
            self._screen_reader.announce("Exited drawing mode", "normal")
            event.accept()
            return
        
        # Pass to parent for other keys
        super().keyPressEvent(event)
    
    def focusInEvent(self, event: QFocusEvent) -> None:
        """Handle focus in events for accessibility."""
        super().focusInEvent(event)
        
        # Announce canvas focus
        x, y = self.get_keyboard_cursor_position()
        color_name = AccessibilityUtils.get_color_name(self._model.get_pixel(x, y))
        tool_name = self.get_current_tool_id() or "brush"
        
        self._screen_reader.announce_canvas_state(x, y, color_name, tool_name)
        
        # Announce keyboard instructions
        instructions = tr_status("canvas_keyboard_instructions")
        self._screen_reader.announce(instructions, "low")
    
    def focusOutEvent(self, event: QFocusEvent) -> None:
        """Handle focus out events."""
        super().focusOutEvent(event)
    
    def _on_cursor_moved_callback(self, x: int, y: int) -> None:
        """Callback for keyboard cursor movement."""
        if self._canvas_navigation:
            self._canvas_navigation.set_keyboard_cursor_position(x, y)
    
    def _on_action_callback(self, x: int, y: int) -> None:
        """Callback for keyboard action (drawing)."""
        if 0 <= x < self._model.width and 0 <= y < self._model.height:
            # Perform drawing action at keyboard cursor position
            self._tool_manager.handle_press(x, y, self.current_color)
            self._tool_manager.handle_release(x, y, self.current_color)
    
    def _on_keyboard_cursor_moved(self, x: int, y: int) -> None:
        """Handle keyboard cursor movement."""
        # Update visual cursor indicator if needed
        self.update()
        
        # Emit hover signal for status updates
        self.pixel_hovered.emit(x, y)
    
    def _on_keyboard_pixel_activated(self, x: int, y: int) -> None:
        """Handle pixel activation via keyboard."""
        if 0 <= x < self._model.width and 0 <= y < self._model.height:
            # Perform drawing action
            self._tool_manager.handle_press(x, y, self.current_color)
            self._tool_manager.handle_release(x, y, self.current_color)
    
    def _on_accessibility_announcement(self, message: str) -> None:
        """Handle accessibility announcements."""
        # Could be used to display visual announcements for hearing-impaired users
        pass