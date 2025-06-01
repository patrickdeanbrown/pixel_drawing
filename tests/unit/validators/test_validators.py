"""
Unit tests for validation functions.

Tests input validation, boundary checking, and error handling
for all validation utilities used throughout the application.
"""

import pytest
import tempfile
import os
from pathlib import Path
from pixel_drawing.validators import validate_canvas_dimensions, validate_file_path
from pixel_drawing.exceptions import ValidationError, FileOperationError
from pixel_drawing.constants import AppConstants


class TestCanvasDimensionValidation:
    """Test canvas dimension validation logic."""
    
    def test_valid_dimensions_succeed(self, valid_canvas_dimensions):
        """Test that valid dimensions pass validation without error."""
        for width, height in valid_canvas_dimensions:
            # Should not raise any exception
            validate_canvas_dimensions(width, height)
    
    def test_invalid_dimensions_raise_error(self, invalid_canvas_dimensions):
        """Test that invalid dimensions raise ValidationError."""
        for width, height in invalid_canvas_dimensions:
            with pytest.raises(ValidationError):
                validate_canvas_dimensions(width, height)
    
    def test_minimum_valid_dimensions(self):
        """Test minimum valid dimensions (1x1)."""
        validate_canvas_dimensions(1, 1)  # Should not raise
    
    def test_maximum_valid_dimensions(self):
        """Test maximum valid dimensions."""
        max_size = AppConstants.MAX_CANVAS_SIZE
        validate_canvas_dimensions(max_size, max_size)  # Should not raise
    
    def test_zero_width_raises_error(self):
        """Test that zero width raises ValidationError."""
        with pytest.raises(ValidationError, match="Canvas dimensions must be at least"):
            validate_canvas_dimensions(0, 10)
    
    def test_zero_height_raises_error(self):
        """Test that zero height raises ValidationError."""
        with pytest.raises(ValidationError, match="Canvas dimensions must be at least"):
            validate_canvas_dimensions(10, 0)
    
    def test_negative_width_raises_error(self):
        """Test that negative width raises ValidationError."""
        with pytest.raises(ValidationError, match="Canvas dimensions must be at least"):
            validate_canvas_dimensions(-5, 10)
    
    def test_negative_height_raises_error(self):
        """Test that negative height raises ValidationError."""
        with pytest.raises(ValidationError, match="Canvas dimensions must be at least"):
            validate_canvas_dimensions(10, -5)
    
    def test_oversized_width_raises_error(self):
        """Test that width above maximum raises ValidationError."""
        max_size = AppConstants.MAX_CANVAS_SIZE
        with pytest.raises(ValidationError, match="Canvas dimensions cannot exceed"):
            validate_canvas_dimensions(max_size + 1, 10)
    
    def test_oversized_height_raises_error(self):
        """Test that height above maximum raises ValidationError."""
        max_size = AppConstants.MAX_CANVAS_SIZE
        with pytest.raises(ValidationError, match="Canvas dimensions cannot exceed"):
            validate_canvas_dimensions(10, max_size + 1)
    
    def test_non_integer_types_conversion(self):
        """Test that non-integer types are properly rejected."""
        # Float values should be rejected (strict type checking)
        with pytest.raises(ValidationError, match="Canvas dimensions must be integers"):
            validate_canvas_dimensions(10.0, 20.0)
        
        # String numbers should not work
        with pytest.raises(ValidationError, match="Canvas dimensions must be integers"):
            validate_canvas_dimensions("10", "20")


class TestFilePathValidation:
    """Test file path validation for different operations."""
    
    def test_valid_existing_file_for_read(self, temp_dir):
        """Test validation of existing file for read operation."""
        # Create a test file
        test_file = temp_dir / "test.json"
        test_file.write_text('{"test": "data"}')
        
        # Should not raise exception
        validate_file_path(str(test_file), "read")
    
    def test_nonexistent_file_for_read_raises_error(self, temp_dir):
        """Test that nonexistent file for read raises FileOperationError."""
        nonexistent_file = temp_dir / "nonexistent.json"
        
        with pytest.raises(FileOperationError, match="File does not exist"):
            validate_file_path(str(nonexistent_file), "read")
    
    def test_valid_directory_for_write(self, temp_dir):
        """Test validation of writable directory for write operation."""
        new_file = temp_dir / "new_file.json"
        
        # Should not raise exception (directory exists and is writable)
        validate_file_path(str(new_file), "write")
    
    def test_nonexistent_directory_for_write_raises_error(self):
        """Test that file in nonexistent directory for write raises FileOperationError."""
        invalid_path = "/nonexistent/directory/file.json"
        
        with pytest.raises(FileOperationError, match="Directory does not exist"):
            validate_file_path(invalid_path, "write")
    
    def test_empty_path_raises_error(self):
        """Test that empty file path raises FileOperationError."""
        with pytest.raises(FileOperationError, match="File path cannot be empty"):
            validate_file_path("", "read")
        
        with pytest.raises(FileOperationError, match="File path cannot be empty"):
            validate_file_path("", "write")
    
    def test_none_path_raises_error(self):
        """Test that None file path raises FileOperationError."""
        with pytest.raises(FileOperationError, match="File path cannot be empty"):
            validate_file_path(None, "read")
    
    def test_directory_instead_of_file_for_read_raises_error(self, temp_dir):
        """Test that directory path for read raises FileOperationError."""
        with pytest.raises(FileOperationError, match="Path is not a file"):
            validate_file_path(str(temp_dir), "read")
    
    def test_invalid_operation_type_ignored(self, temp_dir):
        """Test that invalid operation type is ignored (no validation performed)."""
        test_file = temp_dir / "test.json"
        test_file.write_text('{"test": "data"}')
        
        # Invalid operation types are currently ignored by the validator
        # This test verifies the current behavior (should not raise)
        validate_file_path(str(test_file), "invalid_operation")
    
    def test_readonly_file_for_write_validation(self, temp_dir):
        """Test validation behavior with read-only files."""
        readonly_file = temp_dir / "readonly.json"
        readonly_file.write_text('{"test": "data"}')
        
        # Make file read-only
        readonly_file.chmod(0o444)
        
        try:
            # Should raise FileOperationError for write operation to read-only file
            with pytest.raises(FileOperationError, match="not writable"):
                validate_file_path(str(readonly_file), "write")
        finally:
            # Restore write permissions for cleanup
            readonly_file.chmod(0o644)
    
    def test_special_characters_in_path(self, temp_dir):
        """Test file paths with special characters."""
        # Test various special characters that might be valid in filenames
        special_names = [
            "file with spaces.json",
            "file-with-dashes.json", 
            "file_with_underscores.json",
            "file.with.dots.json"
        ]
        
        for name in special_names:
            test_file = temp_dir / name
            test_file.write_text('{"test": "data"}')
            
            # Should not raise exception
            validate_file_path(str(test_file), "read")
    
    def test_very_long_path_handling(self, temp_dir):
        """Test handling of very long file paths."""
        # Create a reasonably long path (but not exceeding OS limits)
        long_name = "a" * 100 + ".json"
        long_path = temp_dir / long_name
        
        # Should handle long paths gracefully
        validate_file_path(str(long_path), "write")
    
    def test_relative_vs_absolute_paths(self, temp_dir):
        """Test validation of relative vs absolute paths."""
        # Create test file
        test_file = temp_dir / "test.json"
        test_file.write_text('{"test": "data"}')
        
        # Absolute path should work
        validate_file_path(str(test_file), "read")
        
        # Relative path should also work (current working directory context)
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(str(temp_dir))
            validate_file_path("test.json", "read")
        finally:
            os.chdir(original_cwd)


class TestFileExtensionValidation:
    """Test file extension handling in validation."""
    
    def test_json_extension_validation(self, temp_dir):
        """Test validation accepts .json files."""
        json_file = temp_dir / "test.json"
        json_file.write_text('{"test": "data"}')
        
        validate_file_path(str(json_file), "read")
    
    def test_case_insensitive_extension(self, temp_dir):
        """Test that file extension validation is case insensitive."""
        files_to_test = [
            "test.JSON",
            "test.Json", 
            "test.jSoN"
        ]
        
        for filename in files_to_test:
            test_file = temp_dir / filename
            test_file.write_text('{"test": "data"}')
            
            # Should not raise exception regardless of case
            validate_file_path(str(test_file), "read")
    
    def test_missing_extension_handling(self, temp_dir):
        """Test handling of files without extensions."""
        no_ext_file = temp_dir / "test_file"
        no_ext_file.write_text('{"test": "data"}')
        
        # Should still validate for read (extension may not be required)
        validate_file_path(str(no_ext_file), "read")


class TestErrorMessageQuality:
    """Test that validation errors provide helpful messages."""
    
    def test_dimension_error_messages_are_descriptive(self):
        """Test that dimension validation errors provide clear information."""
        # Test minimum dimension error
        try:
            validate_canvas_dimensions(0, 10)
            assert False, "Expected ValidationError"
        except ValidationError as e:
            assert "at least" in str(e).lower()
        
        # Test maximum dimension error
        try:
            validate_canvas_dimensions(1000, 10)
            assert False, "Expected ValidationError"
        except ValidationError as e:
            assert "cannot exceed" in str(e).lower()
    
    def test_file_error_messages_include_path(self, temp_dir):
        """Test that file validation errors include the problematic path."""
        nonexistent_file = temp_dir / "nonexistent.json"
        
        try:
            validate_file_path(str(nonexistent_file), "read")
            assert False, "Expected FileOperationError"
        except FileOperationError as e:
            assert str(nonexistent_file) in str(e)
    
    def test_error_messages_include_valid_ranges(self):
        """Test that dimension errors include information about valid ranges."""
        try:
            validate_canvas_dimensions(1000, 10)  # Exceeds maximum
            assert False, "Expected ValidationError"
        except ValidationError as e:
            error_msg = str(e).lower()
            # Should mention the maximum size
            assert str(AppConstants.MAX_CANVAS_SIZE) in error_msg


class TestEdgeCaseHandling:
    """Test validation behavior with edge cases and boundary conditions."""
    
    def test_boundary_dimensions(self):
        """Test validation at exact boundary values."""
        min_size = AppConstants.MIN_CANVAS_SIZE
        max_size = AppConstants.MAX_CANVAS_SIZE
        
        # Minimum boundaries
        validate_canvas_dimensions(min_size, min_size)  # Should pass
        
        # Maximum boundaries  
        validate_canvas_dimensions(max_size, max_size)  # Should pass
        
        # Just outside boundaries should fail
        with pytest.raises(ValidationError):
            validate_canvas_dimensions(min_size - 1, min_size)
        
        with pytest.raises(ValidationError):
            validate_canvas_dimensions(max_size + 1, max_size)
    
    def test_unicode_file_paths(self, temp_dir):
        """Test file path validation with unicode characters."""
        unicode_file = temp_dir / "test_文件.json"
        unicode_file.write_text('{"test": "data"}')
        
        # Should handle unicode file names
        validate_file_path(str(unicode_file), "read")
    
    def test_concurrent_validation_calls(self):
        """Test that validation functions are thread-safe."""
        import threading
        
        errors = []
        
        def validate_dimensions():
            try:
                for i in range(100):
                    validate_canvas_dimensions(10, 10)
            except Exception as e:
                errors.append(e)
        
        # Run multiple threads
        threads = [threading.Thread(target=validate_dimensions) for _ in range(5)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        # Should not have any errors from concurrent access
        assert len(errors) == 0