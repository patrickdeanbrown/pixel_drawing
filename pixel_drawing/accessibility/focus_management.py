"""Focus management for accessibility."""

from typing import List, Optional, Dict, Any
from PyQt6.QtCore import QObject, pyqtSignal, Qt
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtGui import QFocusEvent

from .screen_reader import ScreenReaderSupport, AccessibilityAnnouncer


class FocusManager(QObject):
    """Manages focus order and accessibility for UI components."""
    
    # Signals
    focus_changed = pyqtSignal(QWidget, QWidget)  # old_widget, new_widget
    focus_announced = pyqtSignal(str)  # announcement message
    
    def __init__(self, screen_reader: ScreenReaderSupport, parent=None):
        """Initialize focus manager.
        
        Args:
            screen_reader: Screen reader support instance
            parent: Parent object
        """
        super().__init__(parent)
        self._screen_reader = screen_reader
        self._announcer = AccessibilityAnnouncer(screen_reader, self)
        
        self._focus_order: List[QWidget] = []
        self._current_focus_index = -1
        self._focus_history: List[QWidget] = []
        self._focus_groups: Dict[str, List[QWidget]] = {}
        
        # Install application-wide event filter
        if QApplication.instance():
            QApplication.instance().focusChanged.connect(self._on_focus_changed)
    
    def register_focus_group(self, group_name: str, widgets: List[QWidget]) -> None:
        """Register a group of widgets for focus management.
        
        Args:
            group_name: Name of the focus group
            widgets: List of widgets in the group
        """
        self._focus_groups[group_name] = widgets
        
        # Ensure widgets can receive focus
        for widget in widgets:
            if widget.focusPolicy() == Qt.FocusPolicy.NoFocus:
                widget.setFocusPolicy(Qt.FocusPolicy.TabFocus)
    
    def set_focus_order(self, widgets: List[QWidget]) -> None:
        """Set the tab order for widgets.
        
        Args:
            widgets: List of widgets in desired tab order
        """
        self._focus_order = widgets
        
        # Set Qt tab order
        for i in range(len(widgets) - 1):
            QWidget.setTabOrder(widgets[i], widgets[i + 1])
    
    def move_focus_to_group(self, group_name: str, widget_index: int = 0) -> bool:
        """Move focus to a specific widget group.
        
        Args:
            group_name: Name of the focus group
            widget_index: Index of widget within group to focus
            
        Returns:
            True if focus was moved successfully
        """
        if group_name not in self._focus_groups:
            return False
            
        widgets = self._focus_groups[group_name]
        if 0 <= widget_index < len(widgets):
            widget = widgets[widget_index]
            if widget.isVisible() and widget.isEnabled():
                widget.setFocus()
                return True
        
        return False
    
    def move_focus_next_in_group(self, group_name: str) -> bool:
        """Move focus to next widget in group.
        
        Args:
            group_name: Name of the focus group
            
        Returns:
            True if focus was moved
        """
        if group_name not in self._focus_groups:
            return False
            
        widgets = self._focus_groups[group_name]
        current_widget = QApplication.focusWidget()
        
        if current_widget in widgets:
            current_index = widgets.index(current_widget)
            next_index = (current_index + 1) % len(widgets)
            
            # Find next focusable widget
            for i in range(len(widgets)):
                widget_index = (next_index + i) % len(widgets)
                widget = widgets[widget_index]
                if widget.isVisible() and widget.isEnabled():
                    widget.setFocus()
                    return True
        
        return False
    
    def move_focus_previous_in_group(self, group_name: str) -> bool:
        """Move focus to previous widget in group.
        
        Args:
            group_name: Name of the focus group
            
        Returns:
            True if focus was moved
        """
        if group_name not in self._focus_groups:
            return False
            
        widgets = self._focus_groups[group_name]
        current_widget = QApplication.focusWidget()
        
        if current_widget in widgets:
            current_index = widgets.index(current_widget)
            prev_index = (current_index - 1) % len(widgets)
            
            # Find previous focusable widget
            for i in range(len(widgets)):
                widget_index = (prev_index - i) % len(widgets)
                widget = widgets[widget_index]
                if widget.isVisible() and widget.isEnabled():
                    widget.setFocus()
                    return True
        
        return False
    
    def save_focus(self) -> Optional[QWidget]:
        """Save current focus for restoration.
        
        Returns:
            Currently focused widget
        """
        current_widget = QApplication.focusWidget()
        if current_widget:
            self._focus_history.append(current_widget)
        return current_widget
    
    def restore_focus(self) -> bool:
        """Restore previously saved focus.
        
        Returns:
            True if focus was restored
        """
        if self._focus_history:
            widget = self._focus_history.pop()
            if widget.isVisible() and widget.isEnabled():
                widget.setFocus()
                return True
        return False
    
    def ensure_focus_visible(self, widget: QWidget) -> None:
        """Ensure focused widget is visible and properly announced.
        
        Args:
            widget: Widget to ensure visibility for
        """
        if not widget:
            return
            
        # Scroll to make widget visible if in scroll area
        parent = widget.parentWidget()
        while parent:
            if hasattr(parent, 'ensureWidgetVisible'):
                parent.ensureWidgetVisible(widget)
                break
            parent = parent.parentWidget()
    
    def set_initial_focus(self, widget: QWidget) -> None:
        """Set initial focus for a container.
        
        Args:
            widget: Widget to receive initial focus
        """
        if widget.isVisible() and widget.isEnabled():
            widget.setFocus()
            self._announcer.announce_widget_focus(widget)
    
    def handle_escape_key(self) -> bool:
        """Handle escape key for focus management.
        
        Returns:
            True if escape was handled
        """
        # Return focus to main area or close dialogs
        return self.restore_focus()
    
    def _on_focus_changed(self, old_widget: Optional[QWidget], new_widget: Optional[QWidget]) -> None:
        """Handle focus change events.
        
        Args:
            old_widget: Previously focused widget
            new_widget: Newly focused widget
        """
        if new_widget:
            # Update current focus index if in focus order
            if new_widget in self._focus_order:
                self._current_focus_index = self._focus_order.index(new_widget)
            
            # Ensure widget is visible
            self.ensure_focus_visible(new_widget)
            
            # Announce to screen reader
            self._announcer.announce_widget_focus(new_widget)
            
            # Emit signal
            self.focus_changed.emit(old_widget, new_widget)


class DialogFocusManager(FocusManager):
    """Specialized focus manager for dialogs."""
    
    def __init__(self, dialog: QWidget, screen_reader: ScreenReaderSupport, parent=None):
        """Initialize dialog focus manager.
        
        Args:
            dialog: Dialog widget
            screen_reader: Screen reader support
            parent: Parent object
        """
        super().__init__(screen_reader, parent)
        self._dialog = dialog
        self._initial_focus_widget: Optional[QWidget] = None
        self._previous_focus_widget: Optional[QWidget] = None
    
    def setup_dialog_focus(self, initial_focus_widget: Optional[QWidget] = None) -> None:
        """Set up focus for dialog.
        
        Args:
            initial_focus_widget: Widget to receive initial focus
        """
        # Save focus from main window
        self._previous_focus_widget = QApplication.focusWidget()
        
        # Set initial focus
        if initial_focus_widget:
            self._initial_focus_widget = initial_focus_widget
            self.set_initial_focus(initial_focus_widget)
        
        # Announce dialog opening
        dialog_title = self._dialog.windowTitle()
        self._announcer.announce_dialog_opened(dialog_title)
    
    def close_dialog_focus(self) -> None:
        """Handle focus when dialog closes."""
        # Restore focus to main window
        if self._previous_focus_widget and self._previous_focus_widget.isVisible():
            self._previous_focus_widget.setFocus()
    
    def handle_tab_navigation(self, forward: bool = True) -> bool:
        """Handle tab navigation within dialog.
        
        Args:
            forward: True for forward tab, False for backward
            
        Returns:
            True if navigation was handled
        """
        current_widget = QApplication.focusWidget()
        if not current_widget:
            return False
        
        # Find next/previous focusable widget
        if forward:
            next_widget = current_widget.nextInFocusChain()
        else:
            next_widget = current_widget.previousInFocusChain()
        
        # Ensure we stay within dialog
        if next_widget and self._is_widget_in_dialog(next_widget):
            next_widget.setFocus()
            return True
        
        return False
    
    def _is_widget_in_dialog(self, widget: QWidget) -> bool:
        """Check if widget is within the dialog.
        
        Args:
            widget: Widget to check
            
        Returns:
            True if widget is in dialog
        """
        parent = widget
        while parent:
            if parent == self._dialog:
                return True
            parent = parent.parentWidget()
        return False


class CanvasFocusManager(FocusManager):
    """Specialized focus manager for the drawing canvas."""
    
    def __init__(self, canvas: QWidget, screen_reader: ScreenReaderSupport, parent=None):
        """Initialize canvas focus manager.
        
        Args:
            canvas: Canvas widget
            screen_reader: Screen reader support
            parent: Parent object
        """
        super().__init__(screen_reader, parent)
        self._canvas = canvas
        self._canvas_has_focus = False
    
    def enter_canvas_mode(self) -> None:
        """Enter canvas-focused mode for drawing."""
        self._canvas.setFocus()
        self._canvas_has_focus = True
        
        # Announce canvas mode
        message = "Drawing mode. Use arrow keys to navigate, Space to draw, Escape to exit."
        self._screen_reader.announce(message, "high")
    
    def exit_canvas_mode(self) -> None:
        """Exit canvas-focused mode."""
        self._canvas_has_focus = False
        
        # Return focus to tools or main UI
        self.restore_focus()
        
        # Announce mode exit
        message = "Exited drawing mode."
        self._screen_reader.announce(message, "normal")
    
    def is_in_canvas_mode(self) -> bool:
        """Check if in canvas-focused mode.
        
        Returns:
            True if in canvas mode
        """
        return self._canvas_has_focus and self._canvas.hasFocus()