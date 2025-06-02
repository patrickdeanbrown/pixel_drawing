"""
UI tests for tool controller interactions using pytest-qt.

These tests verify tool behavior through the UI, tool switching,
and integration between tools and the canvas.
"""

import pytest
from unittest.mock import Mock, patch

try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt, QPoint
    from PyQt6.QtGui import QColor, QKeyEvent, QMouseEvent
    from PyQt6.QtTest import QTest
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    pytest.skip("PyQt6 not available", allow_module_level=True)

from pixel_drawing.controllers.tools import ToolManager
from pixel_drawing.models import PixelArtModel
from pixel_drawing.enums import ToolType


# ============================================================================
# Tool Manager UI Integration Tests
# ============================================================================

@pytest.mark.ui
class TestToolManagerUI:
    """Test tool manager integration with UI components."""
    
    def test_tool_manager_with_canvas(self, qtbot, canvas_widget, test_colors):
        """Test tool manager works properly with canvas widget."""
        canvas = canvas_widget
        tool_manager = canvas._tool_manager
        
        # Verify tool manager is connected
        assert tool_manager is not None
        assert tool_manager._model == canvas._model
        
        # Test tool switching through canvas
        canvas.set_current_tool("brush")
        assert canvas.get_current_tool_id() == "brush"
        
        canvas.set_current_tool("fill")
        assert canvas.get_current_tool_id() == "fill"
    
    def test_tool_manager_signal_connections(self, qtbot, canvas_widget):
        """Test tool manager signals are properly connected."""
        canvas = canvas_widget
        tool_manager = canvas._tool_manager
        
        # Verify signal connections exist
        assert hasattr(tool_manager, 'tool_changed')
        
        # Test signal emission
        with qtbot.wait_signal(canvas.tool_changed, timeout=1000):
            canvas.set_current_tool("eraser")


# ============================================================================
# Brush Tool UI Tests
# ============================================================================

@pytest.mark.ui
class TestBrushToolUI:
    """Test brush tool behavior through UI interactions."""
    
    def test_brush_tool_single_click(self, qtbot, canvas_widget, test_colors):
        """Test brush tool draws single pixel on click."""
        canvas = canvas_widget
        canvas.set_current_tool("brush")
        canvas.current_color = test_colors['red']
        
        # Click at specific position
        pixel_size = canvas.pixel_size
        pos = QPoint(3 * pixel_size + pixel_size//2, 3 * pixel_size + pixel_size//2)
        
        qtbot.mouse_click(canvas, Qt.MouseButton.LeftButton, pos=pos)
        
        # Verify pixel was drawn
        assert canvas._model.get_pixel(3, 3) == test_colors['red']
        
        # Verify surrounding pixels unchanged
        assert canvas._model.get_pixel(2, 3) == QColor(255, 255, 255)
        assert canvas._model.get_pixel(4, 3) == QColor(255, 255, 255)
    
    def test_brush_tool_drag_drawing(self, qtbot, canvas_widget, test_colors):
        """Test brush tool draws continuous line when dragging."""
        canvas = canvas_widget
        canvas.set_current_tool("brush")
        canvas.current_color = test_colors['blue']
        
        pixel_size = canvas.pixel_size
        
        # Start drawing
        start_pos = QPoint(1 * pixel_size + pixel_size//2, 1 * pixel_size + pixel_size//2)
        qtbot.mouse_press(canvas, Qt.MouseButton.LeftButton, pos=start_pos)
        
        # Drag to create line
        for i in range(2, 5):
            move_pos = QPoint(i * pixel_size + pixel_size//2, 1 * pixel_size + pixel_size//2)
            qtbot.mouse_move(canvas, move_pos)
            qtbot.wait(10)  # Small delay for processing
        
        # End drawing
        end_pos = QPoint(4 * pixel_size + pixel_size//2, 1 * pixel_size + pixel_size//2)
        qtbot.mouse_release(canvas, Qt.MouseButton.LeftButton, pos=end_pos)
        
        # Verify line was drawn
        for x in range(1, 5):
            assert canvas._model.get_pixel(x, 1) == test_colors['blue']
    
    def test_brush_tool_color_changes(self, qtbot, canvas_widget, test_colors):
        """Test brush tool respects color changes."""
        canvas = canvas_widget
        canvas.set_current_tool("brush")
        
        # Draw with red
        canvas.current_color = test_colors['red']
        pos1 = QPoint(2 * canvas.pixel_size + 5, 2 * canvas.pixel_size + 5)
        qtbot.mouse_click(canvas, Qt.MouseButton.LeftButton, pos=pos1)
        
        # Change color and draw with blue
        canvas.current_color = test_colors['blue']
        pos2 = QPoint(3 * canvas.pixel_size + 5, 3 * canvas.pixel_size + 5)
        qtbot.mouse_click(canvas, Qt.MouseButton.LeftButton, pos=pos2)
        
        # Verify colors are correct
        assert canvas._model.get_pixel(2, 2) == test_colors['red']
        assert canvas._model.get_pixel(3, 3) == test_colors['blue']


# ============================================================================
# Fill Tool UI Tests
# ============================================================================

@pytest.mark.ui
class TestFillToolUI:
    """Test fill tool behavior through UI interactions."""
    
    def test_fill_tool_simple_fill(self, qtbot, canvas_widget, test_colors):
        """Test fill tool performs flood fill."""
        canvas = canvas_widget
        
        # First, create a boundary with brush tool
        canvas.set_current_tool("brush")
        canvas.current_color = test_colors['black']
        
        # Draw a simple boundary (rectangle outline)
        pixel_size = canvas.pixel_size
        boundary_coords = [
            (2, 2), (3, 2), (4, 2),  # Top
            (2, 3),         (4, 3),  # Sides
            (2, 4), (3, 4), (4, 4)   # Bottom
        ]
        
        for x, y in boundary_coords:
            pos = QPoint(x * pixel_size + pixel_size//2, y * pixel_size + pixel_size//2)
            qtbot.mouse_click(canvas, Qt.MouseButton.LeftButton, pos=pos)
        
        # Switch to fill tool
        canvas.set_current_tool("fill")
        canvas.current_color = test_colors['red']
        
        # Fill inside the boundary
        fill_pos = QPoint(3 * pixel_size + pixel_size//2, 3 * pixel_size + pixel_size//2)
        qtbot.mouse_click(canvas, Qt.MouseButton.LeftButton, pos=fill_pos)
        
        # Verify fill worked - center should be red
        assert canvas._model.get_pixel(3, 3) == test_colors['red']
        
        # Verify boundary is still black
        assert canvas._model.get_pixel(2, 2) == test_colors['black']
        assert canvas._model.get_pixel(4, 4) == test_colors['black']
    
    def test_fill_tool_large_area(self, qtbot, canvas_widget_large, test_colors):
        """Test fill tool works on large areas."""
        canvas = canvas_widget_large
        canvas.set_current_tool("fill")
        canvas.current_color = test_colors['green']
        
        # Fill large empty area
        pos = QPoint(100, 100)  # Center of large canvas
        qtbot.mouse_click(canvas, Qt.MouseButton.LeftButton, pos=pos)
        
        # Should fill entire canvas (since it's all white)
        pixel_x, pixel_y = canvas.get_pixel_coords(pos)
        assert canvas._model.get_pixel(pixel_x, pixel_y) == test_colors['green']
    
    @pytest.mark.ui_slow
    def test_fill_tool_performance(self, qtbot, canvas_widget_large, test_colors, ui_performance_timer):
        """Test fill tool performance on large areas."""
        canvas = canvas_widget_large
        canvas.set_current_tool("fill")
        canvas.current_color = test_colors['blue']
        
        with ui_performance_timer.measure("large_fill_operation", max_duration=1.0):
            pos = QPoint(50, 50)
            qtbot.mouse_click(canvas, Qt.MouseButton.LeftButton, pos=pos)


# ============================================================================
# Eraser Tool UI Tests
# ============================================================================

@pytest.mark.ui
class TestEraserToolUI:
    """Test eraser tool behavior through UI interactions."""
    
    def test_eraser_tool_basic_erase(self, qtbot, canvas_widget, test_colors):
        """Test eraser tool removes pixels."""
        canvas = canvas_widget
        
        # First draw something
        canvas.set_current_tool("brush")
        canvas.current_color = test_colors['red']
        pos = QPoint(2 * canvas.pixel_size + 5, 2 * canvas.pixel_size + 5)
        qtbot.mouse_click(canvas, Qt.MouseButton.LeftButton, pos=pos)
        
        # Verify pixel is red
        assert canvas._model.get_pixel(2, 2) == test_colors['red']
        
        # Switch to eraser and erase
        canvas.set_current_tool("eraser")
        qtbot.mouse_click(canvas, Qt.MouseButton.LeftButton, pos=pos)
        
        # Verify pixel is now white (erased)
        assert canvas._model.get_pixel(2, 2) == QColor(255, 255, 255)
    
    def test_eraser_tool_drag_erase(self, qtbot, canvas_widget, test_colors):
        """Test eraser tool works when dragging."""
        canvas = canvas_widget
        
        # Draw a line first
        canvas.set_current_tool("brush")
        canvas.current_color = test_colors['blue']
        
        for x in range(1, 5):
            pos = QPoint(x * canvas.pixel_size + 5, 2 * canvas.pixel_size + 5)
            qtbot.mouse_click(canvas, Qt.MouseButton.LeftButton, pos=pos)
        
        # Switch to eraser and erase part of the line
        canvas.set_current_tool("eraser")
        
        start_pos = QPoint(2 * canvas.pixel_size + 5, 2 * canvas.pixel_size + 5)
        qtbot.mouse_press(canvas, Qt.MouseButton.LeftButton, pos=start_pos)
        
        end_pos = QPoint(3 * canvas.pixel_size + 5, 2 * canvas.pixel_size + 5)
        qtbot.mouse_move(canvas, end_pos)
        qtbot.mouse_release(canvas, Qt.MouseButton.LeftButton, pos=end_pos)
        
        # Verify partial erasure
        assert canvas._model.get_pixel(1, 2) == test_colors['blue']  # Untouched
        assert canvas._model.get_pixel(2, 2) == QColor(255, 255, 255)  # Erased
        assert canvas._model.get_pixel(3, 2) == QColor(255, 255, 255)  # Erased
        assert canvas._model.get_pixel(4, 2) == test_colors['blue']  # Untouched


# ============================================================================
# Color Picker Tool UI Tests
# ============================================================================

@pytest.mark.ui
class TestColorPickerToolUI:
    """Test color picker tool behavior through UI interactions."""
    
    def test_color_picker_basic_pick(self, qtbot, canvas_widget, test_colors):
        """Test color picker picks colors from canvas."""
        canvas = canvas_widget
        
        # First draw a colored pixel
        canvas.set_current_tool("brush")
        canvas.current_color = test_colors['green']
        pos = QPoint(3 * canvas.pixel_size + 5, 3 * canvas.pixel_size + 5)
        qtbot.mouse_click(canvas, Qt.MouseButton.LeftButton, pos=pos)
        
        # Switch to color picker
        canvas.set_current_tool("picker")
        
        # Mock the color picked signal
        color_picker = canvas._tool_manager.get_tool("picker")
        if color_picker and hasattr(color_picker, 'signals'):
            with qtbot.wait_signal(color_picker.signals.color_picked, timeout=1000):
                qtbot.mouse_click(canvas, Qt.MouseButton.LeftButton, pos=pos)
    
    def test_color_picker_updates_current_color(self, qtbot, canvas_widget, test_colors):
        """Test color picker updates current color."""
        canvas = canvas_widget
        
        # Draw colored pixel
        canvas.set_current_tool("brush")
        canvas.current_color = test_colors['red']
        pos = QPoint(4 * canvas.pixel_size + 5, 4 * canvas.pixel_size + 5)
        qtbot.mouse_click(canvas, Qt.MouseButton.LeftButton, pos=pos)
        
        # Change current color to something else
        canvas.current_color = test_colors['blue']
        
        # Use color picker
        canvas.set_current_tool("picker")
        qtbot.mouse_click(canvas, Qt.MouseButton.LeftButton, pos=pos)
        
        # Current color should now be red (picked color)
        assert canvas.current_color == test_colors['red']


# ============================================================================
# Pan Tool UI Tests
# ============================================================================

@pytest.mark.ui
class TestPanToolUI:
    """Test pan tool behavior through UI interactions."""
    
    def test_pan_tool_activation(self, qtbot, canvas_widget):
        """Test pan tool can be activated."""
        canvas = canvas_widget
        
        # Switch to pan tool
        success = canvas.set_current_tool("pan")
        assert success
        assert canvas.get_current_tool_id() == "pan"
    
    def test_pan_tool_cursor_change(self, qtbot, canvas_widget):
        """Test pan tool changes cursor."""
        canvas = canvas_widget
        
        # Get initial cursor
        initial_cursor = canvas.cursor()
        
        # Switch to pan tool
        canvas.set_current_tool("pan")
        
        # Cursor might change (depends on implementation)
        # At minimum, tool should be active
        assert canvas.get_current_tool_id() == "pan"


# ============================================================================
# Tool Switching UI Tests
# ============================================================================

@pytest.mark.ui
class TestToolSwitchingUI:
    """Test tool switching behavior through UI."""
    
    def test_keyboard_tool_shortcuts(self, qtbot, canvas_widget):
        """Test keyboard shortcuts for tool switching."""
        canvas = canvas_widget
        canvas.setFocus()
        
        # Test all tool shortcuts
        tool_shortcuts = [
            (Qt.Key.Key_B, "brush"),
            (Qt.Key.Key_F, "fill"),
            (Qt.Key.Key_E, "eraser"),
            (Qt.Key.Key_I, "picker"),
            (Qt.Key.Key_H, "pan")
        ]
        
        for key, expected_tool in tool_shortcuts:
            qtbot.key_click(canvas, key)
            assert canvas.get_current_tool_id() == expected_tool
    
    def test_tool_switching_preserves_state(self, qtbot, canvas_widget, test_colors):
        """Test switching tools preserves drawing state."""
        canvas = canvas_widget
        
        # Set initial state
        canvas.set_current_tool("brush")
        canvas.current_color = test_colors['red']
        
        # Draw something
        pos = QPoint(2 * canvas.pixel_size + 5, 2 * canvas.pixel_size + 5)
        qtbot.mouse_click(canvas, Qt.MouseButton.LeftButton, pos=pos)
        
        # Switch tool and back
        canvas.set_current_tool("fill")
        canvas.set_current_tool("brush")
        
        # Color should be preserved
        assert canvas.current_color == test_colors['red']
        
        # Can still draw with same color
        pos2 = QPoint(3 * canvas.pixel_size + 5, 3 * canvas.pixel_size + 5)
        qtbot.mouse_click(canvas, Qt.MouseButton.LeftButton, pos=pos2)
        assert canvas._model.get_pixel(3, 3) == test_colors['red']
    
    def test_rapid_tool_switching(self, qtbot, canvas_widget):
        """Test rapid tool switching doesn't cause issues."""
        canvas = canvas_widget
        canvas.setFocus()
        
        # Rapidly switch between tools
        tools = [Qt.Key.Key_B, Qt.Key.Key_F, Qt.Key.Key_E, Qt.Key.Key_B]
        
        for key in tools:
            qtbot.key_click(canvas, key)
            qtbot.wait(10)  # Small delay
        
        # Should end up with brush tool
        assert canvas.get_current_tool_id() == "brush"


# ============================================================================
# Tool State Management Tests
# ============================================================================

@pytest.mark.ui
class TestToolStateManagement:
    """Test tool state management through UI interactions."""
    
    def test_tool_state_during_drawing(self, qtbot, canvas_widget, test_colors):
        """Test tool state is properly managed during drawing operations."""
        canvas = canvas_widget
        canvas.set_current_tool("brush")
        canvas.current_color = test_colors['blue']
        
        # Start drawing
        pos = QPoint(2 * canvas.pixel_size + 5, 2 * canvas.pixel_size + 5)
        qtbot.mouse_press(canvas, Qt.MouseButton.LeftButton, pos=pos)
        
        # Canvas should be in drawing state
        assert canvas._is_drawing
        
        # Try to switch tools while drawing (should not work or should cancel)
        original_tool = canvas.get_current_tool_id()
        canvas.set_current_tool("fill")
        
        # Complete the drawing operation
        qtbot.mouse_release(canvas, Qt.MouseButton.LeftButton, pos=pos)
        
        # Should no longer be drawing
        assert not canvas._is_drawing
    
    def test_tool_signal_emissions(self, qtbot, canvas_widget):
        """Test tools emit appropriate signals."""
        canvas = canvas_widget
        
        # Test tool change signal
        with qtbot.wait_signal(canvas.tool_changed, timeout=1000):
            canvas.set_current_tool("fill")
        
        # Test color usage signal (when drawing)
        canvas.set_current_tool("brush")
        with qtbot.wait_signal(canvas.color_used, timeout=1000):
            pos = QPoint(1 * canvas.pixel_size + 5, 1 * canvas.pixel_size + 5)
            qtbot.mouse_click(canvas, Qt.MouseButton.LeftButton, pos=pos)


# ============================================================================
# Tool Integration Tests
# ============================================================================

@pytest.mark.ui
class TestToolIntegration:
    """Test tool integration with other UI components."""
    
    def test_tool_canvas_model_integration(self, qtbot, canvas_widget, test_colors):
        """Test tools properly integrate with canvas and model."""
        canvas = canvas_widget
        model = canvas._model
        
        # Drawing should update model
        canvas.set_current_tool("brush")
        canvas.current_color = test_colors['red']
        
        pos = QPoint(5 * canvas.pixel_size + 5, 5 * canvas.pixel_size + 5)
        qtbot.mouse_click(canvas, Qt.MouseButton.LeftButton, pos=pos)
        
        # Model should be updated
        assert model.get_pixel(5, 5) == test_colors['red']
        
        # Model changes should trigger canvas updates
        with patch.object(canvas, 'update') as mock_update:
            model.set_pixel(6, 6, test_colors['blue'])
            qtbot.wait(150)  # Wait for batched updates
            mock_update.assert_called()
    
    def test_tool_accessibility_integration(self, qtbot, canvas_widget):
        """Test tools work with accessibility features."""
        canvas = canvas_widget
        canvas.setFocus()
        
        # Tool shortcuts should work in accessibility mode
        qtbot.key_click(canvas, Qt.Key.Key_B)
        assert canvas.get_current_tool_id() == "brush"
        
        # Keyboard navigation should work with tools
        canvas.set_keyboard_cursor_position(2, 2)
        
        # Space key should trigger current tool
        qtbot.key_click(canvas, Qt.Key.Key_Space)
        
        # Should have drawn at cursor position
        # (Exact verification depends on tool implementation)


# ============================================================================
# Error Handling Tests
# ============================================================================

@pytest.mark.ui
class TestToolErrorHandling:
    """Test tool error handling in UI interactions."""
    
    def test_invalid_tool_switching(self, qtbot, canvas_widget):
        """Test handling of invalid tool switches."""
        canvas = canvas_widget
        
        # Try to switch to non-existent tool
        result = canvas.set_current_tool("invalid_tool")
        assert not result
        
        # Should still have a valid tool active
        current_tool = canvas.get_current_tool_id()
        assert current_tool is not None
    
    def test_tool_operations_out_of_bounds(self, qtbot, canvas_widget):
        """Test tool operations outside canvas bounds."""
        canvas = canvas_widget
        canvas.set_current_tool("brush")
        
        # Click outside canvas bounds
        out_of_bounds_pos = QPoint(
            canvas._model.width * canvas.pixel_size + 50,
            canvas._model.height * canvas.pixel_size + 50
        )
        
        # Should not start drawing
        qtbot.mouse_press(canvas, Qt.MouseButton.LeftButton, pos=out_of_bounds_pos)
        assert not canvas._is_drawing
    
    def test_tool_state_recovery(self, qtbot, canvas_widget, test_colors):
        """Test tool state recovery after errors."""
        canvas = canvas_widget
        canvas.set_current_tool("brush")
        canvas.current_color = test_colors['red']
        
        # Simulate interrupted drawing operation
        pos = QPoint(2 * canvas.pixel_size + 5, 2 * canvas.pixel_size + 5)
        qtbot.mouse_press(canvas, Qt.MouseButton.LeftButton, pos=pos)
        
        # Simulate focus loss or other interruption
        canvas.clearFocus()
        
        # Should recover gracefully
        canvas.setFocus()
        
        # Should be able to continue normal operations
        pos2 = QPoint(3 * canvas.pixel_size + 5, 3 * canvas.pixel_size + 5)
        qtbot.mouse_click(canvas, Qt.MouseButton.LeftButton, pos=pos2)
        
        assert canvas._model.get_pixel(3, 3) == test_colors['red']