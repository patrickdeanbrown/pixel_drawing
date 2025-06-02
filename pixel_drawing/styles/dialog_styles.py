"""
Modern Dialog Styling for Qt File Dialogs and Color Picker
Applies Material Design principles to system dialogs.
"""

from PyQt6.QtWidgets import QDialog, QFileDialog, QColorDialog, QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor

from .design_constants import ModernDesignConstants


class ModernDialogStyler:
    """Applies modern styling to Qt dialogs."""
    
    @staticmethod
    def style_file_dialog(dialog: QFileDialog) -> None:
        """Apply modern styling to file dialogs.
        
        Args:
            dialog: QFileDialog to style
        """
        dialog.setStyleSheet("""
            QFileDialog {
                background-color: #FFFFFF;
                color: #202124;
                font-family: "Segoe UI", "Roboto", sans-serif;
            }
            
            QFileDialog QListView {
                background-color: #FFFFFF;
                border: 1px solid #E8EAED;
                border-radius: 4px;
                selection-background-color: rgba(160, 32, 240, 0.12);
                outline: none;
            }
            
            QFileDialog QTreeView {
                background-color: #FFFFFF;
                border: 1px solid #E8EAED;
                border-radius: 4px;
                selection-background-color: rgba(160, 32, 240, 0.12);
                outline: none;
            }
            
            QFileDialog QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #DADCE0;
                border-radius: 6px;
                padding: 8px 16px;
                color: #202124;
                font-weight: 500;
                min-width: 64px;
            }
            
            QFileDialog QPushButton:hover {
                background-color: #E8F0FE;
                border-color: #A020F0;
                color: #A020F0;
            }
            
            QFileDialog QPushButton[default="true"] {
                background-color: #A020F0;
                color: #FFFFFF;
                border-color: #A020F0;
            }
            
            QFileDialog QPushButton[default="true"]:hover {
                background-color: #8C1AC9;
                border-color: #8C1AC9;
            }
            
            QFileDialog QLineEdit {
                background-color: #FFFFFF;
                border: 1px solid #DADCE0;
                border-radius: 4px;
                padding: 8px 12px;
                color: #202124;
                selection-background-color: #A020F0;
                selection-color: #FFFFFF;
            }
            
            QFileDialog QLineEdit:focus {
                border-color: #A020F0;
                outline: none;
                box-shadow: 0 0 0 2px rgba(160, 32, 240, 0.2);
            }
            
            QFileDialog QComboBox {
                background-color: #FFFFFF;
                border: 1px solid #DADCE0;
                border-radius: 4px;
                padding: 8px 12px;
                color: #202124;
                min-width: 120px;
            }
            
            QFileDialog QComboBox:hover {
                border-color: #5F6368;
            }
            
            QFileDialog QComboBox:focus {
                border-color: #A020F0;
                outline: none;
            }
            
            QFileDialog QLabel {
                color: #202124;
                font-weight: 500;
            }
        """)
        
        # Set modern fonts
        font = ModernDesignConstants.get_primary_font(
            size=ModernDesignConstants.FONT_SIZE_REGULAR
        )
        dialog.setFont(font)
    
    @staticmethod
    def style_color_dialog(dialog: QColorDialog) -> None:
        """Apply modern styling to color dialogs.
        
        Args:
            dialog: QColorDialog to style
        """
        dialog.setStyleSheet("""
            QColorDialog {
                background-color: #FFFFFF;
                color: #202124;
                font-family: "Segoe UI", "Roboto", sans-serif;
            }
            
            QColorDialog QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #DADCE0;
                border-radius: 6px;
                padding: 8px 16px;
                color: #202124;
                font-weight: 500;
                min-width: 64px;
            }
            
            QColorDialog QPushButton:hover {
                background-color: #E8F0FE;
                border-color: #A020F0;
                color: #A020F0;
            }
            
            QColorDialog QPushButton[default="true"] {
                background-color: #A020F0;
                color: #FFFFFF;
                border-color: #A020F0;
            }
            
            QColorDialog QPushButton[default="true"]:hover {
                background-color: #8C1AC9;
                border-color: #8C1AC9;
            }
            
            QColorDialog QSpinBox {
                background-color: #FFFFFF;
                border: 1px solid #DADCE0;
                border-radius: 4px;
                padding: 4px 8px;
                color: #202124;
                selection-background-color: #A020F0;
                selection-color: #FFFFFF;
            }
            
            QColorDialog QSpinBox:focus {
                border-color: #A020F0;
                outline: none;
            }
            
            QColorDialog QLineEdit {
                background-color: #FFFFFF;
                border: 1px solid #DADCE0;
                border-radius: 4px;
                padding: 8px 12px;
                color: #202124;
                selection-background-color: #A020F0;
                selection-color: #FFFFFF;
            }
            
            QColorDialog QLineEdit:focus {
                border-color: #A020F0;
                outline: none;
            }
            
            QColorDialog QLabel {
                color: #202124;
                font-weight: 500;
            }
            
            QColorDialog QTabWidget::pane {
                border: 1px solid #E8EAED;
                border-radius: 4px;
                background-color: #FFFFFF;
            }
            
            QColorDialog QTabBar::tab {
                background-color: #F8F9FA;
                border: 1px solid #E8EAED;
                border-bottom: none;
                border-radius: 4px 4px 0 0;
                padding: 8px 16px;
                color: #5F6368;
                font-weight: 500;
            }
            
            QColorDialog QTabBar::tab:selected {
                background-color: #FFFFFF;
                color: #A020F0;
                border-color: #A020F0;
            }
            
            QColorDialog QTabBar::tab:hover {
                background-color: #E8F0FE;
                color: #A020F0;
            }
        """)
        
        # Set modern fonts
        font = ModernDesignConstants.get_primary_font(
            size=ModernDesignConstants.FONT_SIZE_REGULAR
        )
        dialog.setFont(font)
    
    @staticmethod
    def style_message_box(dialog: QDialog) -> None:
        """Apply modern styling to message boxes.
        
        Args:
            dialog: QDialog (message box) to style
        """
        dialog.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
                color: #202124;
                font-family: "Segoe UI", "Roboto", sans-serif;
                border: 1px solid #E8EAED;
                border-radius: 8px;
            }
            
            QDialog QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #DADCE0;
                border-radius: 6px;
                padding: 8px 16px;
                color: #202124;
                font-weight: 500;
                min-width: 64px;
                min-height: 32px;
            }
            
            QDialog QPushButton:hover {
                background-color: #E8F0FE;
                border-color: #A020F0;
                color: #A020F0;
            }
            
            QDialog QPushButton[default="true"] {
                background-color: #A020F0;
                color: #FFFFFF;
                border-color: #A020F0;
            }
            
            QDialog QPushButton[default="true"]:hover {
                background-color: #8C1AC9;
                border-color: #8C1AC9;
            }
            
            QDialog QLabel {
                color: #202124;
                font-size: 14px;
                padding: 16px;
            }
        """)
        
        # Set modern fonts
        font = ModernDesignConstants.get_primary_font(
            size=ModernDesignConstants.FONT_SIZE_REGULAR
        )
        dialog.setFont(font)


def create_styled_file_dialog(parent=None, caption="", directory="", filter="") -> QFileDialog:
    """Create a styled file dialog.
    
    Args:
        parent: Parent widget
        caption: Dialog caption
        directory: Initial directory
        filter: File filter
        
    Returns:
        Styled QFileDialog
    """
    dialog = QFileDialog(parent, caption, directory, filter)
    ModernDialogStyler.style_file_dialog(dialog)
    return dialog


def create_styled_color_dialog(initial_color=None, parent=None) -> QColorDialog:
    """Create a styled color dialog.
    
    Args:
        initial_color: Initial color selection
        parent: Parent widget
        
    Returns:
        Styled QColorDialog
    """
    dialog = QColorDialog(parent)
    if initial_color:
        dialog.setCurrentColor(initial_color)
    ModernDialogStyler.style_color_dialog(dialog)
    return dialog


def show_styled_file_dialog(parent=None, caption="", directory="", filter="", mode="open"):
    """Show a styled file dialog and return the result.
    
    Args:
        parent: Parent widget
        caption: Dialog caption
        directory: Initial directory
        filter: File filter
        mode: 'open' or 'save'
        
    Returns:
        Tuple of (file_path, selected_filter)
    """
    dialog = create_styled_file_dialog(parent, caption, directory, filter)
    
    if mode == "save":
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        dialog.setDefaultSuffix("json")
    else:
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
    
    if dialog.exec() == QDialog.DialogCode.Accepted:
        files = dialog.selectedFiles()
        if files:
            return files[0], dialog.selectedNameFilter()
    
    return "", ""


def show_styled_color_dialog(initial_color, parent=None):
    """Show a styled color dialog and return the selected color.
    
    Args:
        initial_color: Initial color
        parent: Parent widget
        
    Returns:
        Selected QColor or None if cancelled
    """
    dialog = create_styled_color_dialog(initial_color, parent)
    
    if dialog.exec() == QDialog.DialogCode.Accepted:
        return dialog.currentColor()
    
    return None