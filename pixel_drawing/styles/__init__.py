"""
Modern UI Styling System for Pixel Art Application

This module provides a comprehensive theming and styling system for the pixel art
application, implementing a modern purple-accented design with accessibility support.

Key Components:
- ModernDesignConstants: Centralized design tokens and constants
- StyleManager: Theme loading and application management 
- QSS Stylesheets: Complete styling definitions for all UI components

Usage:
    from pixel_drawing.styles import initialize_style_manager, apply_modern_theme
    
    # Initialize in main application
    app = QApplication(sys.argv)
    style_manager = initialize_style_manager(app)
    apply_modern_theme()
"""

from .design_constants import (
    ModernDesignConstants,
    ToolButtonStates,
    ColorThemes
)

from .style_manager import (
    StyleManager,
    get_style_manager,
    initialize_style_manager,
    apply_modern_theme,
    apply_tool_button_style,
    apply_primary_button_style,
    apply_secondary_button_style,
    apply_danger_button_style
)

from .dialog_styles import (
    ModernDialogStyler,
    show_styled_file_dialog,
    show_styled_color_dialog,
    create_styled_file_dialog,
    create_styled_color_dialog
)

__all__ = [
    # Design Constants
    'ModernDesignConstants',
    'ToolButtonStates', 
    'ColorThemes',
    
    # Style Manager
    'StyleManager',
    'get_style_manager',
    'initialize_style_manager',
    'apply_modern_theme',
    
    # Widget Styling Helpers
    'apply_tool_button_style',
    'apply_primary_button_style',
    'apply_secondary_button_style',
    'apply_danger_button_style',
    
    # Dialog Styling
    'ModernDialogStyler',
    'show_styled_file_dialog',
    'show_styled_color_dialog',
    'create_styled_file_dialog',
    'create_styled_color_dialog',
]

# Version info
__version__ = '1.0.0'
__author__ = 'Pixel Art Application Team'