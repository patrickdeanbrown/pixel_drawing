"""Cursor management utilities for drawing tools."""

import os
from typing import Dict, Optional
from PyQt6.QtGui import QCursor, QPixmap, QPainter
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtSvg import QSvgRenderer


class CursorManager:
    """Manages custom cursors for drawing tools.
    
    Provides functionality to create custom cursors from SVG icons,
    cache them for performance, and coordinate cursor changes with
    tool selection.
    """
    
    def __init__(self, cursor_size: int = 24):
        """Initialize cursor manager.
        
        Args:
            cursor_size: Size in pixels for custom cursors
        """
        self._cursor_size = cursor_size
        self._cursor_cache: Dict[str, QCursor] = {}
        
        # Create default cursors
        self._default_cursors = {
            "brush": QCursor(Qt.CursorShape.CrossCursor),
            "fill": QCursor(Qt.CursorShape.CrossCursor),
            "eraser": QCursor(Qt.CursorShape.CrossCursor),
            "picker": QCursor(Qt.CursorShape.CrossCursor),
            "pan": QCursor(Qt.CursorShape.OpenHandCursor),
        }
    
    def get_cursor(self, tool_id: str, icon_path: Optional[str] = None) -> QCursor:
        """Get cursor for specified tool.
        
        Args:
            tool_id: Unique identifier for the tool
            icon_path: Optional path to SVG icon for custom cursor
            
        Returns:
            QCursor: Cursor to use for the tool
        """
        # Check cache first
        cache_key = f"{tool_id}_{icon_path}"
        if cache_key in self._cursor_cache:
            return self._cursor_cache[cache_key]
        
        # Create custom cursor from icon if available
        if icon_path and os.path.exists(icon_path):
            cursor = self._create_cursor_from_icon(icon_path)
            if cursor:
                self._cursor_cache[cache_key] = cursor
                return cursor
        
        # Fall back to default cursor for tool
        default_cursor = self._default_cursors.get(tool_id, QCursor(Qt.CursorShape.CrossCursor))
        self._cursor_cache[cache_key] = default_cursor
        return default_cursor
    
    def _create_cursor_from_icon(self, icon_path: str) -> Optional[QCursor]:
        """Create custom cursor from SVG icon.
        
        Args:
            icon_path: Path to SVG icon file
            
        Returns:
            Optional[QCursor]: Custom cursor or None if creation failed
        """
        try:
            if not os.path.exists(icon_path):
                return None
            
            # Create pixmap from SVG
            renderer = QSvgRenderer(icon_path)
            pixmap = QPixmap(self._cursor_size, self._cursor_size)
            pixmap.fill(Qt.GlobalColor.transparent)
            
            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()
            
            # Create cursor with hot spot at center
            hot_spot_x = self._cursor_size // 2
            hot_spot_y = self._cursor_size // 2
            
            return QCursor(pixmap, hot_spot_x, hot_spot_y)
            
        except Exception as e:
            # If cursor creation fails, return None to use default
            print(f"Warning: Failed to create cursor from {icon_path}: {e}")
            return None
    
    def clear_cache(self) -> None:
        """Clear the cursor cache to free memory."""
        self._cursor_cache.clear()
    
    def preload_cursors(self, tool_configs: Dict[str, str]) -> None:
        """Preload cursors for better performance.
        
        Args:
            tool_configs: Dictionary mapping tool IDs to icon paths
        """
        for tool_id, icon_path in tool_configs.items():
            self.get_cursor(tool_id, icon_path)