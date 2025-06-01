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
    TOOLBAR_COLOR_BUTTON_WIDTH = 32
    TOOLBAR_COLOR_BUTTON_HEIGHT = 24
    TOOLBAR_BG_COLOR_WIDTH = 20
    TOOLBAR_BG_COLOR_HEIGHT = 16
    
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
    
    # File extensions
    JSON_EXTENSION = ".json"
    PNG_EXTENSION = ".png"
    TMP_EXTENSION = ".tmp"
    BAK_EXTENSION = ".bak"
    
    # Icon paths
    ICON_BRUSH = "icons/paint-brush.svg"
    ICON_FILL = "icons/paint-bucket.svg"
    ICON_ERASER = "icons/eraser.svg"
    ICON_COLOR_PICKER = "icons/eyedropper.svg"
    ICON_PAN = "icons/hand.svg"
    
    # Performance settings
    UPDATE_TIMER_INTERVAL = 16  # ~60 FPS
    MAX_UNDO_HISTORY = 50
    DIRTY_RECT_MERGE_THRESHOLD = 3
    
    # Icon preload sizes
    ICON_PRELOAD_SIZES = [16, 24, 32, 48]
    
    # Error messages
    ERROR_COORDS_OUT_OF_BOUNDS = "Coordinates out of bounds"
    ERROR_INVALID_COLOR = "Invalid color"
    ERROR_INVALID_DIMENSIONS = "Invalid canvas dimensions"
    
    # Status messages
    STATUS_READY = "Ready"
    STATUS_UNDONE = "Undone"
    STATUS_REDONE = "Redone"