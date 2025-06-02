"""
Style Manager for Modern UI Theme
Handles loading, applying, and managing UI themes for the pixel art application.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor

from .design_constants import ModernDesignConstants, ColorThemes


class StyleManager(QObject):
    """Manages application styling and theme switching."""
    
    # Signals
    theme_changed = pyqtSignal(str)  # theme_name
    
    def __init__(self, app: QApplication):
        super().__init__()
        self.app = app
        self.current_theme = "light"
        self.stylesheet_cache: Dict[str, str] = {}
        self.styles_dir = Path(__file__).parent
        
    def load_theme(self, theme_name: str = "modern") -> bool:
        """Load and apply a theme to the application.
        
        Args:
            theme_name: Name of the theme to load ('modern', 'dark', 'high_contrast')
            
        Returns:
            True if theme was loaded successfully, False otherwise
        """
        try:
            if theme_name not in self.stylesheet_cache:
                stylesheet = self._load_stylesheet(theme_name)
                if stylesheet:
                    self.stylesheet_cache[theme_name] = stylesheet
                else:
                    return False
            
            # Apply the stylesheet
            self.app.setStyleSheet(self.stylesheet_cache[theme_name])
            
            # Set application font
            self._set_application_font()
            
            # Set application palette for system colors
            self._set_application_palette(theme_name)
            
            self.current_theme = theme_name
            self.theme_changed.emit(theme_name)
            
            return True
            
        except Exception as e:
            print(f"Error loading theme '{theme_name}': {e}")
            return False
    
    def _load_stylesheet(self, theme_name: str) -> Optional[str]:
        """Load stylesheet from file.
        
        Args:
            theme_name: Name of the theme
            
        Returns:
            Stylesheet content or None if failed
        """
        # Map theme names to files
        theme_files = {
            'modern': 'modern_theme.qss',
            'light': 'modern_theme.qss',  # Same as modern for now
            'dark': 'dark_theme.qss',
            'high_contrast': 'high_contrast_theme.qss'
        }
        
        filename = theme_files.get(theme_name, 'modern_theme.qss')
        file_path = self.styles_dir / filename
        
        if not file_path.exists():
            # For now, if dark or high contrast don't exist, use modern with modifications
            if theme_name in ['dark', 'high_contrast']:
                return self._generate_variant_stylesheet(theme_name)
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Process any CSS variables or theme-specific modifications
            return self._process_stylesheet(content, theme_name)
            
        except Exception as e:
            print(f"Error reading stylesheet file '{file_path}': {e}")
            return None
    
    def _process_stylesheet(self, content: str, theme_name: str) -> str:
        """Process stylesheet content for theme-specific modifications.
        
        Args:
            content: Raw stylesheet content
            theme_name: Theme name for context
            
        Returns:
            Processed stylesheet content
        """
        # For now, return content as-is
        # In the future, this could handle CSS variable substitution
        return content
    
    def _generate_variant_stylesheet(self, theme_name: str) -> str:
        """Generate a variant stylesheet for themes that don't have separate files.
        
        Args:
            theme_name: Theme variant to generate
            
        Returns:
            Generated stylesheet content
        """
        base_stylesheet = self._load_stylesheet('modern')
        if not base_stylesheet:
            return ""
        
        if theme_name == 'dark':
            return self._apply_dark_theme_modifications(base_stylesheet)
        elif theme_name == 'high_contrast':
            return self._apply_high_contrast_modifications(base_stylesheet)
        
        return base_stylesheet
    
    def _apply_dark_theme_modifications(self, stylesheet: str) -> str:
        """Apply dark theme modifications to base stylesheet."""
        # This is a simplified approach - in production you'd want more sophisticated processing
        dark_replacements = {
            '#F8F9FA': '#1F1F1F',  # Main background
            '#FFFFFF': '#2D2D2D',  # Panel background
            '#202124': '#E8EAED',  # Primary text
            '#5F6368': '#9AA0A6',  # Secondary text
            '#E8EAED': '#5F6368',  # Light borders
            '#DADCE0': '#5F6368',  # Medium borders
        }
        
        modified = stylesheet
        for old_color, new_color in dark_replacements.items():
            modified = modified.replace(old_color, new_color)
        
        return modified
    
    def _apply_high_contrast_modifications(self, stylesheet: str) -> str:
        """Apply high contrast theme modifications to base stylesheet."""
        # High contrast theme with stark black/white/yellow
        hc_replacements = {
            '#F8F9FA': '#000000',  # Main background
            '#FFFFFF': '#000000',  # Panel background
            '#202124': '#FFFFFF',  # Primary text
            '#A020F0': '#FFFF00',  # Primary accent (yellow for visibility)
            '#E8EAED': '#FFFFFF',  # Borders
            '#DADCE0': '#FFFFFF',  # Borders
        }
        
        modified = stylesheet
        for old_color, new_color in hc_replacements.items():
            modified = modified.replace(old_color, new_color)
        
        return modified
    
    def _set_application_font(self) -> None:
        """Set the application's default font."""
        font = ModernDesignConstants.get_primary_font(
            size=ModernDesignConstants.FONT_SIZE_REGULAR,
            weight=ModernDesignConstants.FONT_WEIGHT_NORMAL
        )
        self.app.setFont(font)
    
    def _set_application_palette(self, theme_name: str) -> None:
        """Set the application's color palette.
        
        Args:
            theme_name: Theme name to determine palette
        """
        palette = QPalette()
        
        if theme_name == 'dark':
            theme_colors = ColorThemes.DARK
        elif theme_name == 'high_contrast':
            theme_colors = ColorThemes.HIGH_CONTRAST
        else:
            theme_colors = ColorThemes.LIGHT
        
        # Set palette colors
        palette.setColor(QPalette.ColorRole.Window, QColor(theme_colors['background']))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(theme_colors['text']))
        palette.setColor(QPalette.ColorRole.Base, QColor(theme_colors['panel']))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(theme_colors['background']))
        palette.setColor(QPalette.ColorRole.Text, QColor(theme_colors['text']))
        palette.setColor(QPalette.ColorRole.Button, QColor(theme_colors['panel']))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(theme_colors['text']))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(ModernDesignConstants.PRIMARY_PURPLE))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(ModernDesignConstants.TEXT_INVERSE))
        
        self.app.setPalette(palette)
    
    def apply_widget_style(self, widget: QWidget, style_class: str) -> None:
        """Apply a specific style class to a widget.
        
        Args:
            widget: Widget to style
            style_class: CSS class name to apply
        """
        current_classes = widget.property('class') or ""
        if style_class not in current_classes:
            new_classes = f"{current_classes} {style_class}".strip()
            widget.setProperty('class', new_classes)
            # Force style refresh
            widget.style().unpolish(widget)
            widget.style().polish(widget)
    
    def remove_widget_style(self, widget: QWidget, style_class: str) -> None:
        """Remove a specific style class from a widget.
        
        Args:
            widget: Widget to modify
            style_class: CSS class name to remove
        """
        current_classes = widget.property('class') or ""
        new_classes = current_classes.replace(style_class, '').strip()
        widget.setProperty('class', new_classes)
        # Force style refresh
        widget.style().unpolish(widget)
        widget.style().polish(widget)
    
    def set_widget_object_name(self, widget: QWidget, name: str) -> None:
        """Set object name for specific QSS targeting.
        
        Args:
            widget: Widget to name
            name: Object name for QSS selectors
        """
        widget.setObjectName(name)
    
    def get_color(self, color_name: str) -> QColor:
        """Get a themed color by name.
        
        Args:
            color_name: Color constant name (e.g., 'PRIMARY_PURPLE')
            
        Returns:
            QColor object
        """
        color_map = {
            'PRIMARY_PURPLE': ModernDesignConstants.PRIMARY_PURPLE,
            'PRIMARY_PURPLE_DARK': ModernDesignConstants.PRIMARY_PURPLE_DARK,
            'BG_MAIN': ModernDesignConstants.BG_MAIN,
            'BG_PANEL': ModernDesignConstants.BG_PANEL,
            'TEXT_PRIMARY': ModernDesignConstants.TEXT_PRIMARY,
            'TEXT_SECONDARY': ModernDesignConstants.TEXT_SECONDARY,
            'BORDER_LIGHT': ModernDesignConstants.BORDER_LIGHT,
            'ERROR': ModernDesignConstants.ERROR,
            'SUCCESS': ModernDesignConstants.SUCCESS,
            'WARNING': ModernDesignConstants.WARNING,
        }
        
        color_hex = color_map.get(color_name, ModernDesignConstants.TEXT_PRIMARY)
        return QColor(color_hex)
    
    def refresh_styles(self) -> None:
        """Refresh styles for all widgets."""
        if self.current_theme in self.stylesheet_cache:
            self.app.setStyleSheet(self.stylesheet_cache[self.current_theme])
    
    def clear_cache(self) -> None:
        """Clear the stylesheet cache."""
        self.stylesheet_cache.clear()
    
    def get_current_theme(self) -> str:
        """Get the name of the currently active theme."""
        return self.current_theme
    
    def is_dark_theme(self) -> bool:
        """Check if the current theme is a dark theme."""
        return self.current_theme in ['dark', 'high_contrast']


# Global style manager instance (will be initialized by the application)
_style_manager: Optional[StyleManager] = None


def get_style_manager() -> Optional[StyleManager]:
    """Get the global style manager instance."""
    return _style_manager


def initialize_style_manager(app: QApplication) -> StyleManager:
    """Initialize the global style manager.
    
    Args:
        app: QApplication instance
        
    Returns:
        StyleManager instance
    """
    global _style_manager
    _style_manager = StyleManager(app)
    return _style_manager


def apply_modern_theme() -> bool:
    """Apply the modern theme to the application.
    
    Returns:
        True if successful, False otherwise
    """
    if _style_manager:
        return _style_manager.load_theme('modern')
    return False


def apply_tool_button_style(button: QWidget) -> None:
    """Apply tool button styling to a widget.
    
    Args:
        button: Button widget to style
    """
    if _style_manager:
        _style_manager.apply_widget_style(button, 'tool_button')


def apply_primary_button_style(button: QWidget) -> None:
    """Apply primary button styling to a widget.
    
    Args:
        button: Button widget to style
    """
    if _style_manager:
        _style_manager.apply_widget_style(button, 'primary')


def apply_secondary_button_style(button: QWidget) -> None:
    """Apply secondary button styling to a widget.
    
    Args:
        button: Button widget to style
    """
    if _style_manager:
        _style_manager.apply_widget_style(button, 'secondary')


def apply_danger_button_style(button: QWidget) -> None:
    """Apply danger button styling to a widget.
    
    Args:
        button: Button widget to style
    """
    if _style_manager:
        _style_manager.apply_widget_style(button, 'danger')