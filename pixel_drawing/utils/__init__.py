"""Utilities for the pixel drawing application."""

from .shortcuts import setup_keyboard_shortcuts
from .cursors import CursorManager
from .dirty_rectangles import DirtyRegionManager
from .icon_cache import get_cached_icon, preload_app_icons, clear_icon_cache

__all__ = [
    'setup_keyboard_shortcuts', 
    'CursorManager',
    'DirtyRegionManager',
    'get_cached_icon',
    'preload_app_icons',
    'clear_icon_cache'
]