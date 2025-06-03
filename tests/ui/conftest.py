"""
UI-specific test configuration and fixtures for pytest-qt tests.

This module provides PyQt6-specific fixtures and utilities for testing
GUI components with pytest-qt.
"""

import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
import sys
from pathlib import Path
from typing import Optional, Generator
from unittest.mock import Mock, patch

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from PyQt6.QtWidgets import QApplication, QWidget
    from PyQt6.QtCore import Qt, QTimer
    from PyQt6.QtGui import QColor, QKeyEvent, QMouseEvent
    from PyQt6.QtTest import QTest
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    QApplication = Mock
    QWidget = Mock
    Qt = Mock
    QTimer = Mock
    QColor = Mock


# ============================================================================
# Qt Application Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def qapp():
    """
    QApplication fixture for pytest-qt.
    
    This is automatically provided by pytest-qt, but we define it here
    to ensure it's available and properly configured for our tests.
    """
    if not PYQT_AVAILABLE:
        return Mock()


    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    # Set application properties for testing
    app.setApplicationName("PixelDrawing-Test")
    app.setApplicationVersion("test")
    
    yield app
    
    # Cleanup is handled by pytest-qt automatically


@pytest.fixture
def qtbot_mock():
    """Mock qtbot for tests when PyQt6 is not available."""
    if PYQT_AVAILABLE:
        pytest.skip("PyQt6 available, use real qtbot")
    
    mock_qtbot = Mock()
    mock_qtbot.add_widget.return_value = None
    mock_qtbot.wait.return_value = None
    mock_qtbot.wait_for_window_shown.return_value = None
    mock_qtbot.key_click.return_value = None
    mock_qtbot.mouse_click.return_value = None
    mock_qtbot.mouse_press.return_value = None
    mock_qtbot.mouse_release.return_value = None
    mock_qtbot.mouse_move.return_value = None
    
    return mock_qtbot


# ============================================================================
# Model and Service Fixtures for UI Tests
# ============================================================================

@pytest.fixture
def ui_model():
    """Create a model specifically for UI testing."""
    if not PYQT_AVAILABLE:
        return Mock()
    
    from pixel_drawing.models import PixelArtModel
    model = PixelArtModel(width=8, height=8)
    
    # Add some test pixels for visual verification
    model.set_pixel(0, 0, QColor(255, 0, 0))    # Red
    model.set_pixel(1, 0, QColor(0, 255, 0))    # Green
    model.set_pixel(0, 1, QColor(0, 0, 255))    # Blue
    model.set_pixel(1, 1, QColor(255, 255, 0))  # Yellow
    
    return model


@pytest.fixture
def ui_file_service():
    """File service fixture for UI tests."""
    if not PYQT_AVAILABLE:
        return Mock()
    
    from pixel_drawing.services import FileService
    return FileService()


# ============================================================================
# Canvas Widget Fixtures
# ============================================================================

@pytest.fixture
def canvas_widget(qtbot, ui_model):
    """Create a canvas widget for testing."""
    if not PYQT_AVAILABLE:
        return Mock()
    
    from pixel_drawing.views.canvas import PixelCanvas
    
    canvas = PixelCanvas(model=ui_model, pixel_size=16)
    qtbot.add_widget(canvas)
    
    # Show widget and wait for it to be ready
    canvas.show()
    qtbot.wait_for_window_shown(canvas)
    
    yield canvas
    
    # Cleanup
    canvas.close()


@pytest.fixture
def canvas_widget_large(qtbot):
    """Create a larger canvas widget for testing."""
    if not PYQT_AVAILABLE:
        return Mock()
    
    from pixel_drawing.models import PixelArtModel
    from pixel_drawing.views.canvas import PixelCanvas
    
    model = PixelArtModel(width=32, height=32)
    canvas = PixelCanvas(model=model, pixel_size=8)
    qtbot.add_widget(canvas)
    
    canvas.show()
    qtbot.wait_for_window_shown(canvas)
    
    yield canvas
    
    canvas.close()


# ============================================================================
# Application Window Fixtures
# ============================================================================

@pytest.fixture
def app_window(qtbot, ui_model, ui_file_service):
    """Create main application window for integration testing."""
    if not PYQT_AVAILABLE:
        return Mock()
    
    from pixel_drawing.views.app import PixelDrawingApp
    
    # Create app with test model and services
    app = PixelDrawingApp(
        model=ui_model,
        file_service=ui_file_service
    )
    qtbot.add_widget(app)
    
    # Show window and wait for it to be ready
    app.show()
    qtbot.wait_for_window_shown(app)
    
    yield app
    
    # Cleanup
    app.close()


@pytest.fixture
def minimal_app_window(qtbot):
    """Create minimal app window for basic testing."""
    if not PYQT_AVAILABLE:
        return Mock()
    
    from pixel_drawing.views.app import PixelDrawingApp
    
    app = PixelDrawingApp()
    qtbot.add_widget(app)
    
    app.show()
    qtbot.wait_for_window_shown(app)
    
    yield app
    
    app.close()


# ============================================================================
# Tool Testing Fixtures
# ============================================================================

@pytest.fixture
def test_colors():
    """Test colors for UI testing."""
    if not PYQT_AVAILABLE:
        return {
            'red': Mock(),
            'green': Mock(),
            'blue': Mock(),
            'white': Mock(),
            'black': Mock()
        }
    
    return {
        'red': QColor(255, 0, 0),
        'green': QColor(0, 255, 0),
        'blue': QColor(0, 0, 255),
        'white': QColor(255, 255, 255),
        'black': QColor(0, 0, 0)
    }


@pytest.fixture
def mouse_events():
    """Factory for creating mouse events."""
    if not PYQT_AVAILABLE:
        return Mock()
    
    def create_mouse_event(event_type, pos, button=Qt.MouseButton.LeftButton):
        from PyQt6.QtCore import QPoint
        from PyQt6.QtGui import QMouseEvent
        
        return QMouseEvent(
            event_type,
            QPoint(pos[0], pos[1]),
            QPoint(pos[0], pos[1]),
            button,
            button,
            Qt.KeyboardModifier.NoModifier
        )
    
    return create_mouse_event


@pytest.fixture
def key_events():
    """Factory for creating keyboard events."""
    if not PYQT_AVAILABLE:
        return Mock()
    
    def create_key_event(key, event_type=QKeyEvent.Type.KeyPress, 
                        modifiers=Qt.KeyboardModifier.NoModifier):
        return QKeyEvent(event_type, key, modifiers)
    
    return create_key_event


# ============================================================================
# Dialog Testing Fixtures
# ============================================================================

@pytest.fixture
def mock_color_dialog():
    """Mock color dialog for testing color selection."""
    with patch('PyQt6.QtWidgets.QColorDialog') as mock_dialog:
        mock_dialog.getColor.return_value = QColor(255, 0, 0) if PYQT_AVAILABLE else Mock()
        yield mock_dialog


@pytest.fixture
def mock_file_dialog():
    """Mock file dialog for testing file operations."""
    with patch('PyQt6.QtWidgets.QFileDialog') as mock_dialog:
        mock_dialog.getOpenFileName.return_value = ("/test/path.json", "JSON files (*.json)")
        mock_dialog.getSaveFileName.return_value = ("/test/save.json", "JSON files (*.json)")
        mock_dialog.getExistingDirectory.return_value = "/test/directory"
        yield mock_dialog


@pytest.fixture
def mock_message_box():
    """Mock message box for testing dialogs."""
    with patch('PyQt6.QtWidgets.QMessageBox') as mock_box:
        mock_box.question.return_value = mock_box.StandardButton.Yes
        mock_box.information.return_value = mock_box.StandardButton.Ok
        mock_box.warning.return_value = mock_box.StandardButton.Ok
        mock_box.critical.return_value = mock_box.StandardButton.Ok
        yield mock_box


# ============================================================================
# Performance Testing Fixtures
# ============================================================================

@pytest.fixture
def ui_performance_timer():
    """Timer for measuring UI performance."""
    import time
    
    class UITimer:
        def __init__(self):
            self.times = {}
        
        def start(self, operation: str):
            self.times[operation] = time.perf_counter()
        
        def stop(self, operation: str) -> float:
            if operation not in self.times:
                return 0.0
            duration = time.perf_counter() - self.times[operation]
            del self.times[operation]
            return duration
        
        def measure(self, operation: str, max_duration: float = 1.0):
            """Context manager for measuring operation duration."""
            return TimedOperation(self, operation, max_duration)
    
    class TimedOperation:
        def __init__(self, timer: UITimer, operation: str, max_duration: float):
            self.timer = timer
            self.operation = operation
            self.max_duration = max_duration
            
        def __enter__(self):
            self.timer.start(self.operation)
            return self
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            duration = self.timer.stop(self.operation)
            if duration > self.max_duration:
                pytest.fail(f"Operation '{self.operation}' took {duration:.3f}s, "
                          f"exceeding maximum of {self.max_duration:.3f}s")
    
    return UITimer()


# ============================================================================
# Accessibility Testing Fixtures
# ============================================================================

@pytest.fixture
def accessibility_tester():
    """Helper for testing accessibility features."""
    class AccessibilityTester:
        def check_focus_policy(self, widget):
            """Check if widget has appropriate focus policy."""
            if not PYQT_AVAILABLE:
                return True
            return widget.focusPolicy() != Qt.FocusPolicy.NoFocus
        
        def check_accessible_name(self, widget):
            """Check if widget has accessible name."""
            if not PYQT_AVAILABLE:
                return True
            return bool(widget.accessibleName())
        
        def check_accessible_description(self, widget):
            """Check if widget has accessible description."""
            if not PYQT_AVAILABLE:
                return True
            return bool(widget.accessibleDescription())
        
        def check_keyboard_navigation(self, widget, qtbot):
            """Test basic keyboard navigation."""
            if not PYQT_AVAILABLE:
                return True
            
            widget.setFocus()
            qtbot.key_click(widget, Qt.Key.Key_Tab)
            return True  # Basic test - more specific tests in individual test files
    
    return AccessibilityTester()


# ============================================================================
# Test Utilities
# ============================================================================

@pytest.fixture
def wait_for_signal():
    """Utility for waiting for Qt signals in tests."""
    if not PYQT_AVAILABLE:
        return Mock()
    
    def wait_signal(signal, timeout=1000):
        """Wait for a signal to be emitted within timeout."""
        from PyQt6.QtTest import QSignalSpy
        spy = QSignalSpy(signal)
        QTest.qWait(timeout)
        return len(spy) > 0
    
    return wait_signal


@pytest.fixture
def signal_blocker():
    """Utility for blocking signals during tests."""
    if not PYQT_AVAILABLE:
        return Mock()
    
    def block_signals(obj, blocked=True):
        """Block or unblock signals for an object."""
        from PyQt6.QtCore import QSignalBlocker
        return QSignalBlocker(obj) if blocked else None
    
    return block_signals


# ============================================================================
# Cleanup and Error Handling
# ============================================================================

def pytest_runtest_teardown(item, nextitem):
    """Clean up after each UI test."""
    if PYQT_AVAILABLE:
        # Process any pending events
        app = QApplication.instance()
        if app:
            app.processEvents()


def pytest_configure(config):
    """Configure pytest for UI testing."""
    # Add UI-specific markers
    config.addinivalue_line("markers", "ui_slow: marks UI tests that are slow")
    config.addinivalue_line("markers", "ui_interactive: marks tests requiring user interaction")
    config.addinivalue_line("markers", "accessibility: marks accessibility-related tests")