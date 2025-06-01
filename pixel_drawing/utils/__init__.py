"""Utilities for the pixel drawing application."""

from .shortcuts import setup_keyboard_shortcuts
from .cursors import CursorManager
from .dirty_rectangles import DirtyRegionManager
from .icon_cache import get_cached_icon, preload_app_icons, clear_icon_cache
from .icon_effects import get_tool_icon, get_white_icon, clear_icon_effects_cache
from .logging import (
    init_logging, shutdown_logging, get_logger,
    log_debug, log_info, log_warning, log_error,
    log_performance, log_canvas_event, log_tool_usage, log_file_operation
)

__all__ = [
    'setup_keyboard_shortcuts', 
    'CursorManager',
    'DirtyRegionManager',
    'get_cached_icon',
    'preload_app_icons',
    'clear_icon_cache',
    'get_tool_icon',
    'get_white_icon',
    'clear_icon_effects_cache',
    'init_logging',
    'shutdown_logging', 
    'get_logger',
    'log_debug',
    'log_info', 
    'log_warning',
    'log_error',
    'log_performance',
    'log_canvas_event',
    'log_tool_usage',
    'log_file_operation'
]