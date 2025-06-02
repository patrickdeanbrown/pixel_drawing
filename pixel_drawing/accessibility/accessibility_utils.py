"""Accessibility utility functions and constants."""

from typing import Optional, Dict, Any
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget

from ..constants import AppConstants
from ..i18n import tr_panel, tr_dialog


class AccessibilityUtils:
    """Utility functions for accessibility enhancements."""
    
    # Accessibility constants
    MIN_TOUCH_TARGET_SIZE = 44  # Minimum 44x44px for touch accessibility
    FOCUS_OUTLINE_WIDTH = 2
    HIGH_CONTRAST_RATIO = 7.0  # WCAG AAA level
    NORMAL_CONTRAST_RATIO = 4.5  # WCAG AA level
    
    # High contrast color scheme
    HIGH_CONTRAST_COLORS = {
        'background': '#FFFFFF',
        'foreground': '#000000', 
        'focus': '#0000FF',
        'selection': '#FFFF00',
        'border': '#000000',
        'disabled': '#808080'
    }
    
    @staticmethod
    def get_color_name(color: QColor) -> str:
        """Get human-readable color name for screen readers.
        
        Args:
            color: QColor to describe
            
        Returns:
            Human-readable color description
        """
        hex_value = color.name().upper()
        
        # Common color names for better accessibility
        color_names = {
            '#000000': 'Black',
            '#FFFFFF': 'White', 
            '#FF0000': 'Red',
            '#00FF00': 'Green',
            '#0000FF': 'Blue',
            '#FFFF00': 'Yellow',
            '#FF00FF': 'Magenta',
            '#00FFFF': 'Cyan',
            '#808080': 'Gray',
            '#C0C0C0': 'Silver',
            '#800000': 'Maroon',
            '#008000': 'Dark Green',
            '#000080': 'Navy',
            '#808000': 'Olive',
            '#800080': 'Purple',
            '#008080': 'Teal',
            '#FFA500': 'Orange',
            '#FFC0CB': 'Pink'
        }
        
        if hex_value in color_names:
            return color_names[hex_value]
        
        # For custom colors, describe as RGB values
        return f"RGB {color.red()}, {color.green()}, {color.blue()}"
    
    @staticmethod
    def get_contrast_ratio(color1: QColor, color2: QColor) -> float:
        """Calculate contrast ratio between two colors.
        
        Args:
            color1: First color
            color2: Second color
            
        Returns:
            Contrast ratio (1.0 to 21.0)
        """
        def get_luminance(color: QColor) -> float:
            """Calculate relative luminance of a color."""
            def to_linear(channel: int) -> float:
                c = channel / 255.0
                return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
            
            r = to_linear(color.red())
            g = to_linear(color.green()) 
            b = to_linear(color.blue())
            
            return 0.2126 * r + 0.7152 * g + 0.0722 * b
        
        lum1 = get_luminance(color1)
        lum2 = get_luminance(color2)
        
        # Ensure lighter color is numerator
        if lum1 < lum2:
            lum1, lum2 = lum2, lum1
            
        return (lum1 + 0.05) / (lum2 + 0.05)
    
    @staticmethod
    def meets_contrast_requirement(color1: QColor, color2: QColor, level: str = "AA") -> bool:
        """Check if color combination meets WCAG contrast requirements.
        
        Args:
            color1: First color
            color2: Second color  
            level: WCAG level ("AA" or "AAA")
            
        Returns:
            True if contrast requirement is met
        """
        ratio = AccessibilityUtils.get_contrast_ratio(color1, color2)
        required_ratio = AccessibilityUtils.HIGH_CONTRAST_RATIO if level == "AAA" else AccessibilityUtils.NORMAL_CONTRAST_RATIO
        return ratio >= required_ratio
    
    @staticmethod
    def setup_accessible_widget(widget: QWidget, 
                               accessible_name: str,
                               accessible_description: Optional[str] = None,
                               role: Optional[str] = None) -> None:
        """Configure accessibility properties for a widget.
        
        Args:
            widget: Widget to configure
            accessible_name: Name for screen readers
            accessible_description: Optional detailed description
            role: Optional accessibility role (as string)
        """
        widget.setAccessibleName(accessible_name)
        
        if accessible_description:
            widget.setAccessibleDescription(accessible_description)
            
        # Note: QAccessible.Role usage removed for compatibility
        # Role setting would be handled through Qt accessibility system
    
    @staticmethod
    def setup_tool_button_accessibility(button: QWidget, 
                                       tool_name: str,
                                       shortcut: str,
                                       description: str) -> None:
        """Configure accessibility for tool buttons.
        
        Args:
            button: Tool button widget
            tool_name: Name of the tool
            shortcut: Keyboard shortcut
            description: Tool description
        """
        accessible_name = f"{tool_name} Tool"
        accessible_desc = f"{description}. Keyboard shortcut: {shortcut}"
        
        AccessibilityUtils.setup_accessible_widget(
            button,
            accessible_name,
            accessible_desc,
            "Button"
        )
        
        # Add shortcut information to what's this
        button.setWhatsThis(f"Use keyboard shortcut '{shortcut}' to activate {tool_name}")
    
    @staticmethod
    def setup_color_button_accessibility(button: QWidget, color: QColor) -> None:
        """Configure accessibility for color buttons.
        
        Args:
            button: Color button widget
            color: Color value
        """
        color_name = AccessibilityUtils.get_color_name(color)
        hex_value = color.name().upper()
        
        accessible_name = f"Color {color_name}"
        accessible_desc = f"Select color {color_name}, hex value {hex_value}"
        
        AccessibilityUtils.setup_accessible_widget(
            button,
            accessible_name, 
            accessible_desc,
            "Button"
        )
        
        # Update tooltip with accessible information
        button.setToolTip(f"{color_name} ({hex_value})")
    
    @staticmethod
    def setup_canvas_accessibility(canvas: QWidget, width: int, height: int) -> None:
        """Configure accessibility for the drawing canvas.
        
        Args:
            canvas: Canvas widget
            width: Canvas width in pixels
            height: Canvas height in pixels  
        """
        accessible_name = tr_panel("drawing_canvas")
        accessible_desc = tr_panel("canvas_description", width=width, height=height)
        
        AccessibilityUtils.setup_accessible_widget(
            canvas,
            accessible_name,
            accessible_desc,
            "Canvas"
        )
        
        # Set up keyboard navigation instructions
        instructions = tr_panel("canvas_keyboard_instructions")
        canvas.setWhatsThis(instructions)
    
    @staticmethod
    def announce_to_screen_reader(widget: QWidget, message: str) -> None:
        """Announce a message to screen readers.
        
        Args:
            widget: Widget to use for announcement
            message: Message to announce
        """
        # Update accessible name temporarily to trigger screen reader announcement
        original_name = widget.accessibleName()
        widget.setAccessibleName(f"{original_name} - {message}")
        
        # Reset after brief delay (handled by Qt accessibility system)
        # The temporary name change triggers the announcement
        
    @staticmethod
    def get_high_contrast_stylesheet() -> str:
        """Get high contrast CSS stylesheet.
        
        Returns:
            CSS stylesheet for high contrast mode
        """
        colors = AccessibilityUtils.HIGH_CONTRAST_COLORS
        
        return f"""
        QWidget {{
            background-color: {colors['background']};
            color: {colors['foreground']};
        }}
        
        QPushButton {{
            background-color: {colors['background']};
            color: {colors['foreground']};
            border: 2px solid {colors['border']};
            padding: 8px;
            min-width: 80px;
            min-height: 32px;
        }}
        
        QPushButton:hover {{
            background-color: {colors['selection']};
            color: {colors['foreground']};
        }}
        
        QPushButton:focus {{
            border: 3px solid {colors['focus']};
            outline: 2px solid {colors['focus']};
        }}
        
        QPushButton:pressed {{
            background-color: {colors['foreground']};
            color: {colors['background']};
        }}
        
        QPushButton:disabled {{
            color: {colors['disabled']};
            border-color: {colors['disabled']};
        }}
        
        QGroupBox {{
            border: 2px solid {colors['border']};
            border-radius: 5px;
            margin-top: 1ex;
            padding-top: 10px;
            font-weight: bold;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
            background-color: {colors['background']};
            color: {colors['foreground']};
        }}
        
        QSpinBox, QComboBox {{
            background-color: {colors['background']};
            color: {colors['foreground']};
            border: 2px solid {colors['border']};
            padding: 4px;
            min-height: 24px;
        }}
        
        QSpinBox:focus, QComboBox:focus {{
            border: 3px solid {colors['focus']};
        }}
        
        QLabel {{
            color: {colors['foreground']};
            font-weight: bold;
        }}
        
        QScrollArea {{
            border: 2px solid {colors['border']};
        }}
        """
    
    @staticmethod
    def is_high_contrast_enabled() -> bool:
        """Check if high contrast mode should be enabled.
        
        Returns:
            True if high contrast mode is enabled
        """
        # This would typically check system settings
        # For now, return False - can be extended with user preference
        return False
    
    @staticmethod
    def get_focus_stylesheet() -> str:
        """Get enhanced focus indicator stylesheet.
        
        Returns:
            CSS for enhanced focus indicators
        """
        return """
        *:focus {
            outline: 2px solid #0066CC;
            outline-offset: 2px;
        }
        
        QPushButton:focus {
            border: 2px solid #0066CC;
            background-color: #E6F3FF;
        }
        
        QSpinBox:focus, QComboBox:focus {
            border: 2px solid #0066CC;
        }
        """