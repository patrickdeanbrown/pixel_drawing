"""
File service module for handling file I/O operations in the pixel art application.

This module provides the FileService class which handles all file operations
including loading, saving, and exporting pixel art projects. It supports
JSON project files and PNG export functionality with proper error handling
and atomic file operations.
"""

import json
import os
import time
from typing import Dict, Any

from PIL import Image
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QColor

from ..models.pixel_art_model import PixelArtModel
from ..validators import validate_file_path
from ..exceptions import FileOperationError, ValidationError
from ..utils.logging import log_file_operation, log_performance, log_error, log_info


class FileService(QObject):
    """Service class for file I/O operations."""
    
    # Signals for file operations
    file_loaded = pyqtSignal(str)  # file_path
    file_saved = pyqtSignal(str)   # file_path
    file_exported = pyqtSignal(str)  # file_path
    operation_failed = pyqtSignal(str, str)  # operation, error_message
    
    def __init__(self) -> None:
        """Initialize file service."""
        super().__init__()
    
    def load_file(self, file_path: str, model: PixelArtModel) -> bool:
        """Load a pixel art file into the model.
        
        Args:
            file_path: Path to the file to load
            model: PixelArtModel to load data into
            
        Returns:
            True if successful, False otherwise
        """
        start_time = time.time()
        log_info("file", f"Starting load operation: {os.path.basename(file_path)}")
        
        try:
            # Validate file path
            validate_file_path(file_path, "read")
            
            # Load and validate JSON data
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Load data into model
            model.load_from_dict(data)
            model.set_current_file(file_path)
            
            # Log successful operation
            duration_ms = (time.time() - start_time) * 1000
            log_file_operation("LOAD", file_path, True, duration_ms)
            log_performance("file_load", duration_ms, f"Canvas: {data.get('width', 0)}x{data.get('height', 0)}")
            
            self.file_loaded.emit(file_path)
            return True
            
        except (FileOperationError, ValidationError, json.JSONDecodeError) as e:
            duration_ms = (time.time() - start_time) * 1000
            log_file_operation("LOAD", file_path, False, duration_ms)
            log_error("file", f"Load failed: {str(e)}")
            self.operation_failed.emit("load", str(e))
            return False
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_file_operation("LOAD", file_path, False, duration_ms)
            log_error("file", f"Unexpected load error: {str(e)}")
            self.operation_failed.emit("load", f"Unexpected error: {str(e)}")
            return False
    
    def save_file(self, file_path: str, model: PixelArtModel) -> bool:
        """Save model data to a file.
        
        Args:
            file_path: Path to save the file to
            model: PixelArtModel to save data from
            
        Returns:
            True if successful, False otherwise
        """
        start_time = time.time()
        log_info("file", f"Starting save operation: {os.path.basename(file_path)}")
        
        try:
            # Ensure .json extension
            if not file_path.lower().endswith('.json'):
                file_path += '.json'
            
            # Validate file path for writing
            validate_file_path(file_path, "write")
            
            # Get data from model
            data = model.to_dict()
            pixel_count = len(data.get('pixels', {}))
            canvas_size = f"{data.get('width', 0)}x{data.get('height', 0)}"
            
            # Write to temporary file first for safety
            temp_path = file_path + ".tmp"
            try:
                with open(temp_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                # Atomic move from temp to final location
                if os.path.exists(file_path):
                    backup_path = file_path + ".bak"
                    os.rename(file_path, backup_path)
                    try:
                        os.rename(temp_path, file_path)
                        os.remove(backup_path)  # Remove backup on success
                    except Exception:
                        os.rename(backup_path, file_path)  # Restore backup on failure
                        raise
                else:
                    os.rename(temp_path, file_path)
                
                # Log successful operation
                duration_ms = (time.time() - start_time) * 1000
                log_file_operation("SAVE", file_path, True, duration_ms)
                log_performance("file_save", duration_ms, f"Canvas: {canvas_size}, Pixels: {pixel_count}")
                
                model.set_current_file(file_path)
                self.file_saved.emit(file_path)
                return True
                
            finally:
                # Clean up temp file if it still exists
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    
        except (FileOperationError, ValidationError) as e:
            duration_ms = (time.time() - start_time) * 1000
            log_file_operation("SAVE", file_path, False, duration_ms)
            log_error("file", f"Save failed: {str(e)}")
            self.operation_failed.emit("save", str(e))
            return False
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_file_operation("SAVE", file_path, False, duration_ms)
            log_error("file", f"Unexpected save error: {str(e)}")
            self.operation_failed.emit("save", f"Failed to save file: {str(e)}")
            return False
    
    def export_png(self, file_path: str, model: PixelArtModel) -> bool:
        """Export model as PNG image.
        
        Args:
            file_path: Path to save the PNG file
            model: PixelArtModel to export
            
        Returns:
            True if successful, False otherwise
        """
        start_time = time.time()
        canvas_size = f"{model.width}x{model.height}"
        log_info("file", f"Starting PNG export: {os.path.basename(file_path)} ({canvas_size})")
        
        try:
            # Validate file path for writing
            validate_file_path(file_path, "write")
            
            # Ensure .png extension
            if not file_path.lower().endswith('.png'):
                file_path += '.png'
            
            # Create PIL image
            img = Image.new("RGB", (model.width, model.height), "white")
            
            # Count non-default pixels for performance metrics
            pixel_count = 0
            
            # Set pixels
            for x in range(model.width):
                for y in range(model.height):
                    color = model.get_pixel(x, y)
                    rgb = color.getRgb()[:3]  # Get RGB values
                    img.putpixel((x, y), rgb)
                    if rgb != (255, 255, 255):  # Count non-white pixels
                        pixel_count += 1
            
            # Save image
            img.save(file_path, "PNG", optimize=True)
            
            # Log successful operation
            duration_ms = (time.time() - start_time) * 1000
            log_file_operation("EXPORT", file_path, True, duration_ms)
            log_performance("png_export", duration_ms, f"Canvas: {canvas_size}, Pixels: {pixel_count}")
            
            self.file_exported.emit(file_path)
            return True
            
        except (FileOperationError, ValidationError) as e:
            duration_ms = (time.time() - start_time) * 1000
            log_file_operation("EXPORT", file_path, False, duration_ms)
            log_error("file", f"Export failed: {str(e)}")
            self.operation_failed.emit("export", str(e))
            return False
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_file_operation("EXPORT", file_path, False, duration_ms)
            log_error("file", f"Unexpected export error: {str(e)}")
            self.operation_failed.emit("export", f"Failed to export PNG: {str(e)}")
            return False