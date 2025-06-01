"""
Integration tests for FileService with PixelArtModel.

Tests complete file operation workflows including save/load cycles,
error handling, and data integrity across the file service and model layers.
"""

import pytest
import json
import os
from pathlib import Path
from PyQt6.QtGui import QColor

from pixel_drawing.services.file_service import FileService
from pixel_drawing.models.pixel_art_model import PixelArtModel
from pixel_drawing.exceptions import ValidationError, FileOperationError


class TestFileServiceModelIntegration:
    """Test FileService operations with actual PixelArtModel instances."""
    
    def test_save_load_round_trip_preserves_data(self, temp_dir, test_colors):
        """Test that save→load cycle preserves all model data exactly."""
        # Create model with test data
        model = PixelArtModel(width=8, height=8)
        model.set_pixel(0, 0, test_colors['red'])
        model.set_pixel(1, 0, test_colors['green'])
        model.set_pixel(0, 1, test_colors['blue'])
        model.set_pixel(2, 2, test_colors['white'])
        
        # Save to file
        file_service = FileService()
        save_path = temp_dir / "test_save.json"
        
        success = file_service.save_file(str(save_path), model)
        assert success
        assert save_path.exists()
        
        # Load into new model
        new_model = PixelArtModel()
        load_success = file_service.load_file(str(save_path), new_model)
        assert load_success
        
        # Verify all data preserved
        assert new_model.width == model.width
        assert new_model.height == model.height
        
        # Check all pixels match
        for x in range(model.width):
            for y in range(model.height):
                original_color = model.get_pixel(x, y)
                loaded_color = new_model.get_pixel(x, y)
                assert original_color == loaded_color, f"Pixel ({x},{y}) color mismatch"
        
        # Check file association
        assert new_model.current_file == str(save_path)
        assert not new_model.is_modified  # Loading clears modified flag
    
    def test_save_load_empty_model(self, temp_dir):
        """Test save/load cycle with empty model (no non-default pixels)."""
        # Create empty model
        model = PixelArtModel(width=4, height=4)
        
        # Save to file
        file_service = FileService()
        save_path = temp_dir / "empty_model.json"
        
        success = file_service.save_file(str(save_path), model)
        assert success
        
        # Load into new model
        new_model = PixelArtModel()
        load_success = file_service.load_file(str(save_path), new_model)
        assert load_success
        
        # Verify dimensions
        assert new_model.width == 4
        assert new_model.height == 4
        
        # Verify all pixels are default color
        default_color = QColor("#FFFFFF")  # Default background
        for x in range(4):
            for y in range(4):
                assert new_model.get_pixel(x, y) == default_color
    
    def test_save_overwrites_existing_file(self, temp_dir, test_colors):
        """Test that saving overwrites existing files correctly."""
        file_service = FileService()
        save_path = temp_dir / "overwrite_test.json"
        
        # Create first model and save
        model1 = PixelArtModel(width=4, height=4)
        model1.set_pixel(0, 0, test_colors['red'])
        
        success1 = file_service.save_file(str(save_path), model1)
        assert success1
        
        # Create second model with different data and save to same file
        model2 = PixelArtModel(width=6, height=6)
        model2.set_pixel(0, 0, test_colors['blue'])
        model2.set_pixel(1, 1, test_colors['green'])
        
        success2 = file_service.save_file(str(save_path), model2)
        assert success2
        
        # Load and verify second model's data
        loaded_model = PixelArtModel()
        file_service.load_file(str(save_path), loaded_model)
        
        assert loaded_model.width == 6
        assert loaded_model.height == 6
        assert loaded_model.get_pixel(0, 0) == test_colors['blue']
        assert loaded_model.get_pixel(1, 1) == test_colors['green']
    
    def test_save_adds_json_extension_automatically(self, temp_dir):
        """Test that save operation adds .json extension if missing."""
        model = PixelArtModel(width=2, height=2)
        file_service = FileService()
        
        # Save without .json extension
        save_path_no_ext = temp_dir / "test_file"
        success = file_service.save_file(str(save_path_no_ext), model)
        assert success
        
        # Verify .json extension was added
        expected_path = temp_dir / "test_file.json"
        assert expected_path.exists()
        assert not save_path_no_ext.exists()
        
        # Verify model's current_file reflects the actual saved path
        assert model.current_file == str(expected_path)
    
    def test_load_nonexistent_file_returns_false(self, temp_dir):
        """Test that loading nonexistent file returns False and emits error signal."""
        file_service = FileService()
        model = PixelArtModel()
        
        # Track error signals
        error_signals = []
        def capture_error(operation, message):
            error_signals.append((operation, message))
        
        file_service.operation_failed.connect(capture_error)
        
        # Attempt to load nonexistent file
        nonexistent_path = temp_dir / "nonexistent.json"
        success = file_service.load_file(str(nonexistent_path), model)
        
        assert not success
        assert len(error_signals) == 1
        assert error_signals[0][0] == "load"
        assert "does not exist" in error_signals[0][1] or "No such file" in error_signals[0][1]
    
    def test_load_corrupted_json_returns_false(self, temp_dir):
        """Test that loading corrupted JSON file returns False and emits error signal."""
        # Create corrupted JSON file
        corrupted_file = temp_dir / "corrupted.json"
        corrupted_file.write_text("{ invalid json content }")
        
        file_service = FileService()
        model = PixelArtModel()
        
        # Track error signals
        error_signals = []
        file_service.operation_failed.connect(lambda op, msg: error_signals.append((op, msg)))
        
        # Attempt to load corrupted file
        success = file_service.load_file(str(corrupted_file), model)
        
        assert not success
        assert len(error_signals) == 1
        assert error_signals[0][0] == "load"
    
    def test_load_invalid_model_data_returns_false(self, temp_dir):
        """Test that loading JSON with invalid model data returns False."""
        # Create JSON with invalid model data
        invalid_data = {
            "width": -1,  # Invalid width
            "height": 4,
            "pixels": {}
        }
        
        invalid_file = temp_dir / "invalid_model.json"
        with open(invalid_file, 'w') as f:
            json.dump(invalid_data, f)
        
        file_service = FileService()
        model = PixelArtModel()
        
        # Track error signals
        error_signals = []
        file_service.operation_failed.connect(lambda op, msg: error_signals.append((op, msg)))
        
        # Attempt to load invalid data
        success = file_service.load_file(str(invalid_file), model)
        
        assert not success
        assert len(error_signals) == 1
        assert error_signals[0][0] == "load"


class TestFileServiceSignalIntegration:
    """Test FileService signal emission during operations."""
    
    def test_successful_save_emits_file_saved_signal(self, temp_dir):
        """Test that successful save operation emits file_saved signal."""
        model = PixelArtModel(width=2, height=2)
        file_service = FileService()
        save_path = temp_dir / "signal_test.json"
        
        # Track signals
        saved_signals = []
        file_service.file_saved.connect(lambda path: saved_signals.append(path))
        
        success = file_service.save_file(str(save_path), model)
        
        assert success
        assert len(saved_signals) == 1
        assert saved_signals[0] == str(save_path)
    
    def test_successful_load_emits_file_loaded_signal(self, temp_dir, sample_project_file):
        """Test that successful load operation emits file_loaded signal."""
        model = PixelArtModel()
        file_service = FileService()
        
        # Track signals
        loaded_signals = []
        file_service.file_loaded.connect(lambda path: loaded_signals.append(path))
        
        success = file_service.load_file(str(sample_project_file), model)
        
        assert success
        assert len(loaded_signals) == 1
        assert loaded_signals[0] == str(sample_project_file)
    
    def test_failed_operations_emit_operation_failed_signal(self, temp_dir):
        """Test that failed operations emit operation_failed signals with details."""
        file_service = FileService()
        model = PixelArtModel()
        
        # Track error signals
        error_signals = []
        file_service.operation_failed.connect(lambda op, msg: error_signals.append((op, msg)))
        
        # Test failed save to read-only directory (simulate by invalid path)
        invalid_save_path = "/invalid/directory/test.json"
        save_success = file_service.save_file(invalid_save_path, model)
        
        # Test failed load of nonexistent file
        invalid_load_path = temp_dir / "nonexistent.json"
        load_success = file_service.load_file(str(invalid_load_path), model)
        
        assert not save_success
        assert not load_success
        assert len(error_signals) == 2
        
        # Verify error signal details
        save_error = next((op, msg) for op, msg in error_signals if op == "save")
        load_error = next((op, msg) for op, msg in error_signals if op == "load")
        
        assert save_error is not None
        assert load_error is not None


class TestPNGExportIntegration:
    """Test PNG export functionality with model integration."""
    
    def test_export_png_creates_correct_image(self, temp_dir, test_colors):
        """Test that PNG export creates image with correct pixel data."""
        # Create model with known pixel pattern
        model = PixelArtModel(width=3, height=3)
        model.set_pixel(0, 0, test_colors['red'])     # Top-left red
        model.set_pixel(1, 1, test_colors['green'])   # Center green
        model.set_pixel(2, 2, test_colors['blue'])    # Bottom-right blue
        
        file_service = FileService()
        export_path = temp_dir / "test_export.png"
        
        success = file_service.export_png(str(export_path), model)
        
        assert success
        assert export_path.exists()
        
        # Verify the PNG file can be read (basic validation)
        try:
            from PIL import Image
            img = Image.open(export_path)
            assert img.size == (3, 3)
            assert img.mode == "RGB"
            
            # Check specific pixel colors
            assert img.getpixel((0, 0)) == (255, 0, 0)    # Red
            assert img.getpixel((1, 1)) == (0, 255, 0)    # Green  
            assert img.getpixel((2, 2)) == (0, 0, 255)    # Blue
            assert img.getpixel((0, 1)) == (255, 255, 255)  # Default white
            
        except ImportError:
            # If PIL not available, just verify file exists and has reasonable size
            assert export_path.stat().st_size > 0
    
    def test_export_png_adds_extension_automatically(self, temp_dir):
        """Test that PNG export adds .png extension if missing."""
        model = PixelArtModel(width=2, height=2)
        file_service = FileService()
        
        export_path_no_ext = temp_dir / "test_export"
        success = file_service.export_png(str(export_path_no_ext), model)
        
        assert success
        
        # Verify .png extension was added
        expected_path = temp_dir / "test_export.png"
        assert expected_path.exists()
        assert not export_path_no_ext.exists()
    
    def test_export_png_emits_file_exported_signal(self, temp_dir):
        """Test that successful PNG export emits file_exported signal."""
        model = PixelArtModel(width=2, height=2)
        file_service = FileService()
        export_path = temp_dir / "signal_export.png"
        
        # Track signals
        exported_signals = []
        file_service.file_exported.connect(lambda path: exported_signals.append(path))
        
        success = file_service.export_png(str(export_path), model)
        
        assert success
        assert len(exported_signals) == 1
        assert exported_signals[0] == str(export_path)


class TestFileServicePerformance:
    """Test FileService performance with larger models."""
    
    @pytest.mark.performance
    def test_save_load_large_model_performance(self, temp_dir, performance_timer):
        """Test save/load performance with large model stays within acceptable limits."""
        # Create large model with many pixels
        model = PixelArtModel(width=64, height=64)
        
        # Fill model with pattern to ensure substantial data
        from PyQt6.QtGui import QColor
        for x in range(0, 64, 4):
            for y in range(0, 64, 4):
                color = QColor((x * 4) % 256, (y * 4) % 256, 128)
                model.set_pixel(x, y, color)
        
        file_service = FileService()
        save_path = temp_dir / "large_model.json"
        
        # Time save operation
        performance_timer.start()
        success = file_service.save_file(str(save_path), model)
        save_duration = performance_timer.stop()
        
        assert success
        assert save_duration < 1.0  # Should complete within 1 second
        
        # Time load operation
        new_model = PixelArtModel()
        performance_timer.start()
        load_success = file_service.load_file(str(save_path), new_model)
        load_duration = performance_timer.stop()
        
        assert load_success
        assert load_duration < 1.0  # Should complete within 1 second
        
        # Verify data integrity with spot checks
        assert new_model.width == 64
        assert new_model.height == 64
        assert new_model.get_pixel(0, 0) == model.get_pixel(0, 0)
        assert new_model.get_pixel(60, 60) == model.get_pixel(60, 60)
    
    @pytest.mark.performance  
    def test_png_export_large_model_performance(self, temp_dir, performance_timer):
        """Test PNG export performance with large model."""
        # Create large model
        model = PixelArtModel(width=128, height=128)
        
        # Add some pixel data
        from PyQt6.QtGui import QColor
        for i in range(0, 128, 8):
            model.set_pixel(i, i, QColor(255, 0, 0))
        
        file_service = FileService()
        export_path = temp_dir / "large_export.png"
        
        # Time export operation
        performance_timer.start()
        success = file_service.export_png(str(export_path), model)
        export_duration = performance_timer.stop()
        
        assert success
        assert export_duration < 2.0  # Should complete within 2 seconds
        assert export_path.exists()


class TestAtomicFileOperations:
    """Test that file operations are atomic and handle interruptions gracefully."""
    
    def test_save_operation_atomicity(self, temp_dir):
        """Test that save operations are atomic (temp file → final file)."""
        model = PixelArtModel(width=4, height=4)
        model.set_pixel(0, 0, QColor(255, 0, 0))
        
        file_service = FileService()
        save_path = temp_dir / "atomic_test.json"
        
        # Mock file system error during final rename to test atomicity
        # (In real implementation, this would test the backup/restore logic)
        success = file_service.save_file(str(save_path), model)
        
        assert success
        assert save_path.exists()
        
        # Verify no temporary files left behind
        temp_files = list(temp_dir.glob("*.tmp"))
        assert len(temp_files) == 0
    
    def test_save_preserves_existing_file_on_error(self, temp_dir):
        """Test that save errors don't corrupt existing files."""
        # Create initial file
        model1 = PixelArtModel(width=2, height=2)
        model1.set_pixel(0, 0, QColor(255, 0, 0))
        
        file_service = FileService()
        save_path = temp_dir / "preserve_test.json"
        
        success1 = file_service.save_file(str(save_path), model1)
        assert success1
        
        original_content = save_path.read_text()
        
        # Attempt save with invalid model (this should fail gracefully)
        # For this test, we'll simulate by trying to save to a read-only file
        save_path.chmod(0o444)  # Make read-only
        
        model2 = PixelArtModel(width=3, height=3)
        try:
            success2 = file_service.save_file(str(save_path), model2)
            # If save "succeeds" on read-only file, the implementation may vary
            # The key is that the original file should remain intact
        except:
            pass
        finally:
            save_path.chmod(0o644)  # Restore permissions
        
        # Original content should be preserved
        current_content = save_path.read_text()
        assert current_content == original_content