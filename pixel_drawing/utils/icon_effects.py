"""Icon color manipulation utilities for different UI states."""

from typing import Optional
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt6.QtCore import Qt
from PyQt6.QtSvg import QSvgRenderer
import os


def create_colored_icon(svg_path: str, color: QColor, size: int = 24) -> Optional[QIcon]:
    """Create a colored version of an SVG icon.
    
    Args:
        svg_path: Path to the SVG icon file
        color: Color to apply to the icon
        size: Size of the icon in pixels
        
    Returns:
        QIcon with the specified color, or None if creation failed
    """
    if not os.path.exists(svg_path):
        return None
    
    try:
        # Create base pixmap
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        # Render SVG to pixmap
        renderer = QSvgRenderer(svg_path)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        
        # Create colored version
        colored_pixmap = QPixmap(size, size)
        colored_pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(colored_pixmap)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        painter.fillRect(colored_pixmap.rect(), color)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationOver)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
        
        return QIcon(colored_pixmap)
        
    except Exception as e:
        print(f"Warning: Failed to create colored icon from {svg_path}: {e}")
        return None


def create_white_icon(svg_path: str, size: int = 24) -> Optional[QIcon]:
    """Create a white version of an SVG icon for selected states.
    
    Args:
        svg_path: Path to the SVG icon file
        size: Size of the icon in pixels
        
    Returns:
        White QIcon for selected state visibility
    """
    return create_colored_icon(svg_path, QColor(255, 255, 255), size)


def create_icon_with_states(svg_path: str, size: int = 24) -> Optional[QIcon]:
    """Create an icon with different states for normal and selected modes.
    
    Args:
        svg_path: Path to the SVG icon file
        size: Size of the icon in pixels
        
    Returns:
        QIcon with normal and selected state variants
    """
    if not os.path.exists(svg_path):
        return None
    
    try:
        icon = QIcon()
        
        # Create normal state (dark icon)
        normal_pixmap = QPixmap(size, size)
        normal_pixmap.fill(Qt.GlobalColor.transparent)
        renderer = QSvgRenderer(svg_path)
        painter = QPainter(normal_pixmap)
        renderer.render(painter)
        painter.end()
        
        # Add normal state
        icon.addPixmap(normal_pixmap, QIcon.Mode.Normal, QIcon.State.Off)
        icon.addPixmap(normal_pixmap, QIcon.Mode.Normal, QIcon.State.On)
        
        # Create selected state (white icon)
        selected_pixmap = QPixmap(size, size)
        selected_pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(selected_pixmap)
        # First draw the original icon
        renderer.render(painter)
        # Then overlay white color using composition mode
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        painter.fillRect(selected_pixmap.rect(), QColor(255, 255, 255))
        painter.end()
        
        # Add selected states  
        icon.addPixmap(selected_pixmap, QIcon.Mode.Selected, QIcon.State.Off)
        icon.addPixmap(selected_pixmap, QIcon.Mode.Selected, QIcon.State.On)
        
        # For active state (when button is pressed/checked)
        icon.addPixmap(selected_pixmap, QIcon.Mode.Active, QIcon.State.On)
        
        return icon
        
    except Exception as e:
        print(f"Warning: Failed to create stateful icon from {svg_path}: {e}")
        return None


class IconStateManager:
    """Manages icon states for tool buttons with dynamic coloring."""
    
    def __init__(self):
        """Initialize icon state manager."""
        self._icon_cache = {}
        self._white_icon_cache = {}
    
    def get_tool_icon(self, svg_path: str, size: int = 24) -> Optional[QIcon]:
        """Get tool icon with proper state handling.
        
        Args:
            svg_path: Path to SVG icon
            size: Icon size
            
        Returns:
            QIcon with normal and selected states
        """
        cache_key = f"{svg_path}_{size}"
        
        if cache_key not in self._icon_cache:
            self._icon_cache[cache_key] = create_icon_with_states(svg_path, size)
        
        return self._icon_cache[cache_key]
    
    def get_white_icon(self, svg_path: str, size: int = 24) -> Optional[QIcon]:
        """Get white version of icon for manual state management.
        
        Args:
            svg_path: Path to SVG icon
            size: Icon size
            
        Returns:
            White QIcon for selected visibility
        """
        cache_key = f"{svg_path}_{size}_white"
        
        if cache_key not in self._white_icon_cache:
            self._white_icon_cache[cache_key] = create_white_icon(svg_path, size)
        
        return self._white_icon_cache[cache_key]
    
    def clear_cache(self) -> None:
        """Clear icon cache to free memory."""
        self._icon_cache.clear()
        self._white_icon_cache.clear()


# Global icon state manager
_icon_state_manager = IconStateManager()


def get_tool_icon(svg_path: str, size: int = 24) -> Optional[QIcon]:
    """Get tool icon with proper state handling via global manager."""
    return _icon_state_manager.get_tool_icon(svg_path, size)


def get_white_icon(svg_path: str, size: int = 24) -> Optional[QIcon]:
    """Get white icon via global manager.""" 
    return _icon_state_manager.get_white_icon(svg_path, size)


def clear_icon_effects_cache() -> None:
    """Clear the global icon effects cache."""
    _icon_state_manager.clear_cache()