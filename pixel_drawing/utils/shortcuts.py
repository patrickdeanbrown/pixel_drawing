"""Keyboard shortcut utilities for the pixel drawing application."""

from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import QMainWindow


def setup_keyboard_shortcuts(window: QMainWindow) -> None:
    """Set up keyboard shortcuts for common actions.
    
    Args:
        window: Main window to attach shortcuts to
        
    Note:
        This function assumes the window has methods: new_file, open_file,
        save_file, save_as_file, export_png, set_tool, clear_canvas, and close.
    """
    # File operations
    QShortcut(QKeySequence("Ctrl+N"), window, window.new_file)
    QShortcut(QKeySequence("Ctrl+O"), window, window.open_file)
    QShortcut(QKeySequence("Ctrl+S"), window, window.save_file)
    QShortcut(QKeySequence("Ctrl+Shift+S"), window, window.save_as_file)
    QShortcut(QKeySequence("Ctrl+E"), window, window.export_png)
    
    # Tool shortcuts  
    QShortcut(QKeySequence("B"), window, lambda: window.set_tool("brush"))
    QShortcut(QKeySequence("F"), window, lambda: window.set_tool("fill"))
    QShortcut(QKeySequence("E"), window, lambda: window.set_tool("eraser"))
    QShortcut(QKeySequence("I"), window, lambda: window.set_tool("picker"))
    QShortcut(QKeySequence("H"), window, lambda: window.set_tool("pan"))
    
    # Canvas operations
    QShortcut(QKeySequence("Ctrl+Del"), window, window.clear_canvas)
    
    # Undo/Redo operations
    QShortcut(QKeySequence("Ctrl+Z"), window, window.undo)
    QShortcut(QKeySequence("Ctrl+Y"), window, window.redo)
    QShortcut(QKeySequence("Ctrl+Shift+Z"), window, window.redo)
    
    # Application shortcuts
    QShortcut(QKeySequence("Ctrl+Q"), window, window.close)