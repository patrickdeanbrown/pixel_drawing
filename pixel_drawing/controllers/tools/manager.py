"""Tool manager for handling drawing tool selection and delegation."""

from typing import Dict, Optional
from PyQt6.QtGui import QColor

from .base import DrawingTool
from .brush import BrushTool
from .fill import FillTool
from .eraser import EraserTool
from .color_picker import ColorPickerTool
from .pan import PanTool
from ...models import PixelArtModel


class ToolManager:
    """Manages available drawing tools and current tool selection.
    
    The ToolManager acts as a registry and coordinator for drawing tools,
    providing a unified interface for tool operations and maintaining
    the current active tool state.
    """
    
    def __init__(self, model: PixelArtModel):
        """Initialize tool manager.
        
        Args:
            model: PixelArtModel for tools to operate on
        """
        self._model = model
        self._tools: Dict[str, DrawingTool] = {}
        self._current_tool: Optional[DrawingTool] = None
        
        # Register all available tools
        self.register_tool("brush", BrushTool(model))
        self.register_tool("fill", FillTool(model))
        self.register_tool("eraser", EraserTool(model))
        self.register_tool("picker", ColorPickerTool(model))
        self.register_tool("pan", PanTool(model))
        
        # Set default tool
        self.set_current_tool("brush")
    
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
            self._current_tool = tool
            return True
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
            return self._current_tool.on_press(x, y, color)
        return False
    
    def handle_move(self, x: int, y: int, color: QColor) -> None:
        """Handle mouse move with current tool."""
        if self._current_tool:
            self._current_tool.on_move(x, y, color)
    
    def handle_release(self, x: int, y: int, color: QColor) -> None:
        """Handle mouse release with current tool."""
        if self._current_tool:
            self._current_tool.on_release(x, y, color)