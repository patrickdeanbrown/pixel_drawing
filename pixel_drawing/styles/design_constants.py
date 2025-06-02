"""
Design Constants for Modern UI Theme
Centralized design tokens for the pixel art application's modern interface.
"""

from PyQt6.QtGui import QColor, QFont


class ModernDesignConstants:
    """Modern design system constants and tokens."""
    
    # ==========================================================================
    # Color Palette
    # ==========================================================================
    
    # Primary Colors
    PRIMARY_PURPLE = "#A020F0"
    PRIMARY_PURPLE_DARK = "#8C1AC9"
    PRIMARY_PURPLE_LIGHT = "#B348F7"
    PRIMARY_PURPLE_ALPHA = "rgba(160, 32, 240, 0.1)"
    
    # Secondary Colors
    SECONDARY_MAROON = "#8B1538"
    SECONDARY_MAROON_LIGHT = "#A8276D"
    
    # Background Colors
    BG_MAIN = "#F8F9FA"
    BG_PANEL = "#FFFFFF"
    BG_SECONDARY = "#F1F3F4"
    BG_HOVER = "#E8F0FE"
    BG_PRESSED = "#D2E3FC"
    BG_DISABLED = "#F5F5F5"
    
    # Text Colors
    TEXT_PRIMARY = "#202124"
    TEXT_SECONDARY = "#5F6368"
    TEXT_DISABLED = "#9AA0A6"
    TEXT_INVERSE = "#FFFFFF"
    
    # Border Colors
    BORDER_LIGHT = "#E8EAED"
    BORDER_MEDIUM = "#DADCE0"
    BORDER_DARK = "#BABABA"
    BORDER_FOCUS = "#A020F0"
    
    # Status Colors
    SUCCESS = "#34A853"
    WARNING = "#FBBC04"
    ERROR = "#EA4335"
    INFO = "#4285F4"
    
    # ==========================================================================
    # Typography
    # ==========================================================================
    
    # Font Families
    FONT_FAMILY_PRIMARY = "Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"
    FONT_FAMILY_MONOSPACE = "JetBrains Mono, Consolas, Monaco, monospace"
    
    # Font Sizes
    FONT_SIZE_SMALL = 12
    FONT_SIZE_REGULAR = 14
    FONT_SIZE_MEDIUM = 16
    FONT_SIZE_LARGE = 18
    FONT_SIZE_XLARGE = 24
    
    # Font Weights
    FONT_WEIGHT_NORMAL = 400
    FONT_WEIGHT_MEDIUM = 500
    FONT_WEIGHT_SEMIBOLD = 600
    FONT_WEIGHT_BOLD = 700
    
    # ==========================================================================
    # Spacing and Layout
    # ==========================================================================
    
    # Spacing Scale
    SPACING_XS = 4
    SPACING_SM = 8
    SPACING_MD = 12
    SPACING_LG = 16
    SPACING_XL = 24
    SPACING_XXL = 32
    
    # Padding
    PADDING_BUTTON = "8px 16px"
    PADDING_INPUT = "8px 12px"
    PADDING_PANEL = "16px 12px 12px 12px"
    PADDING_TOOL_BUTTON = "12px"
    
    # Margins
    MARGIN_PANEL = "16px"
    MARGIN_SECTION = "8px"
    MARGIN_ELEMENT = "4px"
    
    # ==========================================================================
    # Component Dimensions
    # ==========================================================================
    
    # Buttons
    BUTTON_HEIGHT_SMALL = 32
    BUTTON_HEIGHT_REGULAR = 40
    BUTTON_HEIGHT_LARGE = 48
    
    BUTTON_MIN_WIDTH = 80
    TOOL_BUTTON_SIZE = 48
    COLOR_SWATCH_SIZE = 32
    LARGE_COLOR_DISPLAY_SIZE = 80
    
    # Panels
    SIDE_PANEL_WIDTH = 280
    SIDE_PANEL_MIN_WIDTH = 240
    SIDE_PANEL_MAX_WIDTH = 320
    
    # Input Fields
    INPUT_HEIGHT = 36
    SPINBOX_WIDTH = 80
    
    # Icons
    ICON_SIZE_SMALL = 16
    ICON_SIZE_REGULAR = 24
    ICON_SIZE_LARGE = 32
    ICON_SIZE_TOOL = 24
    
    # ==========================================================================
    # Border Radius
    # ==========================================================================
    
    RADIUS_SMALL = 4
    RADIUS_MEDIUM = 6
    RADIUS_LARGE = 8
    RADIUS_XLARGE = 12
    
    # ==========================================================================
    # Shadows
    # ==========================================================================
    
    SHADOW_LIGHT = "0 1px 3px rgba(0, 0, 0, 0.12)"
    SHADOW_MEDIUM = "0 2px 6px rgba(0, 0, 0, 0.15)"
    SHADOW_HEAVY = "0 4px 12px rgba(0, 0, 0, 0.15)"
    SHADOW_FOCUS = "0 0 0 2px rgba(160, 32, 240, 0.2)"
    
    # ==========================================================================
    # Animation and Interaction
    # ==========================================================================
    
    ANIMATION_DURATION_FAST = 150
    ANIMATION_DURATION_NORMAL = 250
    ANIMATION_DURATION_SLOW = 400
    
    HOVER_TRANSITION = "all 0.15s ease-in-out"
    FOCUS_TRANSITION = "box-shadow 0.15s ease-in-out"
    
    # ==========================================================================
    # Layout Grids
    # ==========================================================================
    
    # Tool Grid
    TOOL_GRID_COLUMNS = 2
    TOOL_GRID_SPACING = 8
    
    # Color Grid
    COLOR_GRID_COLUMNS = 3
    COLOR_GRID_ROWS = 2
    COLOR_GRID_SPACING = 4
    
    # ==========================================================================
    # Accessibility
    # ==========================================================================
    
    # Minimum touch target size (WCAG AAA)
    MIN_TOUCH_TARGET = 44
    
    # Focus outline width
    FOCUS_OUTLINE_WIDTH = 2
    
    # High contrast ratios
    CONTRAST_RATIO_AA = 4.5
    CONTRAST_RATIO_AAA = 7.0
    
    # ==========================================================================
    # Recent Colors Configuration
    # ==========================================================================
    
    RECENT_COLORS_COUNT = 6
    RECENT_COLORS_GRID_COLS = 3
    RECENT_COLORS_GRID_ROWS = 2
    
    # ==========================================================================
    # Panel Configuration
    # ==========================================================================
    
    PANEL_SECTION_SPACING = 16
    PANEL_HEADER_MARGIN_BOTTOM = 8
    PANEL_CONTENT_PADDING = 12
    
    # ==========================================================================
    # Helper Methods
    # ==========================================================================
    
    @classmethod
    def get_primary_font(cls, size: int = None, weight: int = None) -> QFont:
        """Get the primary font with optional size and weight."""
        font = QFont("Segoe UI")
        if size:
            font.setPointSize(size)
        if weight:
            font.setWeight(weight)
        return font
    
    @classmethod
    def get_monospace_font(cls, size: int = None) -> QFont:
        """Get the monospace font with optional size."""
        font = QFont("JetBrains Mono")
        if size:
            font.setPointSize(size)
        return font
    
    @classmethod
    def get_primary_color(cls) -> QColor:
        """Get the primary purple color as QColor."""
        return QColor(cls.PRIMARY_PURPLE)
    
    @classmethod
    def get_primary_color_dark(cls) -> QColor:
        """Get the dark primary purple color as QColor."""
        return QColor(cls.PRIMARY_PURPLE_DARK)
    
    @classmethod
    def get_background_color(cls) -> QColor:
        """Get the main background color as QColor."""
        return QColor(cls.BG_MAIN)
    
    @classmethod
    def get_panel_color(cls) -> QColor:
        """Get the panel background color as QColor."""
        return QColor(cls.BG_PANEL)
    
    @classmethod
    def get_text_color(cls) -> QColor:
        """Get the primary text color as QColor."""
        return QColor(cls.TEXT_PRIMARY)
    
    @classmethod
    def get_border_color(cls) -> QColor:
        """Get the border color as QColor."""
        return QColor(cls.BORDER_LIGHT)


class ToolButtonStates:
    """Tool button state styling configurations."""
    
    NORMAL = {
        'background': ModernDesignConstants.BG_PANEL,
        'border': ModernDesignConstants.BORDER_LIGHT,
        'color': ModernDesignConstants.TEXT_PRIMARY
    }
    
    HOVER = {
        'background': ModernDesignConstants.BG_HOVER,
        'border': ModernDesignConstants.PRIMARY_PURPLE,
        'color': ModernDesignConstants.PRIMARY_PURPLE
    }
    
    CHECKED = {
        'background': ModernDesignConstants.PRIMARY_PURPLE,
        'border': ModernDesignConstants.PRIMARY_PURPLE_DARK,
        'color': ModernDesignConstants.TEXT_INVERSE
    }
    
    CHECKED_HOVER = {
        'background': ModernDesignConstants.PRIMARY_PURPLE_DARK,
        'border': ModernDesignConstants.PRIMARY_PURPLE_DARK,
        'color': ModernDesignConstants.TEXT_INVERSE
    }


class ColorThemes:
    """Color theme configurations for different UI modes."""
    
    LIGHT = {
        'background': ModernDesignConstants.BG_MAIN,
        'panel': ModernDesignConstants.BG_PANEL,
        'text': ModernDesignConstants.TEXT_PRIMARY,
        'border': ModernDesignConstants.BORDER_LIGHT
    }
    
    DARK = {
        'background': '#1F1F1F',
        'panel': '#2D2D2D',
        'text': '#E8EAED',
        'border': '#5F6368'
    }
    
    HIGH_CONTRAST = {
        'background': '#000000',
        'panel': '#000000',
        'text': '#FFFFFF',
        'border': '#FFFFFF'
    }


# Export commonly used constants for easy importing
__all__ = [
    'ModernDesignConstants',
    'ToolButtonStates', 
    'ColorThemes'
]