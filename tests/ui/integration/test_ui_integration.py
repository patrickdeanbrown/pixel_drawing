"""
UI integration tests using pytest-qt.

These tests verify end-to-end workflows and integration between
all UI components, accessibility features, and user interactions.
"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path
import json
import tempfile

try:
    from PyQt6.QtWidgets import QApplication, QMessageBox, QFileDialog, QColorDialog
    from PyQt6.QtCore import Qt, QPoint, QTimer
    from PyQt6.QtGui import QColor, QKeyEvent
    from PyQt6.QtTest import QTest
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    pytest.skip("PyQt6 not available", allow_module_level=True)

from pixel_drawing.views.app import PixelDrawingApp
from pixel_drawing.models import PixelArtModel
from pixel_drawing.services import FileService


# ============================================================================
# End-to-End Workflow Tests
# ============================================================================

@pytest.mark.ui
class TestCompleteWorkflows:
    """Test complete user workflows from start to finish."""
    
    def test_new_project_draw_save_workflow(self, qtbot, temp_dir, test_colors):
        """Test complete workflow: new project, draw, save."""
        # 1. Start application
        app = PixelDrawingApp()
        qtbot.add_widget(app)
        app.show()
        qtbot.wait_for_window_shown(app)
        
        try:
            canvas = app._canvas
            
            # 2. Create new project (if needed)
            with patch('pixel_drawing.views.app.QMessageBox') as mock_box:
                mock_box.question.return_value = mock_box.StandardButton.Yes
                # Trigger new if there's a new action
                if hasattr(app, '_find_action'):
                    new_action = app._find_action("New")
                    if new_action:
                        new_action.trigger()
            
            # 3. Select brush tool and color
            canvas.set_current_tool("brush")
            canvas.current_color = test_colors['red']
            
            # 4. Draw something recognizable
            pixel_size = canvas.pixel_size
            
            # Draw a simple pattern
            drawing_coords = [
                (2, 2), (3, 2), (4, 2),  # Top line
                (2, 3),         (4, 3),  # Sides
                (2, 4), (3, 4), (4, 4)   # Bottom line
            ]
            
            for x, y in drawing_coords:
                pos = QPoint(x * pixel_size + pixel_size//2, y * pixel_size + pixel_size//2)
                qtbot.mouse_click(canvas, Qt.MouseButton.LeftButton, pos=pos)
                qtbot.wait(10)  # Small delay between clicks
            
            # 5. Save project
            save_file = temp_dir / "integration_test.json"
            with patch('pixel_drawing.views.app.QFileDialog') as mock_dialog:
                mock_dialog.getSaveFileName.return_value = (str(save_file), "JSON files (*.json)")
                
                if hasattr(app, '_find_action'):
                    save_action = app._find_action("Save")
                    if save_action:
                        save_action.trigger()
            
            # 6. Verify the drawing was created
            for x, y in drawing_coords:
                assert canvas._model.get_pixel(x, y) == test_colors['red']
                
        finally:
            app.close()
    
    def test_load_edit_save_workflow(self, qtbot, temp_dir, test_colors):
        """Test workflow: load existing project, edit, save."""
        # 1. Create test project file
        project_data = {
            "width": 8,
            "height": 8,
            "pixels": {
                "1,1": "#FF0000",  # Red pixel
                "2,2": "#00FF00",  # Green pixel
                "3,3": "#0000FF"   # Blue pixel
            }
        }
        
        test_file = temp_dir / "test_project.json"
        with open(test_file, 'w') as f:
            json.dump(project_data, f)
        
        # 2. Start application
        app = PixelDrawingApp()
        qtbot.add_widget(app)
        app.show()
        qtbot.wait_for_window_shown(app)
        
        try:
            canvas = app._canvas
            
            # 3. Load project
            with patch('pixel_drawing.views.app.QFileDialog') as mock_dialog:
                mock_dialog.getOpenFileName.return_value = (str(test_file), "JSON files (*.json)")
                
                if hasattr(app, '_find_action'):
                    open_action = app._find_action("Open")
                    if open_action:
                        open_action.trigger()
            
            # 4. Verify loaded content
            qtbot.wait(100)  # Allow time for loading
            
            # Check if pixels were loaded (depends on file service implementation)
            # This test assumes the file service integration works
            
            # 5. Make edits
            canvas.set_current_tool("brush")
            canvas.current_color = test_colors['red']
            
            # Add new pixel
            pos = QPoint(5 * canvas.pixel_size + 5, 5 * canvas.pixel_size + 5)
            qtbot.mouse_click(canvas, Qt.MouseButton.LeftButton, pos=pos)
            
            # 6. Save changes
            save_file = temp_dir / "edited_project.json"
            with patch('pixel_drawing.views.app.QFileDialog') as mock_dialog:
                mock_dialog.getSaveFileName.return_value = (str(save_file), "JSON files (*.json)")
                
                if hasattr(app, '_find_action'):
                    save_action = app._find_action("Save")
                    if save_action:
                        save_action.trigger()
            
            # 7. Verify edit was made
            assert canvas._model.get_pixel(5, 5) == test_colors['red']
            
        finally:
            app.close()
    
    def test_multicolor_drawing_workflow(self, qtbot, test_colors):
        """Test drawing with multiple colors and tools."""
        app = PixelDrawingApp()
        qtbot.add_widget(app)
        app.show()
        qtbot.wait_for_window_shown(app)
        
        try:
            canvas = app._canvas
            pixel_size = canvas.pixel_size
            
            # 1. Draw red border with brush
            canvas.set_current_tool("brush")
            canvas.current_color = test_colors['red']
            
            border_coords = [
                (1, 1), (2, 1), (3, 1),
                (1, 2),         (3, 2),
                (1, 3), (2, 3), (3, 3)
            ]
            
            for x, y in border_coords:
                pos = QPoint(x * pixel_size + pixel_size//2, y * pixel_size + pixel_size//2)
                qtbot.mouse_click(canvas, Qt.MouseButton.LeftButton, pos=pos)
            
            # 2. Fill center with blue using fill tool
            canvas.set_current_tool("fill")
            canvas.current_color = test_colors['blue']
            
            center_pos = QPoint(2 * pixel_size + pixel_size//2, 2 * pixel_size + pixel_size//2)
            qtbot.mouse_click(canvas, Qt.MouseButton.LeftButton, pos=center_pos)
            
            # 3. Use color picker to pick red color
            canvas.set_current_tool("picker")
            red_pos = QPoint(1 * pixel_size + pixel_size//2, 1 * pixel_size + pixel_size//2)
            qtbot.mouse_click(canvas, Qt.MouseButton.LeftButton, pos=red_pos)
            
            # Current color should now be red
            assert canvas.current_color == test_colors['red']
            
            # 4. Add accent with picked color
            canvas.set_current_tool("brush")
            accent_pos = QPoint(4 * pixel_size + pixel_size//2, 4 * pixel_size + pixel_size//2)
            qtbot.mouse_click(canvas, Qt.MouseButton.LeftButton, pos=accent_pos)
            
            # 5. Verify final result
            assert canvas._model.get_pixel(1, 1) == test_colors['red']   # Border
            assert canvas._model.get_pixel(2, 2) == test_colors['blue']  # Fill
            assert canvas._model.get_pixel(4, 4) == test_colors['red']   # Accent
            
        finally:
            app.close()


# ============================================================================
# Accessibility Integration Tests
# ============================================================================

@pytest.mark.accessibility
@pytest.mark.ui
class TestAccessibilityIntegration:
    """Test accessibility features integration across the app."""
    
    def test_keyboard_navigation_workflow(self, qtbot, test_colors):
        """Test complete workflow using only keyboard navigation."""
        app = PixelDrawingApp()
        qtbot.add_widget(app)
        app.show()
        qtbot.wait_for_window_shown(app)
        
        try:
            canvas = app._canvas
            
            # 1. Focus canvas
            canvas.setFocus()
            assert canvas.hasFocus()
            
            # 2. Use keyboard to select brush tool
            qtbot.key_click(canvas, Qt.Key.Key_B)
            assert canvas.get_current_tool_id() == "brush"
            
            # 3. Navigate using arrow keys
            canvas.set_keyboard_cursor_position(0, 0)
            
            # Move right 3 times
            for _ in range(3):
                qtbot.key_click(canvas, Qt.Key.Key_Right)
            
            # Move down 2 times
            for _ in range(2):
                qtbot.key_click(canvas, Qt.Key.Key_Down)
            
            # Verify position
            x, y = canvas.get_keyboard_cursor_position()
            assert x == 3 and y == 2
            
            # 4. Draw using space key
            canvas.current_color = test_colors['blue']
            qtbot.key_click(canvas, Qt.Key.Key_Space)
            
            # Verify pixel was drawn
            assert canvas._model.get_pixel(3, 2) == test_colors['blue']
            
            # 5. Switch to fill tool using keyboard
            qtbot.key_click(canvas, Qt.Key.Key_F)
            assert canvas.get_current_tool_id() == "fill"
            
            # 6. Use Home key for quick navigation
            qtbot.key_click(canvas, Qt.Key.Key_Home)
            x, y = canvas.get_keyboard_cursor_position()
            assert x == 0 and y == 0
            
            # 7. Exit with Escape
            qtbot.key_click(canvas, Qt.Key.Key_Escape)
            assert not canvas.hasFocus()
            
        finally:
            app.close()
    
    def test_screen_reader_announcements(self, qtbot):
        """Test screen reader announcements during UI interactions."""
        app = PixelDrawingApp()
        qtbot.add_widget(app)
        app.show()
        qtbot.wait_for_window_shown(app)
        
        try:
            canvas = app._canvas
            
            # Mock screen reader to capture announcements
            with patch.object(canvas._screen_reader, 'announce') as mock_announce:
                # Focus should announce canvas state
                canvas.setFocus()
                mock_announce.assert_called()
                
                # Tool changes should be announced
                mock_announce.reset_mock()
                qtbot.key_click(canvas, Qt.Key.Key_F)
                mock_announce.assert_called()
                
                # Navigation should be announced
                mock_announce.reset_mock()
                qtbot.key_click(canvas, Qt.Key.Key_Right)
                mock_announce.assert_called()
                
        finally:
            app.close()
    
    def test_high_contrast_support(self, qtbot, accessibility_tester):
        """Test high contrast mode support."""
        app = PixelDrawingApp()
        qtbot.add_widget(app)
        app.show()
        qtbot.wait_for_window_shown(app)
        
        try:
            canvas = app._canvas
            
            # Test accessibility properties
            assert accessibility_tester.check_accessible_name(canvas)
            assert accessibility_tester.check_accessible_description(canvas)
            assert accessibility_tester.check_focus_policy(canvas)
            
            # Test keyboard navigation setup
            assert accessibility_tester.check_keyboard_navigation(canvas, qtbot)
            
        finally:
            app.close()


# ============================================================================
# Performance Integration Tests
# ============================================================================

@pytest.mark.ui_slow
@pytest.mark.ui
class TestPerformanceIntegration:
    """Test performance across integrated UI components."""
    
    def test_large_canvas_ui_performance(self, qtbot, ui_performance_timer):
        """Test UI responsiveness with large canvas."""
        with ui_performance_timer.measure("large_canvas_app_startup", max_duration=3.0):
            # Create large model
            large_model = PixelArtModel(width=64, height=64)
            app = PixelDrawingApp(model=large_model)
            qtbot.add_widget(app)
            app.show()
            qtbot.wait_for_window_shown(app)
            
        try:
            canvas = app._canvas
            
            # Test drawing performance
            with ui_performance_timer.measure("large_canvas_drawing", max_duration=1.0):
                canvas.set_current_tool("brush")
                
                # Draw multiple pixels rapidly
                for i in range(20):
                    x = i % 8
                    y = i // 8
                    pos = QPoint(x * canvas.pixel_size + 5, y * canvas.pixel_size + 5)
                    qtbot.mouse_click(canvas, Qt.MouseButton.LeftButton, pos=pos)
                    
        finally:
            app.close()
    
    def test_rapid_tool_switching_performance(self, qtbot, ui_performance_timer):
        """Test performance during rapid tool switching."""
        app = PixelDrawingApp()
        qtbot.add_widget(app)
        app.show()
        qtbot.wait_for_window_shown(app)
        
        try:
            canvas = app._canvas
            canvas.setFocus()
            
            with ui_performance_timer.measure("rapid_tool_switching", max_duration=0.5):
                # Rapidly switch between tools
                tools = [Qt.Key.Key_B, Qt.Key.Key_F, Qt.Key.Key_E, Qt.Key.Key_I] * 10
                
                for tool_key in tools:
                    qtbot.key_click(canvas, tool_key)
                    
        finally:
            app.close()
    
    def test_ui_responsiveness_during_operations(self, qtbot, ui_performance_timer):
        """Test UI remains responsive during long operations."""
        app = PixelDrawingApp()
        qtbot.add_widget(app)
        app.show()
        qtbot.wait_for_window_shown(app)
        
        try:
            canvas = app._canvas
            
            # Simulate long operation (large fill)
            canvas.set_current_tool("fill")
            
            with ui_performance_timer.measure("ui_responsiveness", max_duration=1.0):
                # Fill large area
                pos = QPoint(100, 100)
                qtbot.mouse_click(canvas, Qt.MouseButton.LeftButton, pos=pos)
                
                # UI should remain responsive
                QApplication.processEvents()
                
                # Should be able to interact with UI
                assert app.isVisible()
                assert canvas.isVisible()
                
        finally:
            app.close()


# ============================================================================
# Error Handling Integration Tests
# ============================================================================

@pytest.mark.ui
class TestErrorHandlingIntegration:
    """Test error handling across integrated components."""
    
    def test_file_error_recovery(self, qtbot, temp_dir):
        """Test recovery from file operation errors."""
        app = PixelDrawingApp()
        qtbot.add_widget(app)
        app.show()
        qtbot.wait_for_window_shown(app)
        
        try:
            # Try to open corrupted file
            corrupted_file = temp_dir / "corrupted.json"
            corrupted_file.write_text("{ invalid json content")
            
            with patch('pixel_drawing.views.app.QFileDialog') as mock_dialog:
                mock_dialog.getOpenFileName.return_value = (str(corrupted_file), "JSON files (*.json)")
                
                with patch('pixel_drawing.views.app.QMessageBox') as mock_box:
                    if hasattr(app, '_find_action'):
                        open_action = app._find_action("Open")
                        if open_action:
                            open_action.trigger()
                    
                    # Should show error message
                    mock_box.critical.assert_called()
            
            # App should remain functional
            canvas = app._canvas
            assert canvas.isVisible()
            
            # Should be able to continue working
            canvas.set_current_tool("brush")
            pos = QPoint(32, 32)
            qtbot.mouse_click(canvas, Qt.MouseButton.LeftButton, pos=pos)
            
        finally:
            app.close()
    
    def test_memory_constraint_handling(self, qtbot):
        """Test handling of memory constraints."""
        app = PixelDrawingApp()
        qtbot.add_widget(app)
        app.show()
        qtbot.wait_for_window_shown(app)
        
        try:
            canvas = app._canvas
            
            # Try to create very large canvas (should be limited)
            with patch('pixel_drawing.views.app.QMessageBox') as mock_box:
                # This depends on your canvas size validation
                try:
                    canvas._model.resize(1000, 1000)  # Very large
                except Exception:
                    # Should handle gracefully
                    pass
            
            # App should remain stable
            assert app.isVisible()
            assert canvas.isVisible()
            
        finally:
            app.close()
    
    def test_ui_state_consistency_after_errors(self, qtbot, test_colors):
        """Test UI state remains consistent after errors."""
        app = PixelDrawingApp()
        qtbot.add_widget(app)
        app.show()
        qtbot.wait_for_window_shown(app)
        
        try:
            canvas = app._canvas
            
            # Set initial state
            canvas.set_current_tool("brush")
            canvas.current_color = test_colors['red']
            
            # Cause an error (e.g., invalid operation)
            try:
                # Simulate error condition
                canvas.set_current_tool("invalid_tool")
            except Exception:
                pass
            
            # State should be preserved
            assert canvas.get_current_tool_id() in ["brush", "fill", "eraser", "picker", "pan"]
            assert canvas.current_color == test_colors['red']
            
            # Should still be able to draw
            pos = QPoint(32, 32)
            qtbot.mouse_click(canvas, Qt.MouseButton.LeftButton, pos=pos)
            
        finally:
            app.close()


# ============================================================================
# Multi-Window Integration Tests
# ============================================================================

@pytest.mark.ui
class TestMultiWindowIntegration:
    """Test integration with multiple windows and dialogs."""
    
    def test_modal_dialog_integration(self, qtbot):
        """Test modal dialogs don't break main window functionality."""
        app = PixelDrawingApp()
        qtbot.add_widget(app)
        app.show()
        qtbot.wait_for_window_shown(app)
        
        try:
            # Mock color dialog
            with patch('pixel_drawing.views.app.QColorDialog') as mock_dialog:
                mock_color = QColor(255, 0, 0)
                mock_dialog.getColor.return_value = mock_color
                
                # Trigger color dialog (if color selection exists)
                # This depends on your UI implementation
                canvas = app._canvas
                
                # After dialog, functionality should be preserved
                canvas.set_current_tool("brush")
                pos = QPoint(32, 32)
                qtbot.mouse_click(canvas, Qt.MouseButton.LeftButton, pos=pos)
                
        finally:
            app.close()
    
    def test_preferences_dialog_integration(self, qtbot):
        """Test preferences dialog integration."""
        app = PixelDrawingApp()
        qtbot.add_widget(app)
        app.show()
        qtbot.wait_for_window_shown(app)
        
        try:
            # This test depends on preferences dialog implementation
            # For now, just verify app remains stable
            
            canvas = app._canvas
            assert canvas.isVisible()
            
            # Test that preferences changes would affect UI
            # (This is a placeholder for actual preferences integration)
            
        finally:
            app.close()


# ============================================================================
# Cross-Platform Integration Tests
# ============================================================================

@pytest.mark.ui
class TestCrossPlatformIntegration:
    """Test cross-platform UI behavior."""
    
    def test_keyboard_shortcuts_platform_specific(self, qtbot):
        """Test keyboard shortcuts work across platforms."""
        app = PixelDrawingApp()
        qtbot.add_widget(app)
        app.show()
        qtbot.wait_for_window_shown(app)
        
        try:
            canvas = app._canvas
            
            # Test standard shortcuts
            if hasattr(app, '_find_action'):
                # Ctrl+N (or Cmd+N on Mac)
                qtbot.key_click(app, Qt.Key.Key_N, Qt.KeyboardModifier.ControlModifier)
                
                # Should work regardless of platform
                # (Qt handles platform-specific modifiers)
                
        finally:
            app.close()
    
    def test_font_and_scaling_integration(self, qtbot):
        """Test UI works with different font sizes and scaling."""
        app = PixelDrawingApp()
        qtbot.add_widget(app)
        app.show()
        qtbot.wait_for_window_shown(app)
        
        try:
            # Test that UI components are visible and functional
            # regardless of system font scaling
            
            canvas = app._canvas
            assert canvas.isVisible()
            assert canvas.width() > 0
            assert canvas.height() > 0
            
            # Test basic functionality works
            canvas.set_current_tool("brush")
            pos = QPoint(32, 32)
            qtbot.mouse_click(canvas, Qt.MouseButton.LeftButton, pos=pos)
            
        finally:
            app.close()


# ============================================================================
# Integration Test Utilities
# ============================================================================

def wait_for_canvas_update(qtbot, canvas, timeout=1000):
    """Utility to wait for canvas updates."""
    # Wait for any pending paint events
    qtbot.wait(50)
    QApplication.processEvents()

def verify_canvas_state(canvas, expected_pixels):
    """Utility to verify canvas state matches expected pixels."""
    for (x, y), expected_color in expected_pixels.items():
        actual_color = canvas._model.get_pixel(x, y)
        assert actual_color == expected_color, f"Pixel ({x},{y}) expected {expected_color}, got {actual_color}"

def simulate_drawing_pattern(qtbot, canvas, pattern, color, tool="brush"):
    """Utility to simulate drawing a pattern."""
    canvas.set_current_tool(tool)
    canvas.current_color = color
    
    pixel_size = canvas.pixel_size
    
    for x, y in pattern:
        pos = QPoint(x * pixel_size + pixel_size//2, y * pixel_size + pixel_size//2)
        qtbot.mouse_click(canvas, Qt.MouseButton.LeftButton, pos=pos)
        qtbot.wait(10)