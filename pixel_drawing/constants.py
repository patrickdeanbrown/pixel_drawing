"""Application constants and configuration values."""


class AppConstants:
    """Application constants and configuration values.
    
    Centralized configuration to eliminate magic numbers and provide
    a single source of truth for application-wide settings.
    """
    
    # Canvas defaults
    DEFAULT_CANVAS_WIDTH = 32
    DEFAULT_CANVAS_HEIGHT = 32
    DEFAULT_PIXEL_SIZE = 16
    MAX_CANVAS_SIZE = 256
    MIN_CANVAS_SIZE = 1
    
    # UI dimensions
    MIN_WINDOW_WIDTH = 1000
    MIN_WINDOW_HEIGHT = 700
    SIDE_PANEL_WIDTH = 250
    COLOR_BUTTON_SIZE = 18  # Smaller for compact recent colors
    SMALL_COLOR_BUTTON_SIZE = 16  # Even smaller for toolbar
    ICON_SIZE = 24
    COLOR_DISPLAY_WIDTH = 100
    COLOR_DISPLAY_HEIGHT = 30
    
    # Colors
    DEFAULT_BG_COLOR = "#FFFFFF"
    DEFAULT_FG_COLOR = "#000000"
    GRID_COLOR = "#CCCCCC"
    BORDER_COLOR = "#CCCCCC"
    HOVER_COLOR = "#0066CC"
    
    # UI settings
    RECENT_COLORS_COUNT = 6
    LARGE_CANVAS_THRESHOLD = 256
    
    # File formats
    PROJECT_FILE_FILTER = "JSON files (*.json)"
    PNG_FILE_FILTER = "PNG files (*.png)"