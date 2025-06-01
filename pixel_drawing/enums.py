"""Enumerations for improved type safety."""

from enum import Enum


class ToolType(Enum):
    """Tool type enumeration for type-safe tool management."""
    BRUSH = "brush"
    FILL = "fill"
    ERASER = "eraser"
    COLOR_PICKER = "picker"
    PAN = "pan"
    
    @classmethod
    def all_values(cls):
        """Get all tool type values as a list."""
        return [tool.value for tool in cls]
    
    @classmethod
    def from_string(cls, tool_string: str):
        """Convert string to ToolType enum."""
        for tool in cls:
            if tool.value == tool_string:
                return tool
        raise ValueError(f"Unknown tool type: {tool_string}")


class FileExtension(Enum):
    """File extension constants for better maintainability."""
    JSON = ".json"
    PNG = ".png"
    TMP = ".tmp"
    BAK = ".bak"