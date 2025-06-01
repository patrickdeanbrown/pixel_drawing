"""Command pattern implementation for efficient undo/redo system."""

from abc import ABC, abstractmethod
from typing import Dict, Tuple, List, Optional, TYPE_CHECKING
from PyQt6.QtGui import QColor

if TYPE_CHECKING:
    from .models import PixelArtModel


class Command(ABC):
    """Abstract base class for undoable commands."""
    
    @abstractmethod
    def execute(self) -> None:
        """Execute the command."""
        pass
    
    @abstractmethod
    def undo(self) -> None:
        """Undo the command."""
        pass


class SetPixelCommand(Command):
    """Command for setting a single pixel."""
    
    def __init__(self, model: 'PixelArtModel', x: int, y: int, new_color: QColor):
        """Initialize set pixel command.
        
        Args:
            model: PixelArtModel to operate on
            x: X coordinate
            y: Y coordinate  
            new_color: New color to set
        """
        self._model = model
        self._x = x
        self._y = y
        self._new_color = QColor(new_color)
        self._old_color = model.get_pixel(x, y)
    
    def execute(self) -> None:
        """Set the pixel to new color."""
        self._model._set_pixel_direct(self._x, self._y, self._new_color)
    
    def undo(self) -> None:
        """Restore the pixel to old color."""
        self._model._set_pixel_direct(self._x, self._y, self._old_color)


class SetMultiplePixelsCommand(Command):
    """Command for setting multiple pixels efficiently."""
    
    def __init__(self, model: 'PixelArtModel', pixel_changes: Dict[Tuple[int, int], QColor]):
        """Initialize multiple pixel command.
        
        Args:
            model: PixelArtModel to operate on
            pixel_changes: Dictionary mapping coordinates to new colors
        """
        self._model = model
        self._pixel_changes = {}
        self._old_colors = {}
        
        # Store changes and capture old colors
        for (x, y), new_color in pixel_changes.items():
            self._pixel_changes[(x, y)] = QColor(new_color)
            self._old_colors[(x, y)] = model.get_pixel(x, y)
    
    def execute(self) -> None:
        """Apply all pixel changes."""
        for (x, y), new_color in self._pixel_changes.items():
            self._model._set_pixel_direct(x, y, new_color)
    
    def undo(self) -> None:
        """Restore all pixels to old colors."""
        for (x, y), old_color in self._old_colors.items():
            self._model._set_pixel_direct(x, y, old_color)


class CommandHistory:
    """Manages command history for undo/redo functionality."""
    
    def __init__(self, max_history: int = 50):
        """Initialize command history.
        
        Args:
            max_history: Maximum number of commands to store
        """
        self._commands: List[Command] = []
        self._current_index = -1
        self._max_history = max_history
    
    def execute_command(self, command: Command) -> None:
        """Execute a command and add it to history.
        
        Args:
            command: Command to execute and store
        """
        # Remove any commands after current index (redo history)
        if self._current_index < len(self._commands) - 1:
            self._commands = self._commands[:self._current_index + 1]
        
        # Execute the command
        command.execute()
        
        # Add to history
        self._commands.append(command)
        self._current_index += 1
        
        # Limit history size
        if len(self._commands) > self._max_history:
            self._commands.pop(0)
            self._current_index -= 1
    
    def can_undo(self) -> bool:
        """Check if undo is available."""
        return self._current_index >= 0
    
    def can_redo(self) -> bool:
        """Check if redo is available."""
        return self._current_index < len(self._commands) - 1
    
    def undo(self) -> bool:
        """Undo the last command."""
        if not self.can_undo():
            return False
        
        command = self._commands[self._current_index]
        command.undo()
        self._current_index -= 1
        return True
    
    def redo(self) -> bool:
        """Redo the next command."""
        if not self.can_redo():
            return False
        
        self._current_index += 1
        command = self._commands[self._current_index]
        command.execute()
        return True
    
    def clear(self) -> None:
        """Clear all command history."""
        self._commands.clear()
        self._current_index = -1