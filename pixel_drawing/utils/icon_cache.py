"""SVG icon caching system for improved performance."""

from typing import Dict, Optional, List
from PyQt6.QtGui import QIcon, QPixmap, QPainter
from PyQt6.QtCore import QSize
from PyQt6.QtSvg import QSvgRenderer
import os
from ..constants import AppConstants


class IconCache:
    """Caches SVG icons as QIcon objects for better performance.
    
    Prevents repeated SVG parsing and rendering by caching QIcon objects
    with different sizes. Provides theme support and automatic cache management.
    """
    
    def __init__(self):
        """Initialize icon cache."""
        self._cache: Dict[str, QIcon] = {}
        self._size_cache: Dict[Tuple[str, int], QIcon] = {}
    
    def get_icon(self, icon_path: str, size: Optional[int] = None) -> Optional[QIcon]:
        """Get cached icon or create and cache new one.
        
        Args:
            icon_path: Path to SVG icon file
            size: Optional icon size (uses default if None)
            
        Returns:
            QIcon object or None if icon couldn't be loaded
        """
        if not os.path.exists(icon_path):
            return None
        
        # Use size-specific cache if size is specified
        if size is not None:
            cache_key = (icon_path, size)
            if cache_key in self._size_cache:
                return self._size_cache[cache_key]
        else:
            # Use default cache
            if icon_path in self._cache:
                return self._cache[icon_path]
        
        # Create new icon
        icon = self._create_icon(icon_path, size)
        if icon:
            if size is not None:
                self._size_cache[(icon_path, size)] = icon
            else:
                self._cache[icon_path] = icon
        
        return icon
    
    def _create_icon(self, icon_path: str, size: Optional[int]) -> Optional[QIcon]:
        """Create QIcon from SVG file.
        
        Args:
            icon_path: Path to SVG file
            size: Optional size for the icon
            
        Returns:
            QIcon object or None if creation failed
        """
        try:
            if size is not None:
                # Create icon with specific size
                renderer = QSvgRenderer(icon_path)
                pixmap = QPixmap(size, size)
                pixmap.fill()  # Transparent background
                
                painter = QPainter(pixmap)
                renderer.render(painter)
                painter.end()
                
                return QIcon(pixmap)
            else:
                # Create icon directly from SVG (Qt handles sizing)
                return QIcon(icon_path)
        
        except Exception as e:
            from .logging import log_warning
            log_warning("icon_cache", f"Failed to create icon from {icon_path}: {e}")
            return None
    
    def preload_icons(self, icon_paths: Dict[str, str], sizes: Optional[List[int]] = None) -> None:
        """Preload icons for better startup performance.
        
        Args:
            icon_paths: Dictionary mapping names to icon file paths
            sizes: Optional list of sizes to preload
        """
        for name, path in icon_paths.items():
            # Preload default size
            self.get_icon(path)
            
            # Preload specific sizes if requested
            if sizes:
                for size in sizes:
                    self.get_icon(path, size)
    
    def clear_cache(self) -> None:
        """Clear all cached icons to free memory."""
        self._cache.clear()
        self._size_cache.clear()
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics for debugging.
        
        Returns:
            Dictionary with cache size information
        """
        return {
            "default_cache_size": len(self._cache),
            "size_cache_size": len(self._size_cache),
            "total_cached_icons": len(self._cache) + len(self._size_cache)
        }


# Global icon cache instance
_icon_cache = IconCache()


def get_cached_icon(icon_path: str, size: Optional[int] = None) -> Optional[QIcon]:
    """Convenience function to get cached icon.
    
    Args:
        icon_path: Path to SVG icon file
        size: Optional icon size
        
    Returns:
        Cached QIcon object or None if not found
    """
    return _icon_cache.get_icon(icon_path, size)


def preload_app_icons() -> None:
    """Preload all application icons for better performance."""
    icon_paths = {
        "brush": AppConstants.ICON_BRUSH,
        "fill": AppConstants.ICON_FILL, 
        "eraser": AppConstants.ICON_ERASER,
        "color_picker": AppConstants.ICON_COLOR_PICKER,
        "pan": AppConstants.ICON_PAN
    }
    
    # Preload common sizes
    sizes = AppConstants.ICON_PRELOAD_SIZES
    _icon_cache.preload_icons(icon_paths, sizes)


def clear_icon_cache() -> None:
    """Clear the global icon cache."""
    _icon_cache.clear_cache()