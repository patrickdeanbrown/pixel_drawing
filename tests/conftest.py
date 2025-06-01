"""
Shared pytest configuration and fixtures for the Pixel Drawing test suite.

This module provides common test fixtures, configuration, and utilities
used across unit, integration, and UI tests.
"""

import os
import sys
import pytest
import tempfile
import json
from pathlib import Path
from typing import Dict, Any, Generator
from unittest.mock import Mock, MagicMock

# Add the project root to the Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import application modules for testing
from pixel_drawing.models.pixel_art_model import PixelArtModel
from pixel_drawing.services.file_service import FileService
from pixel_drawing.controllers.tools.manager import ToolManager
from pixel_drawing.exceptions import ValidationError


# ============================================================================
# Test Configuration
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "ui: marks tests as UI tests")
    config.addinivalue_line("markers", "performance: marks tests as performance tests")
    config.addinivalue_line("markers", "slow: marks tests as slow running")


# ============================================================================
# Model Fixtures
# ============================================================================

@pytest.fixture
def empty_model() -> PixelArtModel:
    """Create a fresh, empty pixel art model for testing."""
    return PixelArtModel(width=8, height=8)


@pytest.fixture
def small_model() -> PixelArtModel:
    """Create a small 4x4 model for quick testing."""
    return PixelArtModel(width=4, height=4)


@pytest.fixture
def medium_model() -> PixelArtModel:
    """Create a medium 16x16 model for testing."""
    return PixelArtModel(width=16, height=16)


@pytest.fixture
def model_with_pixels(empty_model: PixelArtModel) -> PixelArtModel:
    """Create a model with some predefined pixels for testing."""
    from PyQt6.QtGui import QColor
    
    # Set some test pixels
    empty_model.set_pixel(0, 0, QColor(255, 0, 0))    # Red
    empty_model.set_pixel(1, 0, QColor(0, 255, 0))    # Green
    empty_model.set_pixel(0, 1, QColor(0, 0, 255))    # Blue
    empty_model.set_pixel(1, 1, QColor(255, 255, 0))  # Yellow
    
    return empty_model


# ============================================================================
# File System Fixtures
# ============================================================================

@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for file operations testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def sample_project_data() -> Dict[str, Any]:
    """Sample project data for testing serialization."""
    return {
        "width": 4,
        "height": 4,
        "pixels": {
            "0,0": "#FF0000",
            "1,0": "#00FF00", 
            "0,1": "#0000FF",
            "1,1": "#FFFF00"
        }
    }


@pytest.fixture
def sample_project_file(temp_dir: Path, sample_project_data: Dict[str, Any]) -> Path:
    """Create a sample project file for loading tests."""
    file_path = temp_dir / "sample_project.json"
    with open(file_path, 'w') as f:
        json.dump(sample_project_data, f, indent=2)
    return file_path


@pytest.fixture
def invalid_project_file(temp_dir: Path) -> Path:
    """Create an invalid project file for error testing."""
    file_path = temp_dir / "invalid_project.json"
    with open(file_path, 'w') as f:
        f.write("{ invalid json content")
    return file_path


# ============================================================================
# Service Fixtures
# ============================================================================

@pytest.fixture
def file_service() -> FileService:
    """Create a file service instance for testing."""
    return FileService()


@pytest.fixture
def tool_manager(empty_model: PixelArtModel) -> ToolManager:
    """Create a tool manager with an empty model."""
    return ToolManager(empty_model)


# ============================================================================
# Mock Fixtures
# ============================================================================

@pytest.fixture
def mock_file_system():
    """Mock file system for isolated testing."""
    mock_fs = Mock()
    mock_fs.exists.return_value = True
    mock_fs.read_text.return_value = '{"width": 4, "height": 4, "pixels": {}}'
    mock_fs.write_text.return_value = None
    return mock_fs


@pytest.fixture
def mock_logger():
    """Mock logger for testing without side effects."""
    mock_log = Mock()
    mock_log.info.return_value = None
    mock_log.debug.return_value = None
    mock_log.warning.return_value = None
    mock_log.error.return_value = None
    return mock_log


@pytest.fixture
def mock_qt_application():
    """Mock Qt application for UI testing without actual GUI."""
    try:
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        yield app
    except ImportError:
        # Fallback mock if PyQt6 not available
        mock_app = Mock()
        mock_app.exec.return_value = 0
        yield mock_app


# ============================================================================
# Color Fixtures
# ============================================================================

@pytest.fixture
def test_colors():
    """Common colors used in testing."""
    try:
        from PyQt6.QtGui import QColor
        return {
            'red': QColor(255, 0, 0),
            'green': QColor(0, 255, 0),
            'blue': QColor(0, 0, 255),
            'white': QColor(255, 255, 255),
            'black': QColor(0, 0, 0),
            'transparent': QColor(0, 0, 0, 0),
            'invalid': QColor()  # Invalid color for error testing
        }
    except ImportError:
        # Fallback for when PyQt6 is not available
        return {
            'red': Mock(name='red_color'),
            'green': Mock(name='green_color'),
            'blue': Mock(name='blue_color'),
            'white': Mock(name='white_color'),
            'black': Mock(name='black_color'),
            'transparent': Mock(name='transparent_color'),
            'invalid': Mock(name='invalid_color')
        }


# ============================================================================
# Performance Testing Fixtures
# ============================================================================

@pytest.fixture
def large_model() -> PixelArtModel:
    """Create a large model for performance testing."""
    return PixelArtModel(width=64, height=64)


@pytest.fixture
def performance_timer():
    """Timer utility for performance testing."""
    import time
    
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.perf_counter()
        
        def stop(self):
            self.end_time = time.perf_counter()
            return self.duration
        
        @property
        def duration(self) -> float:
            if self.start_time is None or self.end_time is None:
                return 0.0
            return self.end_time - self.start_time
    
    return Timer()


# ============================================================================
# Test Data Fixtures
# ============================================================================

@pytest.fixture
def edge_case_coordinates():
    """Coordinate edge cases for boundary testing."""
    return {
        'valid_origin': (0, 0),
        'valid_corner': (7, 7),  # For 8x8 model
        'negative_x': (-1, 0),
        'negative_y': (0, -1),
        'negative_both': (-1, -1),
        'overflow_x': (8, 0),    # For 8x8 model  
        'overflow_y': (0, 8),    # For 8x8 model
        'overflow_both': (8, 8), # For 8x8 model
        'large_positive': (1000, 1000)
    }


@pytest.fixture
def invalid_canvas_dimensions():
    """Invalid canvas dimensions for validation testing."""
    return [
        (-1, 10),    # Negative width
        (10, -1),    # Negative height
        (0, 10),     # Zero width
        (10, 0),     # Zero height
        (257, 10),   # Width too large
        (10, 257),   # Height too large
        (-1, -1),    # Both negative
        (0, 0),      # Both zero
    ]


@pytest.fixture
def valid_canvas_dimensions():
    """Valid canvas dimensions for testing."""
    return [
        (1, 1),      # Minimum valid
        (8, 8),      # Small
        (32, 32),    # Default
        (64, 64),    # Large
        (256, 256),  # Maximum valid
        (16, 32),    # Rectangular
        (1, 256),    # Extreme aspect ratio
        (256, 1),    # Extreme aspect ratio
    ]


# ============================================================================
# Cleanup and Utilities
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup_environment():
    """Automatically clean up test environment after each test."""
    yield
    # Any cleanup code here runs after each test
    
    # Clear any singleton instances
    # Reset global state
    # Clean up temporary resources


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Add markers based on test location
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "ui" in str(item.fspath):
            item.add_marker(pytest.mark.ui)
        elif "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)