"""Preferences dialog for application settings."""

from typing import Dict, Any, Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, 
    QLabel, QComboBox, QPushButton, QGroupBox, QCheckBox,
    QSpinBox, QMessageBox, QDialogButtonBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ...i18n import TranslationManager, tr_dialog, tr_panel, tr_pref, SUPPORTED_LANGUAGES
from ...constants import AppConstants
from ...styles import ModernDesignConstants, apply_primary_button_style, apply_secondary_button_style


class PreferencesDialog(QDialog):
    """Preferences dialog for application settings.
    
    Provides user interface for configuring application preferences including:
    - Language selection with instant preview
    - UI settings and appearance
    - Canvas defaults and performance settings
    
    Signals:
        settings_changed(dict): Emitted when settings are applied
        language_changed(str): Emitted when language selection changes
    """
    
    settings_changed = pyqtSignal(dict)
    language_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        """Initialize preferences dialog.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._translation_manager = TranslationManager.instance()
        self._current_settings = {}
        self._setup_ui()
        self._load_current_settings()
        
    def _setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle(tr_pref("preferences_title"))
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # Create tab widget
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Language tab
        language_tab = self._create_language_tab()
        tab_widget.addTab(language_tab, tr_pref("language_settings"))
        
        # UI tab 
        ui_tab = self._create_ui_tab()
        tab_widget.addTab(ui_tab, tr_pref("ui_settings"))
        
        # Canvas tab
        canvas_tab = self._create_canvas_tab()
        tab_widget.addTab(canvas_tab, tr_pref("canvas_settings"))
        
        # Button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.Apply
        )
        
        # Apply modern styling to dialog buttons
        ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        cancel_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)
        apply_button = button_box.button(QDialogButtonBox.StandardButton.Apply)
        
        apply_primary_button_style(ok_button)
        apply_secondary_button_style(cancel_button)
        apply_secondary_button_style(apply_button)
        
        button_box.accepted.connect(self._apply_and_close)
        button_box.rejected.connect(self.reject)
        apply_button.clicked.connect(self._apply_settings)
        
        layout.addWidget(button_box)
        
    def _create_language_tab(self) -> QWidget:
        """Create language settings tab.
        
        Returns:
            QWidget: Language settings tab widget
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Language selection group
        lang_group = QGroupBox(tr_pref("language_selection"))
        lang_layout = QVBoxLayout(lang_group)
        
        # Language selection label and combo
        lang_label = QLabel(tr_pref("interface_language"))
        lang_layout.addWidget(lang_label)
        
        self.language_combo = QComboBox()
        self._populate_language_combo()
        self.language_combo.currentTextChanged.connect(self._on_language_preview)
        lang_layout.addWidget(self.language_combo)
        
        # Language info
        info_label = QLabel(tr_pref("language_restart_note"))
        info_label.setFont(QFont("Arial", 8))
        info_label.setStyleSheet("color: #666666;")
        info_label.setWordWrap(True)
        lang_layout.addWidget(info_label)
        
        layout.addWidget(lang_group)
        layout.addStretch()
        
        return tab
        
    def _create_ui_tab(self) -> QWidget:
        """Create UI settings tab.
        
        Returns:
            QWidget: UI settings tab widget
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Theme settings (placeholder for future)
        theme_group = QGroupBox(tr_pref("appearance"))
        theme_layout = QVBoxLayout(theme_group)
        
        self.dark_mode_check = QCheckBox(tr_pref("enable_dark_mode"))
        self.dark_mode_check.setEnabled(False)  # Not implemented yet
        theme_layout.addWidget(self.dark_mode_check)
        
        layout.addWidget(theme_group)
        
        # Performance settings
        perf_group = QGroupBox(tr_pref("performance"))
        perf_layout = QVBoxLayout(perf_group)
        
        self.smooth_scroll_check = QCheckBox(tr_pref("smooth_scrolling"))
        perf_layout.addWidget(self.smooth_scroll_check)
        
        self.hardware_accel_check = QCheckBox(tr_pref("hardware_acceleration"))
        perf_layout.addWidget(self.hardware_accel_check)
        
        layout.addWidget(perf_group)
        layout.addStretch()
        
        return tab
        
    def _create_canvas_tab(self) -> QWidget:
        """Create canvas settings tab.
        
        Returns:
            QWidget: Canvas settings tab widget
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Default canvas settings
        defaults_group = QGroupBox(tr_pref("default_canvas"))
        defaults_layout = QVBoxLayout(defaults_group)
        
        # Default width
        width_layout = QHBoxLayout()
        width_layout.addWidget(QLabel(tr_pref("default_width")))
        self.default_width_spin = QSpinBox()
        self.default_width_spin.setRange(AppConstants.MIN_CANVAS_SIZE, AppConstants.MAX_CANVAS_SIZE)
        self.default_width_spin.setValue(AppConstants.DEFAULT_CANVAS_WIDTH)
        width_layout.addWidget(self.default_width_spin)
        width_layout.addStretch()
        defaults_layout.addLayout(width_layout)
        
        # Default height
        height_layout = QHBoxLayout()
        height_layout.addWidget(QLabel(tr_pref("default_height")))
        self.default_height_spin = QSpinBox()
        self.default_height_spin.setRange(AppConstants.MIN_CANVAS_SIZE, AppConstants.MAX_CANVAS_SIZE)
        self.default_height_spin.setValue(AppConstants.DEFAULT_CANVAS_HEIGHT)
        height_layout.addWidget(self.default_height_spin)
        height_layout.addStretch()
        defaults_layout.addLayout(height_layout)
        
        layout.addWidget(defaults_group)
        
        # Grid settings
        grid_group = QGroupBox(tr_pref("grid_settings"))
        grid_layout = QVBoxLayout(grid_group)
        
        self.show_grid_check = QCheckBox(tr_pref("show_grid"))
        grid_layout.addWidget(self.show_grid_check)
        
        layout.addWidget(grid_group)
        layout.addStretch()
        
        return tab
        
    def _populate_language_combo(self):
        """Populate language selection combo box."""
        current_language = self._translation_manager.get_current_language()
        
        for i, lang_info in enumerate(self._translation_manager.get_available_languages()):
            display_text = f"{lang_info['native_name']} ({lang_info['name']})"
            self.language_combo.addItem(display_text, lang_info['code'])
            
            if lang_info['code'] == current_language:
                self.language_combo.setCurrentIndex(i)
                
    def _on_language_preview(self):
        """Handle language selection for preview."""
        selected_code = self.language_combo.currentData()
        if selected_code and selected_code != self._translation_manager.get_current_language():
            # Emit signal for potential preview (could update dialog text)
            self.language_changed.emit(selected_code)
            
    def _load_current_settings(self):
        """Load current application settings."""
        self._current_settings = {
            'language': self._translation_manager.get_current_language(),
            'dark_mode': False,  # Placeholder
            'smooth_scrolling': True,  # Placeholder
            'hardware_acceleration': True,  # Placeholder
            'default_canvas_width': AppConstants.DEFAULT_CANVAS_WIDTH,
            'default_canvas_height': AppConstants.DEFAULT_CANVAS_HEIGHT,
            'show_grid': False  # Placeholder
        }
        
        # Update UI controls with current settings
        self.dark_mode_check.setChecked(self._current_settings['dark_mode'])
        self.smooth_scroll_check.setChecked(self._current_settings['smooth_scrolling'])
        self.hardware_accel_check.setChecked(self._current_settings['hardware_acceleration'])
        self.default_width_spin.setValue(self._current_settings['default_canvas_width'])
        self.default_height_spin.setValue(self._current_settings['default_canvas_height'])
        self.show_grid_check.setChecked(self._current_settings['show_grid'])
        
    def _get_settings_from_ui(self) -> Dict[str, Any]:
        """Get settings from UI controls.
        
        Returns:
            Dict containing current UI settings
        """
        return {
            'language': self.language_combo.currentData(),
            'dark_mode': self.dark_mode_check.isChecked(),
            'smooth_scrolling': self.smooth_scroll_check.isChecked(),
            'hardware_acceleration': self.hardware_accel_check.isChecked(),
            'default_canvas_width': self.default_width_spin.value(),
            'default_canvas_height': self.default_height_spin.value(),
            'show_grid': self.show_grid_check.isChecked()
        }
        
    def _apply_settings(self):
        """Apply current settings."""
        new_settings = self._get_settings_from_ui()
        
        # Check if language changed
        if new_settings['language'] != self._current_settings['language']:
            if self._translation_manager.set_language(new_settings['language']):
                QMessageBox.information(
                    self,
                    tr_pref("language_changed_title"),
                    tr_pref("language_changed_message")
                )
            else:
                QMessageBox.warning(
                    self,
                    tr_pref("language_error_title"),
                    tr_pref("language_error_message")
                )
                return
        
        # Store current settings
        self._current_settings = new_settings
        
        # Emit settings changed signal
        self.settings_changed.emit(new_settings)
        
    def _apply_and_close(self):
        """Apply settings and close dialog."""
        self._apply_settings()
        self.accept()
        
    def get_current_settings(self) -> Dict[str, Any]:
        """Get current settings.
        
        Returns:
            Dict containing current settings
        """
        return self._current_settings.copy()