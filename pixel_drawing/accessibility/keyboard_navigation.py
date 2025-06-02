"""Keyboard navigation enhancements for accessibility."""

from typing import Optional, Tuple, Callable
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QObject
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWidgets import QWidget

from ..constants import AppConstants
from ..i18n import tr_status


class KeyboardNavigationMixin:
    """Mixin class to add keyboard navigation capabilities to widgets."""
    
    def __init__(self):
        """Initialize keyboard navigation."""
        self._keyboard_cursor_pos = QPoint(0, 0)
        self._keyboard_navigation_enabled = True
        self._cursor_moved_callback: Optional[Callable[[int, int], None]] = None
        self._action_callback: Optional[Callable[[int, int], None]] = None
        
    def enable_keyboard_navigation(self, 
                                 cursor_moved_callback: Optional[Callable[[int, int], None]] = None,
                                 action_callback: Optional[Callable[[int, int], None]] = None) -> None:
        """Enable keyboard navigation with callbacks.
        
        Args:
            cursor_moved_callback: Called when cursor position changes
            action_callback: Called when action key (Space/Enter) is pressed
        """
        self._keyboard_navigation_enabled = True
        self._cursor_moved_callback = cursor_moved_callback
        self._action_callback = action_callback
        
        # Ensure widget can receive focus
        if hasattr(self, 'setFocusPolicy'):
            self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            
    def disable_keyboard_navigation(self) -> None:
        """Disable keyboard navigation."""
        self._keyboard_navigation_enabled = False
        
    def set_keyboard_cursor_position(self, x: int, y: int) -> None:
        """Set the keyboard cursor position.
        
        Args:
            x: X coordinate
            y: Y coordinate
        """
        self._keyboard_cursor_pos = QPoint(x, y)
        if self._cursor_moved_callback:
            self._cursor_moved_callback(x, y)
            
    def get_keyboard_cursor_position(self) -> Tuple[int, int]:
        """Get current keyboard cursor position.
        
        Returns:
            Tuple of (x, y) coordinates
        """
        return (self._keyboard_cursor_pos.x(), self._keyboard_cursor_pos.y())
    
    def handle_keyboard_navigation(self, event: QKeyEvent) -> bool:
        """Handle keyboard navigation events.
        
        Args:
            event: Key event
            
        Returns:
            True if event was handled, False otherwise
        """
        if not self._keyboard_navigation_enabled:
            return False
            
        key = event.key()
        
        # Arrow key navigation
        if key in [Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_Left, Qt.Key.Key_Right]:
            return self._handle_arrow_navigation(key, event.modifiers())
            
        # Action keys
        elif key in [Qt.Key.Key_Space, Qt.Key.Key_Return, Qt.Key.Key_Enter]:
            return self._handle_action_key()
            
        # Home/End for quick navigation
        elif key == Qt.Key.Key_Home:
            return self._handle_home_key()
        elif key == Qt.Key.Key_End:
            return self._handle_end_key()
            
        return False
    
    def _handle_arrow_navigation(self, key: Qt.Key, modifiers: Qt.KeyboardModifier) -> bool:
        """Handle arrow key navigation.
        
        Args:
            key: Arrow key pressed
            modifiers: Key modifiers
            
        Returns:
            True if handled
        """
        x, y = self.get_keyboard_cursor_position()
        
        # Calculate step size (larger with Ctrl modifier)
        step = 5 if modifiers & Qt.KeyboardModifier.ControlModifier else 1
        
        # Calculate new position
        if key == Qt.Key.Key_Up:
            y = max(0, y - step)
        elif key == Qt.Key.Key_Down:
            y = y + step  # Bounds checking handled by implementation
        elif key == Qt.Key.Key_Left:
            x = max(0, x - step)
        elif key == Qt.Key.Key_Right:
            x = x + step  # Bounds checking handled by implementation
            
        self.set_keyboard_cursor_position(x, y)
        return True
    
    def _handle_action_key(self) -> bool:
        """Handle action key press (Space/Enter).
        
        Returns:
            True if handled
        """
        if self._action_callback:
            x, y = self.get_keyboard_cursor_position()
            self._action_callback(x, y)
            return True
        return False
    
    def _handle_home_key(self) -> bool:
        """Handle Home key (go to top-left).
        
        Returns:
            True if handled
        """
        self.set_keyboard_cursor_position(0, 0)
        return True
    
    def _handle_end_key(self) -> bool:
        """Handle End key (go to bottom-right).
        
        Returns:
            True if handled  
        """
        # Implementation should override this with actual bounds
        return True


class CanvasKeyboardNavigation(QObject, KeyboardNavigationMixin):
    """Keyboard navigation specifically for the drawing canvas."""
    
    # Signals for navigation events
    cursor_moved = pyqtSignal(int, int)  # x, y
    pixel_activated = pyqtSignal(int, int)  # x, y
    navigation_announced = pyqtSignal(str)  # message
    
    def __init__(self, canvas_width: int, canvas_height: int, parent=None):
        """Initialize canvas keyboard navigation.
        
        Args:
            canvas_width: Canvas width in pixels
            canvas_height: Canvas height in pixels
            parent: Parent object
        """
        QObject.__init__(self, parent)
        KeyboardNavigationMixin.__init__(self)
        
        self._canvas_width = canvas_width
        self._canvas_height = canvas_height
        self._current_tool = "brush"
        
        # Connect internal callbacks
        self.enable_keyboard_navigation(
            cursor_moved_callback=self._on_cursor_moved,
            action_callback=self._on_pixel_activated
        )
    
    def set_canvas_dimensions(self, width: int, height: int) -> None:
        """Update canvas dimensions.
        
        Args:
            width: New canvas width
            height: New canvas height
        """
        self._canvas_width = width
        self._canvas_height = height
        
        # Clamp current position to new bounds
        x, y = self.get_keyboard_cursor_position()
        x = min(x, width - 1)
        y = min(y, height - 1)
        self.set_keyboard_cursor_position(x, y)
    
    def set_current_tool(self, tool_name: str) -> None:
        """Set the current drawing tool.
        
        Args:
            tool_name: Name of the current tool
        """
        self._current_tool = tool_name
    
    def _on_cursor_moved(self, x: int, y: int) -> None:
        """Handle cursor movement.
        
        Args:
            x: X coordinate
            y: Y coordinate
        """
        # Clamp to canvas bounds
        x = max(0, min(x, self._canvas_width - 1))
        y = max(0, min(y, self._canvas_height - 1))
        
        # Update position if clamped
        if (x, y) != self.get_keyboard_cursor_position():
            self._keyboard_cursor_pos = QPoint(x, y)
        
        # Emit signals
        self.cursor_moved.emit(x, y)
        
        # Announce position to screen reader
        message = tr_status("cursor_position", x=x, y=y)
        self.navigation_announced.emit(message)
    
    def _on_pixel_activated(self, x: int, y: int) -> None:
        """Handle pixel activation (drawing).
        
        Args:
            x: X coordinate
            y: Y coordinate
        """
        # Clamp to bounds
        x = max(0, min(x, self._canvas_width - 1))
        y = max(0, min(y, self._canvas_height - 1))
        
        self.pixel_activated.emit(x, y)
        
        # Announce action to screen reader
        message = tr_status("pixel_drawn", tool=self._current_tool, x=x, y=y)
        self.navigation_announced.emit(message)
    
    def _handle_end_key(self) -> bool:
        """Handle End key (go to bottom-right).
        
        Returns:
            True if handled
        """
        self.set_keyboard_cursor_position(self._canvas_width - 1, self._canvas_height - 1)
        return True
    
    def handle_tool_shortcut(self, tool_key: str) -> bool:
        """Handle tool shortcut keys.
        
        Args:
            tool_key: Tool shortcut key
            
        Returns:
            True if handled
        """
        tool_map = {
            'B': 'brush',
            'F': 'fill', 
            'E': 'eraser',
            'I': 'color_picker',
            'H': 'pan'
        }
        
        if tool_key.upper() in tool_map:
            tool_name = tool_map[tool_key.upper()]
            self.set_current_tool(tool_name)
            
            # Announce tool change
            message = tr_status("tool_changed_keyboard", tool=tool_name)
            self.navigation_announced.emit(message)
            return True
            
        return False


class GridKeyboardNavigation(QObject):
    """Keyboard navigation for grid-based UI elements (like color grids)."""
    
    # Signals
    item_selected = pyqtSignal(int, int)  # row, column
    selection_announced = pyqtSignal(str)  # message
    
    def __init__(self, rows: int, columns: int, parent=None):
        """Initialize grid navigation.
        
        Args:
            rows: Number of rows in grid
            columns: Number of columns in grid
            parent: Parent object
        """
        super().__init__(parent)
        self._rows = rows
        self._columns = columns
        self._current_row = 0
        self._current_column = 0
        
    def handle_key_event(self, event: QKeyEvent) -> bool:
        """Handle keyboard navigation in grid.
        
        Args:
            event: Key event
            
        Returns:
            True if handled
        """
        key = event.key()
        
        if key == Qt.Key.Key_Up:
            self._current_row = max(0, self._current_row - 1)
            self._emit_selection()
            return True
        elif key == Qt.Key.Key_Down:
            self._current_row = min(self._rows - 1, self._current_row + 1)
            self._emit_selection()
            return True
        elif key == Qt.Key.Key_Left:
            self._current_column = max(0, self._current_column - 1)
            self._emit_selection()
            return True
        elif key == Qt.Key.Key_Right:
            self._current_column = min(self._columns - 1, self._current_column + 1)
            self._emit_selection()
            return True
        elif key in [Qt.Key.Key_Space, Qt.Key.Key_Return, Qt.Key.Key_Enter]:
            self.item_selected.emit(self._current_row, self._current_column)
            return True
            
        return False
    
    def set_current_position(self, row: int, column: int) -> None:
        """Set current grid position.
        
        Args:
            row: Row index
            column: Column index
        """
        self._current_row = max(0, min(row, self._rows - 1))
        self._current_column = max(0, min(column, self._columns - 1))
        self._emit_selection()
    
    def get_current_position(self) -> Tuple[int, int]:
        """Get current grid position.
        
        Returns:
            Tuple of (row, column)
        """
        return (self._current_row, self._current_column)
    
    def _emit_selection(self) -> None:
        """Emit selection change signals."""
        message = tr_status("grid_position", row=self._current_row + 1, column=self._current_column + 1)
        self.selection_announced.emit(message)