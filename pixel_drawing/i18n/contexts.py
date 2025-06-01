"""Translation contexts and type-safe key definitions."""


class UIContext:
    """UI element translation contexts.
    
    These contexts organize translations by functional area,
    making it easier to manage and maintain translations.
    """
    WINDOW_TITLES = "window_titles"
    TOOLBAR = "toolbar"
    TOOLS = "tools"
    PANELS = "panels"
    DIALOGS = "dialogs"
    STATUS = "status"
    ERRORS = "errors"
    FILE_FILTERS = "file_filters"
    PREFERENCES = "preferences"


class TranslationKey:
    """Type-safe translation key definitions.
    
    Provides compile-time validation of translation keys and
    prevents typos in translation lookups.
    """
    
    class WindowTitles:
        """Window title translation keys."""
        APP_TITLE = "app_title"
        APP_WITH_FILE = "app_with_file"
    
    class Toolbar:
        """Toolbar action translation keys."""
        NEW = "new"
        OPEN = "open"
        SAVE = "save"
        SAVE_AS = "save_as"
        EXPORT_PNG = "export_png"
        UNDO = "undo"
        REDO = "redo"
    
    class Tools:
        """Tool name and tooltip translation keys."""
        BRUSH = "brush"
        BRUSH_TOOLTIP = "brush_tooltip"
        FILL = "fill"
        FILL_TOOLTIP = "fill_tooltip"
        ERASER = "eraser"
        ERASER_TOOLTIP = "eraser_tooltip"
        COLOR_PICKER = "color_picker"
        COLOR_PICKER_TOOLTIP = "color_picker_tooltip"
        PAN = "pan"
        PAN_TOOLTIP = "pan_tooltip"
    
    class Panels:
        """UI panel and label translation keys."""
        TOOLS_GROUP = "tools_group"
        COLOR_GROUP = "color_group"
        CANVAS_SIZE_GROUP = "canvas_size_group"
        ACTIONS_GROUP = "actions_group"
        WIDTH_LABEL = "width_label"
        HEIGHT_LABEL = "height_label"
        RESIZE_CANVAS = "resize_canvas"
        CLEAR_CANVAS = "clear_canvas"
        CHOOSE_COLOR = "choose_color"
        RECENT_COLORS = "recent_colors"
        CURRENT_COLOR_TOOLTIP = "current_color_tooltip"
        BACKGROUND_COLOR_TOOLTIP = "background_color_tooltip"
    
    class Dialogs:
        """Dialog title and message translation keys."""
        CHOOSE_COLOR_TITLE = "choose_color_title"
        NEW_FILE_TITLE = "new_file_title"
        NEW_FILE_MESSAGE = "new_file_message"
        OPEN_FILE_TITLE = "open_file_title"
        SAVE_FILE_TITLE = "save_file_title"
        EXPORT_PNG_TITLE = "export_png_title"
        LARGE_CANVAS_TITLE = "large_canvas_title"
        LARGE_CANVAS_MESSAGE = "large_canvas_message"
        INVALID_DIMENSIONS_TITLE = "invalid_dimensions_title"
        CLEAR_CANVAS_TITLE = "clear_canvas_title"
        CLEAR_CANVAS_MESSAGE = "clear_canvas_message"
        SUCCESS_TITLE = "success_title"
        FILE_SAVED_MESSAGE = "file_saved_message"
        PNG_EXPORTED_MESSAGE = "png_exported_message"
        ERROR_TITLE_TEMPLATE = "error_title_template"
    
    class Status:
        """Status bar message translation keys."""
        READY = "ready"
        UNDONE = "undone"
        REDONE = "redone"
        CANVAS_RESIZED = "canvas_resized"
        TOOL_CHANGED = "tool_changed"
        PIXEL_INFO = "pixel_info"
        FILE_OPENED = "file_opened"
        FILE_SAVED = "file_saved"
        FILE_EXPORTED = "file_exported"
    
    class Errors:
        """Error message translation keys."""
        COORDS_OUT_OF_BOUNDS = "coords_out_of_bounds"
        INVALID_COLOR = "invalid_color"
        INVALID_DIMENSIONS = "invalid_dimensions"
        DIMENSIONS_MUST_BE_INTEGERS = "dimensions_must_be_integers"
        DIMENSIONS_TOO_SMALL = "dimensions_too_small"
        DIMENSIONS_TOO_LARGE = "dimensions_too_large"
        FILE_PATH_EMPTY = "file_path_empty"
        FILE_NOT_EXISTS = "file_not_exists"
        PATH_NOT_FILE = "path_not_file"
        FILE_NOT_READABLE = "file_not_readable"
        DIRECTORY_NOT_EXISTS = "directory_not_exists"
        FILE_NOT_WRITABLE = "file_not_writable"
        DIRECTORY_NOT_WRITABLE = "directory_not_writable"
        SAVE_FAILED = "save_failed"
        EXPORT_FAILED = "export_failed"
    
    class FileFilters:
        """File dialog filter translation keys."""
        JSON_FILES = "json_files"
        PNG_FILES = "png_files"