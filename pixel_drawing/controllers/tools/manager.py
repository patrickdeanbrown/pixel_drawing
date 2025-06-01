"""Tool manager for handling drawing tool selection and delegation."""

from typing import Dict, Optional
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QColor

from .base import DrawingTool
from .brush import BrushTool
from .fill import FillTool
from .eraser import EraserTool
from .color_picker import ColorPickerTool
from .pan import PanTool
from ...models import PixelArtModel
from ...enums import ToolType


class ToolManager(QObject):
    """Manages available drawing tools and current tool selection.
    
    The ToolManager acts as a registry and coordinator for drawing tools,
    providing a unified interface for tool operations and maintaining
    the current active tool state.
    """
    
    # Signals
    tool_changed = pyqtSignal(str)  # Emitted when active tool changes
    
    def __init__(self, model: PixelArtModel):
        """Initialize tool manager.
        
        Args:
            model: PixelArtModel for tools to operate on
        """
        super().__init__()
        self._model = model
        self._tools: Dict[str, DrawingTool] = {}
        self._current_tool: Optional[DrawingTool] = None
        
        # Register all available tools using enum values
        self.register_tool(ToolType.BRUSH.value, BrushTool(model))
        self.register_tool(ToolType.FILL.value, FillTool(model))
        self.register_tool(ToolType.ERASER.value, EraserTool(model))
        self.register_tool(ToolType.COLOR_PICKER.value, ColorPickerTool(model))
        self.register_tool(ToolType.PAN.value, PanTool(model))
        
        # Set default tool
        self.set_current_tool(ToolType.BRUSH.value)
    
    def register_tool(self, tool_id: str, tool: DrawingTool) -> None:
        """Register a new tool.
        
        Args:
            tool_id: Unique identifier for the tool
            tool: DrawingTool instance
        """
        self._tools[tool_id] = tool
    
    def get_tool(self, tool_id: str) -> Optional[DrawingTool]:
        """Get tool by ID.
        
        Args:
            tool_id: Tool identifier
            
        Returns:
            DrawingTool instance or None if not found
        """
        return self._tools.get(tool_id)
    
    def get_available_tools(self) -> Dict[str, str]:
        """Get available tools.
        
        Returns:
            Dictionary mapping tool IDs to tool names
        """
        return {tool_id: tool.name for tool_id, tool in self._tools.items()}
    
    def set_current_tool(self, tool_id: str) -> bool:
        """Set the current active tool.
        
        Args:
            tool_id: Tool identifier
            
        Returns:
            True if tool was set successfully
        """
        tool = self.get_tool(tool_id)
        if tool:
            from ...utils.logging import log_debug
            log_debug("tools", f"Tool changed to: {tool_id}")
            self._current_tool = tool
            self.tool_changed.emit(tool_id)
            return True
        else:
            from ...utils.logging import log_warning
            log_warning("tools", f"Failed to set unknown tool: {tool_id}")
            return False
    
    @property
    def current_tool(self) -> Optional[DrawingTool]:
        """Get current active tool."""
        return self._current_tool
    
    def handle_press(self, x: int, y: int, color: QColor) -> bool:
        """Handle mouse press with current tool.
        
        Args:
            x: X coordinate
            y: Y coordinate
            color: Current drawing color
            
        Returns:
            True if tool should receive move events
        """
        if self._current_tool:
            from ...utils.logging import log_tool_usage, log_error
            tool_name = self._current_tool.name
            log_tool_usage(tool_name, "press", f"({x},{y})")
            try:
                return self._current_tool.on_press(x, y, color)
            except Exception as e:
                log_error("tools", f"Tool {tool_name} press handler failed: {e}")
                return False
        return False
    
    def handle_move(self, x: int, y: int, color: QColor) -> None:
        """Handle mouse move with current tool."""
        if self._current_tool:
            try:
                self._current_tool.on_move(x, y, color)
            except Exception as e:
                from ...utils.logging import log_error
                tool_name = self._current_tool.name
                log_error("tools", f"Tool {tool_name} move handler failed: {e}")
    
    def handle_release(self, x: int, y: int, color: QColor) -> None:
        """Handle mouse release with current tool."""
        if self._current_tool:
            try:
                self._current_tool.on_release(x, y, color)
            except Exception as e:
                from ...utils.logging import log_error
                tool_name = self._current_tool.name
                log_error("tools", f"Tool {tool_name} release handler failed: {e}")