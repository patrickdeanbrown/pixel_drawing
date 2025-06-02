"""Screen reader support and announcements."""

from typing import Optional, Dict, Any
from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from PyQt6.QtWidgets import QWidget, QApplication

from ..i18n import tr_status, tr_panel


class ScreenReaderSupport(QObject):
    """Manages screen reader announcements and accessibility events."""
    
    # Signals
    announcement_requested = pyqtSignal(str)  # message
    
    def __init__(self, parent=None):
        """Initialize screen reader support.
        
        Args:
            parent: Parent object
        """
        super().__init__(parent)
        self._announcement_queue = []
        self._announcement_timer = QTimer()
        self._announcement_timer.timeout.connect(self._process_announcement_queue)
        self._announcement_timer.setSingleShot(True)
        
        # Track last announcement to avoid duplicates
        self._last_announcement = ""
        self._announcement_cooldown = 500  # ms
    
    def announce(self, message: str, priority: str = "normal") -> None:
        """Announce a message to screen readers.
        
        Args:
            message: Message to announce
            priority: Priority level ("low", "normal", "high")
        """
        if not message or message == self._last_announcement:
            return
            
        self._announcement_queue.append({
            'message': message,
            'priority': priority,
            'timestamp': QTimer().elapsed() if hasattr(QTimer(), 'elapsed') else 0
        })
        
        # Process immediately for high priority, otherwise queue
        if priority == "high":
            self._process_announcement_immediately(message)
        else:
            self._schedule_announcement_processing()
    
    def announce_canvas_state(self, x: int, y: int, color_name: str, tool_name: str) -> None:
        """Announce current canvas state.
        
        Args:
            x: X coordinate
            y: Y coordinate  
            color_name: Name of current color
            tool_name: Name of current tool
        """
        message = tr_status("canvas_state", x=x, y=y, color=color_name, tool=tool_name)
        self.announce(message, "normal")
    
    def announce_tool_change(self, tool_name: str, shortcut: str) -> None:
        """Announce tool change.
        
        Args:
            tool_name: Name of new tool
            shortcut: Tool keyboard shortcut
        """
        message = tr_status("tool_selected", tool=tool_name, shortcut=shortcut)
        self.announce(message, "high")
    
    def announce_color_change(self, color_name: str, hex_value: str) -> None:
        """Announce color change.
        
        Args:
            color_name: Human-readable color name
            hex_value: Hex color value
        """
        message = tr_status("color_selected", color=color_name, hex=hex_value)
        self.announce(message, "normal")
    
    def announce_canvas_operation(self, operation: str, x: int, y: int) -> None:
        """Announce canvas drawing operation.
        
        Args:
            operation: Type of operation (draw, fill, erase)
            x: X coordinate
            y: Y coordinate
        """
        message = tr_status("canvas_operation", operation=operation, x=x, y=y)
        self.announce(message, "low")
    
    def announce_navigation(self, x: int, y: int, total_width: int, total_height: int) -> None:
        """Announce navigation position.
        
        Args:
            x: X coordinate
            y: Y coordinate
            total_width: Total canvas width
            total_height: Total canvas height
        """
        # Calculate position as percentage for context
        x_percent = int((x / max(1, total_width - 1)) * 100)
        y_percent = int((y / max(1, total_height - 1)) * 100)
        
        message = tr_status("navigation_position", x=x, y=y, x_percent=x_percent, y_percent=y_percent)
        self.announce(message, "low")
    
    def announce_validation_error(self, error_message: str) -> None:
        """Announce validation error.
        
        Args:
            error_message: Error message to announce
        """
        message = tr_status("validation_error", error=error_message)
        self.announce(message, "high")
    
    def announce_file_operation(self, operation: str, filename: str, success: bool) -> None:
        """Announce file operation result.
        
        Args:
            operation: Type of operation (save, load, export)
            filename: File name
            success: Whether operation succeeded
        """
        if success:
            message = tr_status("file_operation_success", operation=operation, filename=filename)
        else:
            message = tr_status("file_operation_failed", operation=operation, filename=filename)
            
        self.announce(message, "high")
    
    def _process_announcement_immediately(self, message: str) -> None:
        """Process high priority announcement immediately.
        
        Args:
            message: Message to announce
        """
        self._last_announcement = message
        self.announcement_requested.emit(message)
        
        # Use Qt accessibility system for immediate announcement
        if QApplication.instance():
            # Create a temporary widget for the announcement
            temp_widget = QWidget()
            temp_widget.setAccessibleName(message)
            
            # Note: QAccessible usage removed for compatibility
            # Screen reader announcements would be handled through platform-specific APIs
    
    def _schedule_announcement_processing(self) -> None:
        """Schedule processing of queued announcements."""
        if not self._announcement_timer.isActive():
            self._announcement_timer.start(100)  # Process after 100ms
    
    def _process_announcement_queue(self) -> None:
        """Process queued announcements."""
        if not self._announcement_queue:
            return
            
        # Get highest priority announcement
        announcement = max(self._announcement_queue, 
                         key=lambda x: {"high": 3, "normal": 2, "low": 1}.get(x['priority'], 1))
        
        self._announcement_queue.remove(announcement)
        
        message = announcement['message']
        if message != self._last_announcement:
            self._process_announcement_immediately(message)
        
        # Schedule next processing if queue not empty
        if self._announcement_queue:
            self._announcement_timer.start(self._announcement_cooldown)


class AccessibilityAnnouncer(QObject):
    """High-level accessibility announcer for common UI operations."""
    
    def __init__(self, screen_reader: ScreenReaderSupport, parent=None):
        """Initialize accessibility announcer.
        
        Args:
            screen_reader: Screen reader support instance
            parent: Parent object
        """
        super().__init__(parent)
        self._screen_reader = screen_reader
        
    def announce_widget_focus(self, widget: QWidget) -> None:
        """Announce when a widget receives focus.
        
        Args:
            widget: Widget that received focus
        """
        name = widget.accessibleName()
        description = widget.accessibleDescription()
        
        if name:
            message = name
            if description:
                message += f". {description}"
            self._screen_reader.announce(message, "normal")
    
    def announce_button_activation(self, button_name: str, action_result: str = "") -> None:
        """Announce button activation.
        
        Args:
            button_name: Name of activated button
            action_result: Optional result description
        """
        message = tr_status("button_activated", button=button_name)
        if action_result:
            message += f". {action_result}"
        self._screen_reader.announce(message, "normal")
    
    def announce_menu_navigation(self, menu_name: str, item_name: str) -> None:
        """Announce menu navigation.
        
        Args:
            menu_name: Name of menu
            item_name: Name of menu item
        """
        message = tr_status("menu_navigation", menu=menu_name, item=item_name)
        self._screen_reader.announce(message, "normal")
    
    def announce_dialog_opened(self, dialog_title: str) -> None:
        """Announce dialog opening.
        
        Args:
            dialog_title: Title of opened dialog
        """
        message = tr_status("dialog_opened", title=dialog_title)
        self._screen_reader.announce(message, "high")
    
    def announce_value_change(self, control_name: str, old_value: str, new_value: str) -> None:
        """Announce value change in controls.
        
        Args:
            control_name: Name of control
            old_value: Previous value
            new_value: New value
        """
        message = tr_status("value_changed", control=control_name, value=new_value)
        self._screen_reader.announce(message, "normal")
    
    def announce_selection_change(self, item_name: str, position: str = "") -> None:
        """Announce selection change.
        
        Args:
            item_name: Name of selected item
            position: Optional position description
        """
        message = tr_status("selection_changed", item=item_name)
        if position:
            message += f" {position}"
        self._screen_reader.announce(message, "normal")