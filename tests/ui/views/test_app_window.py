"""
UI tests for the main PixelDrawingApp window using pytest-qt.

These tests verify the main application window behavior, menu interactions,
toolbar functionality, and overall application integration.
"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path

try:
    from PyQt6.QtWidgets import QApplication, QMessageBox, QFileDialog, QColorDialog
    from PyQt6.QtCore import Qt, QPoint
    from PyQt6.QtGui import QColor, QKeyEvent, QAction
    from PyQt6.QtTest import QTest
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    pytest.skip("PyQt6 not available", allow_module_level=True)

from pixel_drawing.views.app import PixelDrawingApp
from pixel_drawing.models import PixelArtModel
from pixel_drawing.services import FileService


# ============================================================================
# Application Window Initialization Tests
# ============================================================================

@pytest.mark.ui
class TestAppWindowInitialization:
    """Test main application window initialization."""
    
    def test_app_window_default_initialization(self, qtbot):
        """Test app window initializes with default parameters."""
        app = PixelDrawingApp()
        qtbot.add_widget(app)
        
        assert app.isVisible() == False  # Not shown yet
        assert app._model is not None
        assert app._file_service is not None
        
        app.show()
        qtbot.wait_for_window_shown(app)
        assert app.isVisible()
        
    def test_app_window_custom_initialization(self, qtbot, ui_model, ui_file_service):
        """Test app window initializes with custom components."""
        app = PixelDrawingApp(model=ui_model, file_service=ui_file_service)
        qtbot.add_widget(app)
        
        assert app._model == ui_model
        assert app._file_service == ui_file_service
        
    def test_app_window_ui_components(self, qtbot, app_window):
        """Test app window has all required UI components."""
        app = app_window
        
        # Check main components exist
        assert hasattr(app, '_canvas')
        assert hasattr(app, '_toolbar')
        assert hasattr(app, '_side_panel')
        assert hasattr(app, '_status_bar')
        
        # Check components are properly set up
        assert app._canvas is not None
        assert app._toolbar is not None
        assert app._side_panel is not None
        assert app._status_bar is not None
        
    def test_app_window_title(self, qtbot, app_window):
        """Test app window has correct title."""
        app = app_window
        title = app.windowTitle()
        assert "Pixel Drawing" in title
        
    def test_app_window_menu_bar(self, qtbot, app_window):
        """Test app window has menu bar with required menus."""
        app = app_window
        menu_bar = app.menuBar()
        
        assert menu_bar is not None
        
        # Check for expected menus
        menu_actions = [action.text() for action in menu_bar.actions()]
        assert any("File" in text for text in menu_actions)
        assert any("Edit" in text for text in menu_actions)


# ============================================================================
# Menu and Action Tests
# ============================================================================

@pytest.mark.ui
class TestAppWindowMenus:
    """Test menu functionality and actions."""
    
    def test_file_menu_actions(self, qtbot, app_window):
        """Test file menu contains expected actions."""
        app = app_window
        
        # Find file menu
        file_menu = None
        for action in app.menuBar().actions():
            if "File" in action.text():
                file_menu = action.menu()
                break
        
        assert file_menu is not None
        
        # Check for expected actions
        action_texts = [action.text() for action in file_menu.actions()]
        assert any("New" in text for text in action_texts)
        assert any("Open" in text for text in action_texts)
        assert any("Save" in text for text in action_texts)
        
    def test_new_file_action(self, qtbot, app_window, mock_message_box):
        """Test new file action creates fresh canvas."""
        app = app_window
        
        # Add some pixels first
        app._model.set_pixel(1, 1, QColor(255, 0, 0))
        
        # Trigger new file
        new_action = app._find_action("New")
        if new_action:
            new_action.trigger()
            
            # Should show confirmation dialog for unsaved changes
            mock_message_box.question.assert_called()
    
    @patch('pixel_drawing.views.app.QFileDialog')
    def test_open_file_action(self, mock_dialog, qtbot, app_window, temp_dir):
        """Test open file action opens file dialog."""
        app = app_window
        
        # Mock file dialog to return a test file
        test_file = temp_dir / "test.json"
        test_file.write_text('{"width": 8, "height": 8, "pixels": {}}')
        
        mock_dialog.getOpenFileName.return_value = (str(test_file), "JSON files (*.json)")
        
        # Trigger open action
        open_action = app._find_action("Open")
        if open_action:
            open_action.trigger()
            
            mock_dialog.getOpenFileName.assert_called()
    
    @patch('pixel_drawing.views.app.QFileDialog')
    def test_save_file_action(self, mock_dialog, qtbot, app_window, temp_dir):
        """Test save file action opens save dialog."""
        app = app_window
        
        # Mock file dialog
        test_file = temp_dir / "save_test.json"
        mock_dialog.getSaveFileName.return_value = (str(test_file), "JSON files (*.json)")
        
        # Trigger save action
        save_action = app._find_action("Save")
        if save_action:
            save_action.trigger()
            
            mock_dialog.getSaveFileName.assert_called()
    
    def test_edit_menu_actions(self, qtbot, app_window):
        """Test edit menu contains expected actions."""
        app = app_window
        
        # Find edit menu
        edit_menu = None
        for action in app.menuBar().actions():
            if "Edit" in action.text():
                edit_menu = action.menu()
                break
        
        if edit_menu:
            action_texts = [action.text() for action in edit_menu.actions()]
            assert any("Undo" in text for text in action_texts)
            assert any("Redo" in text for text in action_texts)


# ============================================================================
# Toolbar Tests
# ============================================================================

@pytest.mark.ui
class TestAppWindowToolbar:
    """Test toolbar functionality."""
    
    def test_toolbar_exists(self, qtbot, app_window):
        """Test toolbar is present and visible."""
        app = app_window
        
        toolbar = app._toolbar
        assert toolbar is not None
        assert toolbar.isVisible()
        
    def test_toolbar_tool_buttons(self, qtbot, app_window):
        """Test toolbar contains tool buttons."""
        app = app_window
        
        # Look for tool buttons in toolbar
        toolbar = app._toolbar
        if hasattr(toolbar, 'actions'):
            actions = toolbar.actions()
            assert len(actions) > 0
        
        # Or check for specific tool buttons if they exist
        if hasattr(app, '_tool_buttons'):
            assert len(app._tool_buttons) > 0
    
    def test_toolbar_file_buttons(self, qtbot, app_window):
        """Test toolbar contains file operation buttons."""
        app = app_window
        
        # Check for file operation buttons
        toolbar = app._toolbar
        
        # This test depends on the actual toolbar implementation
        # Adjust based on how toolbar is structured in your app
        if hasattr(toolbar, 'actions'):
            action_texts = [action.text() for action in toolbar.actions() if action.text()]
            # Look for common file operations
            expected_actions = ["New", "Open", "Save"]
            found_actions = [action for action in expected_actions 
                           if any(action in text for text in action_texts)]
            assert len(found_actions) > 0


# ============================================================================
# Side Panel Tests
# ============================================================================

@pytest.mark.ui
class TestAppWindowSidePanel:
    """Test side panel functionality."""
    
    def test_side_panel_exists(self, qtbot, app_window):
        """Test side panel is present."""
        app = app_window
        
        side_panel = app._side_panel
        assert side_panel is not None
        
    def test_side_panel_color_controls(self, qtbot, app_window):
        """Test side panel has color selection controls."""
        app = app_window
        side_panel = app._side_panel
        
        # Check for color-related controls
        # This depends on your side panel implementation
        if hasattr(side_panel, '_current_color_button'):
            assert side_panel._current_color_button is not None
    
    def test_side_panel_canvas_controls(self, qtbot, app_window):
        """Test side panel has canvas size controls."""
        app = app_window
        side_panel = app._side_panel
        
        # Check for canvas size controls
        if hasattr(side_panel, '_width_spinbox'):
            assert side_panel._width_spinbox is not None
        if hasattr(side_panel, '_height_spinbox'):
            assert side_panel._height_spinbox is not None
    
    @patch('pixel_drawing.views.app.QColorDialog')
    def test_color_selection_dialog(self, mock_dialog, qtbot, app_window):
        """Test color selection opens color dialog."""
        app = app_window
        
        # Mock color dialog
        mock_dialog.getColor.return_value = QColor(255, 0, 0)
        
        # Try to trigger color selection
        side_panel = app._side_panel
        if hasattr(side_panel, '_current_color_button'):
            qtbot.mouse_click(side_panel._current_color_button, Qt.MouseButton.LeftButton)
            mock_dialog.getColor.assert_called()


# ============================================================================
# Canvas Integration Tests
# ============================================================================

@pytest.mark.ui
class TestAppWindowCanvasIntegration:
    """Test integration between app window and canvas."""
    
    def test_canvas_is_embedded(self, qtbot, app_window):
        """Test canvas is properly embedded in main window."""
        app = app_window
        
        canvas = app._canvas
        assert canvas is not None
        assert canvas.parent() == app or canvas.parent().parent() == app
        
    def test_canvas_receives_mouse_events(self, qtbot, app_window, test_colors):
        """Test canvas receives mouse events through app window."""
        app = app_window
        canvas = app._canvas
        
        # Ensure canvas is focused and visible
        canvas.setFocus()
        assert canvas.isVisible()
        
        # Simulate drawing on canvas
        canvas.set_current_tool("brush")
        canvas.current_color = test_colors['red']
        
        pos = QPoint(32, 32)  # Assuming reasonable canvas position
        qtbot.mouse_click(canvas, Qt.MouseButton.LeftButton, pos=pos)
        
        # Verify the click was processed
        pixel_x, pixel_y = canvas.get_pixel_coords(pos)
        if 0 <= pixel_x < canvas._model.width and 0 <= pixel_y < canvas._model.height:
            # Should have drawn something
            assert canvas._model.get_pixel(pixel_x, pixel_y) == test_colors['red']
    
    def test_canvas_keyboard_focus(self, qtbot, app_window):
        """Test canvas can receive keyboard focus in app window."""
        app = app_window
        canvas = app._canvas
        
        # Set focus to canvas
        canvas.setFocus()
        qtbot.wait(50)  # Allow focus to settle
        
        assert canvas.hasFocus()
        
        # Test keyboard interaction
        qtbot.key_click(canvas, Qt.Key.Key_B)  # Brush tool shortcut
        assert canvas.get_current_tool_id() == "brush"


# ============================================================================
# Status Bar Tests
# ============================================================================

@pytest.mark.ui
class TestAppWindowStatusBar:
    """Test status bar functionality."""
    
    def test_status_bar_exists(self, qtbot, app_window):
        """Test status bar is present."""
        app = app_window
        
        status_bar = app._status_bar
        assert status_bar is not None
        assert status_bar.isVisible()
        
    def test_status_bar_updates(self, qtbot, app_window):
        """Test status bar updates with canvas information."""
        app = app_window
        canvas = app._canvas
        
        # Hover over canvas to trigger status update
        pos = QPoint(32, 32)
        qtbot.mouse_move(canvas, pos)
        
        # Status bar should show pixel information
        status_text = app._status_bar.currentMessage()
        # Should contain coordinate or pixel information
        assert len(status_text) > 0


# ============================================================================
# Window State and Geometry Tests
# ============================================================================

@pytest.mark.ui
class TestAppWindowState:
    """Test window state management."""
    
    def test_window_resize(self, qtbot, app_window):
        """Test window can be resized."""
        app = app_window
        
        original_size = app.size()
        
        # Resize window
        new_width = original_size.width() + 100
        new_height = original_size.height() + 100
        app.resize(new_width, new_height)
        
        qtbot.wait(50)  # Allow resize to process
        
        new_size = app.size()
        assert new_size.width() >= new_width - 10  # Allow some tolerance
        assert new_size.height() >= new_height - 10
        
    def test_window_minimize_restore(self, qtbot, app_window):
        """Test window can be minimized and restored."""
        app = app_window
        
        # Minimize window
        app.showMinimized()
        qtbot.wait(100)
        assert app.isMinimized()
        
        # Restore window
        app.showNormal()
        qtbot.wait(100)
        assert not app.isMinimized()
        
    def test_window_close_confirmation(self, qtbot, app_window, mock_message_box):
        """Test window close shows confirmation for unsaved changes."""
        app = app_window
        
        # Make some changes
        app._model.set_pixel(1, 1, QColor(255, 0, 0))
        
        # Try to close window
        app.close()
        
        # Should show confirmation dialog if there are unsaved changes
        if app._model.is_modified:
            mock_message_box.question.assert_called()


# ============================================================================
# Keyboard Shortcuts Tests
# ============================================================================

@pytest.mark.ui
class TestAppWindowKeyboardShortcuts:
    """Test application-wide keyboard shortcuts."""
    
    def test_file_shortcuts(self, qtbot, app_window):
        """Test file operation shortcuts."""
        app = app_window
        
        # Test Ctrl+N for new file
        qtbot.key_click(app, Qt.Key.Key_N, Qt.KeyboardModifier.ControlModifier)
        
        # Test Ctrl+O for open file
        with patch('pixel_drawing.views.app.QFileDialog'):
            qtbot.key_click(app, Qt.Key.Key_O, Qt.KeyboardModifier.ControlModifier)
        
        # Test Ctrl+S for save file
        with patch('pixel_drawing.views.app.QFileDialog'):
            qtbot.key_click(app, Qt.Key.Key_S, Qt.KeyboardModifier.ControlModifier)
    
    def test_edit_shortcuts(self, qtbot, app_window):
        """Test edit operation shortcuts."""
        app = app_window
        
        # Test Ctrl+Z for undo (if implemented)
        qtbot.key_click(app, Qt.Key.Key_Z, Qt.KeyboardModifier.ControlModifier)
        
        # Test Ctrl+Y for redo (if implemented)
        qtbot.key_click(app, Qt.Key.Key_Y, Qt.KeyboardModifier.ControlModifier)
    
    def test_tool_shortcuts_global(self, qtbot, app_window):
        """Test tool shortcuts work globally in app."""
        app = app_window
        canvas = app._canvas
        
        # Focus should not matter for global shortcuts
        app.setFocus()
        
        # Test tool shortcuts
        qtbot.key_click(app, Qt.Key.Key_B)  # Brush
        assert canvas.get_current_tool_id() == "brush"
        
        qtbot.key_click(app, Qt.Key.Key_F)  # Fill
        assert canvas.get_current_tool_id() == "fill"


# ============================================================================
# Performance Tests
# ============================================================================

@pytest.mark.ui_slow
@pytest.mark.ui
class TestAppWindowPerformance:
    """Test application window performance."""
    
    def test_app_startup_time(self, qtbot, ui_performance_timer):
        """Test application startup performance."""
        with ui_performance_timer.measure("app_startup", max_duration=2.0):
            app = PixelDrawingApp()
            qtbot.add_widget(app)
            app.show()
            qtbot.wait_for_window_shown(app)
            
    def test_canvas_integration_performance(self, qtbot, app_window, ui_performance_timer):
        """Test canvas operations don't slow down the app."""
        app = app_window
        canvas = app._canvas
        
        with ui_performance_timer.measure("canvas_operations", max_duration=0.5):
            # Perform multiple drawing operations
            canvas.set_current_tool("brush")
            for i in range(10):
                pos = QPoint(i * 16 + 8, i * 16 + 8)
                qtbot.mouse_click(canvas, Qt.MouseButton.LeftButton, pos=pos)
                qtbot.wait(10)


# ============================================================================
# Error Handling Tests
# ============================================================================

@pytest.mark.ui
class TestAppWindowErrorHandling:
    """Test application error handling."""
    
    def test_invalid_file_handling(self, qtbot, app_window, temp_dir, mock_message_box):
        """Test app handles invalid files gracefully."""
        app = app_window
        
        # Create invalid file
        invalid_file = temp_dir / "invalid.json"
        invalid_file.write_text("{ invalid json")
        
        with patch('pixel_drawing.views.app.QFileDialog') as mock_dialog:
            mock_dialog.getOpenFileName.return_value = (str(invalid_file), "JSON files (*.json)")
            
            # Try to open invalid file
            open_action = app._find_action("Open")
            if open_action:
                open_action.trigger()
                
                # Should show error dialog
                mock_message_box.critical.assert_called()
    
    def test_file_permission_error_handling(self, qtbot, app_window, mock_message_box):
        """Test app handles file permission errors."""
        app = app_window
        
        with patch('pixel_drawing.views.app.QFileDialog') as mock_dialog:
            # Mock a file that can't be written
            mock_dialog.getSaveFileName.return_value = ("/root/no_permission.json", "JSON files (*.json)")
            
            # Try to save to restricted location
            save_action = app._find_action("Save")
            if save_action:
                save_action.trigger()
                
                # Should handle the error gracefully
                # (Exact handling depends on implementation)


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.ui
class TestAppWindowIntegration:
    """Test overall application integration."""
    
    def test_full_workflow_new_draw_save(self, qtbot, app_window, temp_dir, test_colors):
        """Test complete workflow: new -> draw -> save."""
        app = app_window
        canvas = app._canvas
        
        # 1. Create new file
        with patch('pixel_drawing.views.app.QMessageBox') as mock_box:
            mock_box.question.return_value = mock_box.StandardButton.Yes
            new_action = app._find_action("New")
            if new_action:
                new_action.trigger()
        
        # 2. Draw something
        canvas.set_current_tool("brush")
        canvas.current_color = test_colors['red']
        
        pos = QPoint(32, 32)
        qtbot.mouse_click(canvas, Qt.MouseButton.LeftButton, pos=pos)
        
        # 3. Save file
        save_file = temp_dir / "workflow_test.json"
        with patch('pixel_drawing.views.app.QFileDialog') as mock_dialog:
            mock_dialog.getSaveFileName.return_value = (str(save_file), "JSON files (*.json)")
            
            save_action = app._find_action("Save")
            if save_action:
                save_action.trigger()
        
        # 4. Verify file was created (if save implementation exists)
        # This depends on actual file service implementation
    
    def test_canvas_tool_panel_synchronization(self, qtbot, app_window):
        """Test canvas and tool panel stay synchronized."""
        app = app_window
        canvas = app._canvas
        
        # Change tool via canvas
        canvas.set_current_tool("fill")
        
        # Tool panel should reflect the change
        # (This test depends on your specific UI implementation)
        current_tool = canvas.get_current_tool_id()
        assert current_tool == "fill"
        
        # If tool panel has visual indicators, test those too
        side_panel = app._side_panel
        if hasattr(side_panel, '_active_tool_indicator'):
            # Check that UI reflects current tool
            pass


# ============================================================================
# Helper Methods for Tests
# ============================================================================

# Add helper methods to PixelDrawingApp for testing
def _find_action(self, action_name: str) -> QAction:
    """Helper method to find action by name (for testing)."""
    for action in self.findChildren(QAction):
        if action_name.lower() in action.text().lower():
            return action
    return None

# Monkey patch for testing
PixelDrawingApp._find_action = _find_action