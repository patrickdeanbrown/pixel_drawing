"""Translation manager for internationalization system."""

import os
from typing import Dict, List, Optional, Any
from PyQt6.QtCore import QTranslator, QLocale, QCoreApplication
from PyQt6.QtWidgets import QApplication

from .config import LanguageConfig, SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE, get_language_config
from ..utils.logging import log_info, log_error, log_debug


class TranslationManager:
    """Central manager for application translations.
    
    Handles loading, switching, and managing translations for the application.
    Implements singleton pattern to ensure consistent translation state.
    """
    
    _instance: Optional['TranslationManager'] = None
    
    def __init__(self):
        """Initialize translation manager."""
        if TranslationManager._instance is not None:
            raise RuntimeError("TranslationManager is a singleton. Use TranslationManager.instance()")
        
        self._current_locale: str = DEFAULT_LANGUAGE
        self._translators: Dict[str, QTranslator] = {}
        self._app: Optional[QApplication] = None
        self._translations_dir: str = os.path.join(os.path.dirname(__file__), "compiled")
        self._fallback_strings: Dict[str, Dict[str, str]] = {}
        
        # Load fallback strings (English)
        self._load_fallback_strings()
        
    @classmethod
    def instance(cls) -> 'TranslationManager':
        """Get singleton instance of TranslationManager."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def initialize(self, app: QApplication) -> None:
        """Initialize translation system with Qt application.
        
        Args:
            app: QApplication instance
        """
        self._app = app
        log_info("i18n", "Translation manager initialized")
        
        # Set default language
        self.set_language(self._detect_system_language())
    
    def _detect_system_language(self) -> str:
        """Detect system language and return supported language code.
        
        Returns:
            Language code for closest supported language
        """
        system_locale = QLocale.system().name()
        log_debug("i18n", f"System locale detected: {system_locale}")
        
        # Check for exact match
        for lang in SUPPORTED_LANGUAGES:
            if lang.code == system_locale:
                log_info("i18n", f"Using exact language match: {system_locale}")
                return system_locale
        
        # Check for language family match (e.g., en_GB -> en_US)
        system_lang = system_locale.split('_')[0]
        for lang in SUPPORTED_LANGUAGES:
            if lang.code.split('_')[0] == system_lang:
                log_info("i18n", f"Using language family match: {lang.code} for {system_locale}")
                return lang.code
        
        # Fall back to default
        log_info("i18n", f"No match found, using default language: {DEFAULT_LANGUAGE}")
        return DEFAULT_LANGUAGE
    
    def set_language(self, locale: str) -> bool:
        """Change application language at runtime.
        
        Args:
            locale: Language code to switch to
            
        Returns:
            True if language was successfully loaded, False otherwise
        """
        if not self._app:
            log_error("i18n", "Cannot set language: TranslationManager not initialized")
            return False
        
        if locale == self._current_locale:
            log_debug("i18n", f"Language {locale} already active")
            return True
        
        # Validate language is supported
        if locale not in [lang.code for lang in SUPPORTED_LANGUAGES]:
            log_error("i18n", f"Unsupported language: {locale}")
            return False
        
        # Remove current translator
        if self._current_locale in self._translators:
            self._app.removeTranslator(self._translators[self._current_locale])
        
        # Load new translator
        if self._load_translator(locale):
            self._current_locale = locale
            log_info("i18n", f"Language changed to: {locale}")
            return True
        else:
            log_error("i18n", f"Failed to load language: {locale}")
            return False
    
    def _load_translator(self, locale: str) -> bool:
        """Load translator for specified locale.
        
        Args:
            locale: Language code to load
            
        Returns:
            True if translator was loaded successfully
        """
        if locale in self._translators:
            # Translator already loaded, just install it
            self._app.installTranslator(self._translators[locale])
            return True
        
        # Create new translator
        translator = QTranslator()
        translation_file = os.path.join(self._translations_dir, f"{locale}.qm")
        
        if os.path.exists(translation_file):
            if translator.load(translation_file):
                self._translators[locale] = translator
                self._app.installTranslator(translator)
                log_debug("i18n", f"Loaded translation file: {translation_file}")
                return True
            else:
                log_error("i18n", f"Failed to load translation file: {translation_file}")
        else:
            log_debug("i18n", f"Translation file not found: {translation_file}")
            
            # For development/testing, allow English without .qm file
            if locale == DEFAULT_LANGUAGE:
                log_info("i18n", f"Using fallback strings for {locale}")
                return True
        
        return False
    
    def get_current_language(self) -> str:
        """Get current active language code.
        
        Returns:
            Current language code
        """
        return self._current_locale
    
    def get_available_languages(self) -> List[Dict[str, str]]:
        """Get list of available translation languages.
        
        Returns:
            List of dictionaries with language information
        """
        languages = []
        for lang in SUPPORTED_LANGUAGES:
            # Check if translation file exists (except for default language)
            translation_file = os.path.join(self._translations_dir, f"{lang.code}.qm")
            if lang.code == DEFAULT_LANGUAGE or os.path.exists(translation_file):
                languages.append({
                    "code": lang.code,
                    "name": lang.name,
                    "native_name": lang.native_name,
                    "is_rtl": lang.is_rtl
                })
        
        return languages
    
    def translate(self, context: str, key: str, **kwargs) -> str:
        """Translate string with optional formatting.
        
        Args:
            context: Translation context (e.g., 'toolbar', 'dialogs')
            key: Translation key
            **kwargs: Formatting arguments for string interpolation
            
        Returns:
            Translated and formatted string
        """
        if not self._app:
            # Fall back to English if not initialized
            return self._get_fallback_string(context, key, **kwargs)
        
        # Try Qt translation system first
        translated = QCoreApplication.translate(context, key)
        
        # If translation not found or same as key, use fallback
        if translated == key or not translated:
            translated = self._get_fallback_string(context, key, **kwargs)
        
        # Apply string formatting if arguments provided
        if kwargs:
            try:
                return translated.format(**kwargs)
            except (KeyError, ValueError) as e:
                log_error("i18n", f"String formatting failed for {context}.{key}: {e}")
                return translated
        
        return translated
    
    def _get_fallback_string(self, context: str, key: str, **kwargs) -> str:
        """Get fallback string from English translations.
        
        Args:
            context: Translation context
            key: Translation key
            **kwargs: Formatting arguments
            
        Returns:
            Fallback string or key if not found
        """
        if context in self._fallback_strings and key in self._fallback_strings[context]:
            string = self._fallback_strings[context][key]
            if kwargs:
                try:
                    return string.format(**kwargs)
                except (KeyError, ValueError):
                    return string
            return string
        else:
            log_debug("i18n", f"Fallback string not found: {context}.{key}")
            return key
    
    def _load_fallback_strings(self) -> None:
        """Load English fallback strings for development/testing."""
        # These serve as fallbacks and documentation for translators
        self._fallback_strings = {
            "window_titles": {
                "app_title": "Pixel Drawing - Retro Game Asset Creator",
                "app_with_file": "Pixel Drawing - {filename}"
            },
            "toolbar": {
                "new": "New",
                "open": "Open",
                "save": "Save",
                "save_as": "Save As",
                "export_png": "Export PNG",
                "undo": "Undo",
                "redo": "Redo"
            },
            "tools": {
                "brush": "Brush",
                "brush_tooltip": "Brush Tool (B)",
                "fill": "Fill Bucket",
                "fill_tooltip": "Fill Bucket Tool (F)",
                "eraser": "Eraser",
                "eraser_tooltip": "Eraser Tool (E)",
                "color_picker": "Color Picker",
                "color_picker_tooltip": "Color Picker Tool (I)",
                "pan": "Pan",
                "pan_tooltip": "Pan Tool (H)"
            },
            "panels": {
                "tools_group": "Tools",
                "color_group": "Color",
                "canvas_size_group": "Canvas Size",
                "actions_group": "Actions",
                "width_label": "Width:",
                "height_label": "Height:",
                "resize_canvas": "Resize Canvas",
                "clear_canvas": "Clear Canvas",
                "choose_color": "Choose Color",
                "recent_colors": "Recent Colors:",
                "current_color_tooltip": "Current Color - Click to choose new color",
                "background_color_tooltip": "Background Color (used by eraser tool)",
                "file_menu": "File",
                "edit_menu": "Edit", 
                "settings_menu": "Settings",
                "preferences": "Preferences...",
                "quit": "Quit"
            },
            "dialogs": {
                "choose_color_title": "Choose Color",
                "new_file_title": "New File",
                "new_file_message": "Are you sure? Unsaved changes will be lost.",
                "open_file_title": "Open Pixel Art File",
                "save_file_title": "Save Pixel Art File",
                "export_png_title": "Export as PNG",
                "large_canvas_title": "Large Canvas",
                "large_canvas_message": "Canvas size {width}x{height} may affect performance. Continue?",
                "invalid_dimensions_title": "Invalid Dimensions",
                "clear_canvas_title": "Clear Canvas",
                "clear_canvas_message": "Are you sure you want to clear the canvas?",
                "success_title": "Success",
                "file_saved_message": "File saved successfully!",
                "png_exported_message": "PNG exported successfully!",
                "error_title_template": "{operation} Error"
            },
            "status": {
                "ready": "Ready",
                "undone": "Undone",
                "redone": "Redone",
                "canvas_resized": "Canvas resized to {width}x{height}",
                "tool_changed": "Tool: {tool_id}",
                "pixel_info": "Pixel ({x}, {y}): {color}",
                "file_opened": "Opened: {filename}",
                "file_saved": "Saved: {filename}",
                "file_exported": "Exported: {filename}"
            },
            "errors": {
                "coords_out_of_bounds": "Coordinates out of bounds",
                "invalid_color": "Invalid color",
                "invalid_dimensions": "Invalid canvas dimensions",
                "dimensions_must_be_integers": "Canvas dimensions must be integers",
                "dimensions_too_small": "Canvas dimensions must be at least {min_size}x{min_size}",
                "dimensions_too_large": "Canvas dimensions cannot exceed {max_size}x{max_size}",
                "file_path_empty": "File path cannot be empty",
                "file_not_exists": "File does not exist: {path}",
                "path_not_file": "Path is not a file: {path}",
                "file_not_readable": "File is not readable: {path}",
                "directory_not_exists": "Directory does not exist: {path}",
                "file_not_writable": "File is not writable: {path}",
                "directory_not_writable": "Directory is not writable: {path}",
                "save_failed": "Failed to save file: {error}",
                "export_failed": "Failed to export PNG: {error}"
            },
            "file_filters": {
                "json_files": "JSON files (*.json)",
                "png_files": "PNG files (*.png)"
            },
            "preferences": {
                "preferences_title": "Preferences",
                "language_settings": "Language",
                "ui_settings": "Interface",
                "canvas_settings": "Canvas",
                "language_selection": "Language Selection",
                "interface_language": "Interface Language:",
                "language_restart_note": "Language changes take effect immediately.",
                "appearance": "Appearance",
                "enable_dark_mode": "Enable dark mode (coming soon)",
                "performance": "Performance",
                "smooth_scrolling": "Smooth scrolling",
                "hardware_acceleration": "Hardware acceleration",
                "default_canvas": "Default Canvas",
                "default_width": "Default Width:",
                "default_height": "Default Height:",
                "grid_settings": "Grid",
                "show_grid": "Show grid lines",
                "language_changed_title": "Language Changed",
                "language_changed_message": "The interface language has been changed successfully.",
                "language_error_title": "Language Error",
                "language_error_message": "Failed to change language. Please try again."
            }
        }