"""Custom color button widget for the pixel drawing application."""

from PyQt6.QtWidgets import QPushButton
from PyQt6.QtGui import QColor

from ...constants import AppConstants


class ColorButton(QPushButton):
    """Custom color button widget with visual feedback and hover effects.
    
    A specialized QPushButton that displays a solid color and provides
    visual feedback when hovered. Used in the recent colors palette to
    allow quick color selection from previously used colors.
    
    Features:
        - Displays solid color background
        - Hover effects with border highlighting
        - Automatic stylesheet updates when color changes
        - Fixed size for consistent layout in color palette
    """
    
    def __init__(self, color: QColor, parent=None):
        super().__init__(parent)
        self.color = color
        self.setFixedSize(AppConstants.COLOR_BUTTON_SIZE, AppConstants.COLOR_BUTTON_SIZE)
        self._update_stylesheet()
    
    def _update_stylesheet(self) -> None:
        """Update button appearance with current color and hover effects.
        
        Applies CSS styling to display the button's color as background
        and configures hover state with border highlighting.
        """
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.color.name().upper()};
                border: 1px solid {AppConstants.BORDER_COLOR};
                border-radius: 2px;
            }}
            QPushButton:hover {{
                border: 3px solid {AppConstants.HOVER_COLOR};
            }}
        """)
    
    def set_color(self, color: QColor) -> None:
        """Update the button's displayed color.
        
        Args:
            color: New color to display on the button
        """
        self.color = color
        self._update_stylesheet()