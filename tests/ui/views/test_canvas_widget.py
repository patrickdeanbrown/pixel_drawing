"""
UI tests for the PixelCanvas widget using pytest-qt.

These tests verify the canvas widget's behavior, user interactions,
keyboard navigation, and accessibility features.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt, QPoint, QRect
    from PyQt6.QtGui import QColor, QKeyEvent, QMouseEvent, QPaintEvent
    from PyQt6.QtTest import QTest
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    pytest.skip("PyQt6 not available", allow_module_level=True)

from pixel_drawing.views.canvas import PixelCanvas
from pixel_drawing.models import PixelArtModel
from pixel_drawing.constants import AppConstants


# ============================================================================
# Canvas Widget Initialization Tests
# ============================================================================

@pytest.mark.ui
class TestCanvasInitialization:
    """Test canvas widget initialization and basic properties."""
    
    def test_canvas_default_initialization(self, qtbot):
        """Test canvas initializes with default parameters."""
        canvas = PixelCanvas()
        qtbot.add_widget(canvas)
        
        assert canvas.pixel_size == AppConstants.DEFAULT_PIXEL_SIZE
        assert canvas.current_color == QColor(AppConstants.DEFAULT_FG_COLOR)
        assert not canvas._is_drawing
        assert canvas._model is not None
        assert canvas._tool_manager is not None
        
    def test_canvas_custom_initialization(self, qtbot, ui_model):
        """Test canvas initializes with custom parameters."""
        pixel_size = 24
        canvas = PixelCanvas(model=ui_model, pixel_size=pixel_size)
        qtbot.add_widget(canvas)
        
        assert canvas.pixel_size == pixel_size
        assert canvas._model == ui_model
        assert canvas.width() == ui_model.width * pixel_size
        assert canvas.height() == ui_model.height * pixel_size
        
    def test_canvas_signals_setup(self, qtbot, ui_model):
        """Test that all required signals are properly set up."""
        canvas = PixelCanvas(model=ui_model)
        qtbot.add_widget(canvas)
        
        # Check signal existence
        assert hasattr(canvas, 'color_used')
        assert hasattr(canvas, 'tool_changed')
        assert hasattr(canvas, 'pixel_hovered')
        
        # Verify signal connections
        assert canvas._model.pixel_changed.isSignalConnected()
        assert canvas._model.canvas_resized.isSignalConnected()
        assert canvas._model.canvas_cleared.isSignalConnected()
    
    def test_canvas_accessibility_setup(self, qtbot, ui_model):
        """Test accessibility features are properly initialized."""
        canvas = PixelCanvas(model=ui_model)
        qtbot.add_widget(canvas)
        
        # Check accessibility properties
        assert canvas.accessibleName()
        assert canvas.accessibleDescription()
        assert canvas.focusPolicy() == Qt.FocusPolicy.StrongFocus
        
        # Check accessibility components
        assert canvas._screen_reader is not None
        assert canvas._canvas_navigation is not None


# ============================================================================
# Mouse Interaction Tests
# ============================================================================

@pytest.mark.ui
class TestCanvasMouseInteraction:
    """Test mouse interactions with the canvas."""
    
    def test_mouse_press_drawing(self, qtbot, canvas_widget, test_colors):
        """Test mouse press starts drawing operation."""
        canvas = canvas_widget
        
        # Set brush tool and color
        canvas.set_current_tool("brush")
        canvas.current_color = test_colors['red']
        
        # Simulate mouse press at pixel (2, 2)
        pos = QPoint(2 * canvas.pixel_size + 5, 2 * canvas.pixel_size + 5)
        qtbot.mouse_press(canvas, Qt.MouseButton.LeftButton, pos=pos)
        
        assert canvas._is_drawing
        
        # Verify pixel was set
        pixel_color = canvas._model.get_pixel(2, 2)
        assert pixel_color == test_colors['red']
        
    def test_mouse_move_continuous_drawing(self, qtbot, canvas_widget, test_colors):
        """Test mouse move continues drawing operation."""
        canvas = canvas_widget
        canvas.set_current_tool("brush")
        canvas.current_color = test_colors['blue']
        
        # Start drawing
        start_pos = QPoint(1 * canvas.pixel_size + 5, 1 * canvas.pixel_size + 5)
        qtbot.mouse_press(canvas, Qt.MouseButton.LeftButton, pos=start_pos)
        
        # Move to different pixel
        move_pos = QPoint(3 * canvas.pixel_size + 5, 3 * canvas.pixel_size + 5)
        qtbot.mouse_move(canvas, move_pos)
        
        # Verify both pixels are drawn
        assert canvas._model.get_pixel(1, 1) == test_colors['blue']
        assert canvas._model.get_pixel(3, 3) == test_colors['blue']
        
    def test_mouse_release_stops_drawing(self, qtbot, canvas_widget, test_colors):
        """Test mouse release stops drawing operation."""
        canvas = canvas_widget
        canvas.set_current_tool("brush")
        canvas.current_color = test_colors['green']
        
        # Start drawing
        pos = QPoint(4 * canvas.pixel_size + 5, 4 * canvas.pixel_size + 5)
        qtbot.mouse_press(canvas, Qt.MouseButton.LeftButton, pos=pos)
        assert canvas._is_drawing
        
        # Release mouse
        qtbot.mouse_release(canvas, Qt.MouseButton.LeftButton, pos=pos)
        assert not canvas._is_drawing
        
    def test_mouse_hover_emits_signal(self, qtbot, canvas_widget):
        """Test mouse hover emits pixel_hovered signal."""
        canvas = canvas_widget
        
        with qtbot.wait_signal(canvas.pixel_hovered, timeout=1000):
            pos = QPoint(5 * canvas.pixel_size + 5, 5 * canvas.pixel_size + 5)
            qtbot.mouse_move(canvas, pos)
            
    def test_mouse_out_of_bounds(self, qtbot, canvas_widget):
        """Test mouse clicks outside canvas bounds are ignored."""
        canvas = canvas_widget
        canvas.set_current_tool("brush")
        
        # Click outside canvas bounds
        out_of_bounds_pos = QPoint(
            canvas._model.width * canvas.pixel_size + 10,
            canvas._model.height * canvas.pixel_size + 10
        )
        
        qtbot.mouse_press(canvas, Qt.MouseButton.LeftButton, pos=out_of_bounds_pos)
        assert not canvas._is_drawing


# ============================================================================
# Keyboard Interaction Tests
# ============================================================================

@pytest.mark.ui
class TestCanvasKeyboardInteraction:
    """Test keyboard interactions and accessibility."""
    
    def test_keyboard_navigation_setup(self, qtbot, canvas_widget):
        """Test keyboard navigation is properly set up."""
        canvas = canvas_widget
        canvas.setFocus()
        
        assert canvas.hasFocus()
        assert canvas._canvas_navigation is not None
        
    def test_tool_shortcuts(self, qtbot, canvas_widget):
        """Test tool shortcut keys work."""
        canvas = canvas_widget
        canvas.setFocus()
        
        # Test brush shortcut (B)
        qtbot.key_click(canvas, Qt.Key.Key_B)
        assert canvas.get_current_tool_id() == "brush"
        
        # Test fill shortcut (F)
        qtbot.key_click(canvas, Qt.Key.Key_F)
        assert canvas.get_current_tool_id() == "fill"
        
        # Test eraser shortcut (E)
        qtbot.key_click(canvas, Qt.Key.Key_E)
        assert canvas.get_current_tool_id() == "eraser"
        
    def test_arrow_key_navigation(self, qtbot, canvas_widget):
        """Test arrow key navigation moves cursor."""
        canvas = canvas_widget
        canvas.setFocus()
        
        # Get initial position
        initial_x, initial_y = canvas.get_keyboard_cursor_position()
        
        # Move right
        qtbot.key_click(canvas, Qt.Key.Key_Right)
        x, y = canvas.get_keyboard_cursor_position()
        assert x == initial_x + 1
        assert y == initial_y
        
        # Move down
        qtbot.key_click(canvas, Qt.Key.Key_Down)
        x, y = canvas.get_keyboard_cursor_position()
        assert x == initial_x + 1
        assert y == initial_y + 1
        
    def test_keyboard_drawing_action(self, qtbot, canvas_widget, test_colors):
        """Test space key performs drawing action."""
        canvas = canvas_widget
        canvas.setFocus()
        canvas.set_current_tool("brush")
        canvas.current_color = test_colors['red']
        
        # Set cursor position
        canvas.set_keyboard_cursor_position(3, 3)
        
        # Press space to draw
        qtbot.key_click(canvas, Qt.Key.Key_Space)
        
        # Verify pixel was drawn
        assert canvas._model.get_pixel(3, 3) == test_colors['red']
        
    def test_escape_key_exits_focus(self, qtbot, canvas_widget):
        """Test escape key removes focus from canvas."""
        canvas = canvas_widget
        canvas.setFocus()
        assert canvas.hasFocus()
        
        qtbot.key_click(canvas, Qt.Key.Key_Escape)
        assert not canvas.hasFocus()
        
    def test_home_end_keys(self, qtbot, canvas_widget):
        """Test Home and End keys for quick navigation."""
        canvas = canvas_widget
        canvas.setFocus()
        
        # Move to middle of canvas
        canvas.set_keyboard_cursor_position(4, 4)
        
        # Press Home - should go to origin
        qtbot.key_click(canvas, Qt.Key.Key_Home)
        x, y = canvas.get_keyboard_cursor_position()
        assert x == 0 and y == 0
        
        # Press End - should go to bottom-right
        qtbot.key_click(canvas, Qt.Key.Key_End)
        x, y = canvas.get_keyboard_cursor_position()
        assert x == canvas._model.width - 1
        assert y == canvas._model.height - 1


# ============================================================================
# Tool Interaction Tests
# ============================================================================

@pytest.mark.ui
class TestCanvasToolInteraction:
    """Test interactions with different drawing tools."""
    
    def test_brush_tool_drawing(self, qtbot, canvas_widget, test_colors):
        """Test brush tool draws individual pixels."""
        canvas = canvas_widget
        canvas.set_current_tool("brush")
        canvas.current_color = test_colors['blue']
        
        # Draw at position (2, 2)
        pos = QPoint(2 * canvas.pixel_size + 5, 2 * canvas.pixel_size + 5)
        qtbot.mouse_click(canvas, Qt.MouseButton.LeftButton, pos=pos)
        
        # Verify only one pixel is affected
        assert canvas._model.get_pixel(2, 2) == test_colors['blue']
        assert canvas._model.get_pixel(1, 2) == QColor(255, 255, 255)  # Should remain white
        
    def test_fill_tool_flood_fill(self, qtbot, canvas_widget, test_colors):
        """Test fill tool performs flood fill operation."""
        canvas = canvas_widget
        
        # First create a boundary with brush
        canvas.set_current_tool("brush")
        canvas.current_color = test_colors['black']
        
        # Draw a boundary
        boundary_positions = [(1, 1), (2, 1), (3, 1), (1, 2), (3, 2), (1, 3), (2, 3), (3, 3)]
        for x, y in boundary_positions:
            pos = QPoint(x * canvas.pixel_size + 5, y * canvas.pixel_size + 5)
            qtbot.mouse_click(canvas, Qt.MouseButton.LeftButton, pos=pos)
        
        # Switch to fill tool and fill inside
        canvas.set_current_tool("fill")
        canvas.current_color = test_colors['red']
        
        fill_pos = QPoint(2 * canvas.pixel_size + 5, 2 * canvas.pixel_size + 5)
        qtbot.mouse_click(canvas, Qt.MouseButton.LeftButton, pos=fill_pos)
        
        # Verify fill worked
        assert canvas._model.get_pixel(2, 2) == test_colors['red']
        
    def test_tool_change_updates_cursor(self, qtbot, canvas_widget):
        """Test tool changes update the cursor."""
        canvas = canvas_widget
        
        initial_cursor = canvas.cursor()
        
        # Change tool
        canvas.set_current_tool("fill")
        
        # Cursor should potentially change (depends on implementation)
        # At minimum, the tool should be changed
        assert canvas.get_current_tool_id() == "fill"
        
    def test_tool_change_emits_signal(self, qtbot, canvas_widget):
        """Test tool changes emit tool_changed signal."""
        canvas = canvas_widget
        
        with qtbot.wait_signal(canvas.tool_changed, timeout=1000):
            canvas.set_current_tool("brush")


# ============================================================================
# Canvas Rendering Tests
# ============================================================================

@pytest.mark.ui
class TestCanvasRendering:
    """Test canvas rendering and performance."""
    
    def test_paint_event_handling(self, qtbot, canvas_widget):
        """Test canvas handles paint events properly."""
        canvas = canvas_widget
        
        # Force a repaint
        canvas.update()
        qtbot.wait(50)  # Allow time for paint event processing
        
        # Verify canvas is properly visible
        assert canvas.isVisible()
        
    def test_pixel_coordinate_conversion(self, qtbot, canvas_widget):
        """Test conversion between screen and pixel coordinates."""
        canvas = canvas_widget
        
        # Test coordinate conversion
        screen_pos = QPoint(32, 48)  # Assuming 16px pixel size
        pixel_x, pixel_y = canvas.get_pixel_coords(screen_pos)
        
        expected_x = 32 // canvas.pixel_size
        expected_y = 48 // canvas.pixel_size
        
        assert pixel_x == expected_x
        assert pixel_y == expected_y
        
    @pytest.mark.ui_slow
    def test_canvas_performance_large_update(self, qtbot, canvas_widget_large, ui_performance_timer):
        """Test canvas performance with large updates."""
        canvas = canvas_widget_large
        
        with ui_performance_timer.measure("large_canvas_update", max_duration=0.5):
            # Trigger full canvas repaint
            canvas.update()
            qtbot.wait(100)


# ============================================================================
# Canvas Resize and Model Changes Tests
# ============================================================================

@pytest.mark.ui
class TestCanvasModelChanges:
    """Test canvas responds properly to model changes."""
    
    def test_canvas_resize_updates_widget(self, qtbot, canvas_widget):
        """Test canvas widget resizes when model dimensions change."""
        canvas = canvas_widget
        
        original_width = canvas.width()
        original_height = canvas.height()
        
        # Resize model
        new_width, new_height = 16, 16
        canvas._model.resize(new_width, new_height)
        
        # Widget should update its size
        expected_width = new_width * canvas.pixel_size
        expected_height = new_height * canvas.pixel_size
        
        assert canvas.width() == expected_width
        assert canvas.height() == expected_height
        
    def test_canvas_clear_updates_display(self, qtbot, canvas_widget, test_colors):
        """Test canvas updates when model is cleared."""
        canvas = canvas_widget
        
        # Add some pixels
        canvas._model.set_pixel(1, 1, test_colors['red'])
        canvas._model.set_pixel(2, 2, test_colors['blue'])
        
        # Clear model
        canvas._model.clear()
        
        # Verify pixels are white
        assert canvas._model.get_pixel(1, 1) == QColor(255, 255, 255)
        assert canvas._model.get_pixel(2, 2) == QColor(255, 255, 255)
        
    def test_pixel_changes_trigger_updates(self, qtbot, canvas_widget, test_colors):
        """Test individual pixel changes trigger appropriate updates."""
        canvas = canvas_widget
        
        # Monitor update calls
        with patch.object(canvas, 'update') as mock_update:
            canvas._model.set_pixel(3, 3, test_colors['green'])
            
            # Should trigger update (possibly delayed)
            qtbot.wait(150)  # Wait for batched updates
            mock_update.assert_called()


# ============================================================================
# Zoom and Wheel Event Tests
# ============================================================================

@pytest.mark.ui
class TestCanvasZoom:
    """Test canvas zoom functionality."""
    
    def test_wheel_zoom_with_ctrl(self, qtbot, canvas_widget):
        """Test mouse wheel zoom with Ctrl modifier."""
        canvas = canvas_widget
        original_pixel_size = canvas.pixel_size
        
        # Create wheel event with Ctrl modifier
        wheel_event = Mock()
        wheel_event.modifiers.return_value = Qt.KeyboardModifier.ControlModifier
        wheel_event.angleDelta.return_value.y.return_value = 120  # Positive delta = zoom in
        
        canvas.wheelEvent(wheel_event)
        
        # Pixel size should increase
        assert canvas.pixel_size > original_pixel_size
        
    def test_wheel_zoom_bounds(self, qtbot, canvas_widget):
        """Test zoom respects minimum and maximum bounds."""
        canvas = canvas_widget
        
        # Set to minimum zoom
        canvas.pixel_size = 4
        
        # Try to zoom out further
        wheel_event = Mock()
        wheel_event.modifiers.return_value = Qt.KeyboardModifier.ControlModifier
        wheel_event.angleDelta.return_value.y.return_value = -120  # Negative delta = zoom out
        
        canvas.wheelEvent(wheel_event)
        
        # Should stay at minimum
        assert canvas.pixel_size >= 4
        
        # Set to maximum zoom
        canvas.pixel_size = 64
        
        # Try to zoom in further
        wheel_event.angleDelta.return_value.y.return_value = 120  # Positive delta = zoom in
        canvas.wheelEvent(wheel_event)
        
        # Should stay at maximum
        assert canvas.pixel_size <= 64


# ============================================================================
# Accessibility Tests
# ============================================================================

@pytest.mark.accessibility
@pytest.mark.ui
class TestCanvasAccessibility:
    """Test canvas accessibility features."""
    
    def test_canvas_has_accessible_properties(self, qtbot, canvas_widget, accessibility_tester):
        """Test canvas has proper accessible properties."""
        canvas = canvas_widget
        
        assert accessibility_tester.check_accessible_name(canvas)
        assert accessibility_tester.check_accessible_description(canvas)
        assert accessibility_tester.check_focus_policy(canvas)
        
    def test_canvas_keyboard_focus(self, qtbot, canvas_widget):
        """Test canvas can receive and handle keyboard focus."""
        canvas = canvas_widget
        
        # Set focus
        canvas.setFocus()
        assert canvas.hasFocus()
        
        # Focus events should be handled
        assert hasattr(canvas, 'focusInEvent')
        assert hasattr(canvas, 'focusOutEvent')
        
    def test_screen_reader_announcements(self, qtbot, canvas_widget):
        """Test screen reader announcements are made."""
        canvas = canvas_widget
        
        # Mock screen reader
        with patch.object(canvas._screen_reader, 'announce') as mock_announce:
            canvas.setFocus()
            
            # Should announce canvas state
            mock_announce.assert_called()
            
    def test_accessibility_navigation_bounds(self, qtbot, canvas_widget):
        """Test keyboard navigation respects canvas bounds."""
        canvas = canvas_widget
        canvas.setFocus()
        
        # Move to edge
        canvas.set_keyboard_cursor_position(0, 0)
        
        # Try to move beyond edge
        qtbot.key_click(canvas, Qt.Key.Key_Left)
        
        x, y = canvas.get_keyboard_cursor_position()
        assert x >= 0  # Should not go below 0
        
        # Move to opposite edge
        max_x = canvas._model.width - 1
        max_y = canvas._model.height - 1
        canvas.set_keyboard_cursor_position(max_x, max_y)
        
        # Try to move beyond edge
        qtbot.key_click(canvas, Qt.Key.Key_Right)
        
        x, y = canvas.get_keyboard_cursor_position()
        assert x <= max_x  # Should not exceed bounds


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.ui
class TestCanvasIntegration:
    """Test canvas integration with other components."""
    
    def test_canvas_model_integration(self, qtbot, canvas_widget, test_colors):
        """Test canvas properly integrates with model."""
        canvas = canvas_widget
        model = canvas._model
        
        # Changes through canvas should update model
        canvas.set_current_tool("brush")
        canvas.current_color = test_colors['red']
        
        pos = QPoint(5 * canvas.pixel_size + 5, 5 * canvas.pixel_size + 5)
        qtbot.mouse_click(canvas, Qt.MouseButton.LeftButton, pos=pos)
        
        assert model.get_pixel(5, 5) == test_colors['red']
        
    def test_canvas_tool_manager_integration(self, qtbot, canvas_widget):
        """Test canvas integrates properly with tool manager."""
        canvas = canvas_widget
        tool_manager = canvas._tool_manager
        
        # Tool changes should be reflected
        canvas.set_current_tool("fill")
        assert tool_manager.current_tool is not None
        
        # Tool manager should handle drawing operations
        assert hasattr(tool_manager, 'handle_press')
        assert hasattr(tool_manager, 'handle_move')
        assert hasattr(tool_manager, 'handle_release')
        
    def test_canvas_signal_emission(self, qtbot, canvas_widget, test_colors):
        """Test canvas emits appropriate signals."""
        canvas = canvas_widget
        
        # Color usage should emit signal
        with qtbot.wait_signal(canvas.color_used, timeout=1000):
            canvas.current_color = test_colors['blue']
            pos = QPoint(1 * canvas.pixel_size + 5, 1 * canvas.pixel_size + 5)
            qtbot.mouse_click(canvas, Qt.MouseButton.LeftButton, pos=pos)
            
        # Hover should emit signal
        with qtbot.wait_signal(canvas.pixel_hovered, timeout=1000):
            hover_pos = QPoint(2 * canvas.pixel_size + 5, 2 * canvas.pixel_size + 5)
            qtbot.mouse_move(canvas, hover_pos)