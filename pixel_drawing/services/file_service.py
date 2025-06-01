"""
File service module for handling file I/O operations in the pixel art application.

This module provides the FileService class which handles all file operations
including loading, saving, and exporting pixel art projects. It supports
JSON project files and PNG export functionality with proper error handling
and atomic file operations.
"""

import json
import os
from typing import Dict, Any

from PIL import Image
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QColor

from ..models.pixel_art_model import PixelArtModel
from ..validators import validate_file_path
from ..exceptions import FileOperationError, ValidationError


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
        try:
            # Validate file path
            validate_file_path(file_path, "read")
            
            # Load and validate JSON data
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Load data into model
            model.load_from_dict(data)
            model.set_current_file(file_path)
            
            self.file_loaded.emit(file_path)
            return True
            
        except (FileOperationError, ValidationError, json.JSONDecodeError) as e:
            self.operation_failed.emit("load", str(e))
            return False
        except Exception as e:
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
        try:
            # Ensure .json extension
            if not file_path.lower().endswith('.json'):
                file_path += '.json'
            
            # Validate file path for writing
            validate_file_path(file_path, "write")
            
            # Get data from model
            data = model.to_dict()
            
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
                
                model.set_current_file(file_path)
                self.file_saved.emit(file_path)
                return True
                
            finally:
                # Clean up temp file if it still exists
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    
        except (FileOperationError, ValidationError) as e:
            self.operation_failed.emit("save", str(e))
            return False
        except Exception as e:
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
        try:
            # Validate file path for writing
            validate_file_path(file_path, "write")
            
            # Ensure .png extension
            if not file_path.lower().endswith('.png'):
                file_path += '.png'
            
            # Create PIL image
            img = Image.new("RGB", (model.width, model.height), "white")
            
            # Set pixels
            for x in range(model.width):
                for y in range(model.height):
                    color = model.get_pixel(x, y)
                    rgb = color.getRgb()[:3]  # Get RGB values
                    img.putpixel((x, y), rgb)
            
            # Save image
            img.save(file_path, "PNG", optimize=True)
            
            self.file_exported.emit(file_path)
            return True
            
        except (FileOperationError, ValidationError) as e:
            self.operation_failed.emit("export", str(e))
            return False
        except Exception as e:
            self.operation_failed.emit("export", f"Failed to export PNG: {str(e)}")
            return False