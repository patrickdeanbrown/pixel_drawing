#!/usr/bin/env python3
"""
Setup script for Pixel Drawing application.
"""

from setuptools import setup, find_packages

with open("README.md", "w") as f:
    f.write("""# Pixel Drawing

A cross-platform pixel art application for creating retro game assets.

## Features

- Pixel-by-pixel drawing with brush tool
- Fill bucket for area filling
- Color selector with custom colors
- Save/load project files (JSON format)
- Export to PNG images
- Resizable canvas with aspect ratio preservation
- Cross-platform support (Windows, Linux, macOS)

## Installation

1. Install Python 3.7 or higher
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. For Linux users, you may need to install tkinter:
   ```bash
   sudo apt-get install python3-tk  # Ubuntu/Debian
   sudo yum install tkinter         # CentOS/RHEL
   ```

## Usage

Run the application:
```bash
python pixel_drawing.py
```

## Controls

- **Left Click**: Draw with brush or use fill bucket
- **Drag**: Continuous drawing with brush
- **Tools Panel**: Switch between brush and fill bucket
- **Color Panel**: Choose drawing color
- **Canvas Size**: Resize the drawing canvas
- **File Menu**: New, Open, Save, Export functions

## File Formats

- **Project files**: JSON format containing pixel data and canvas dimensions
- **Export**: PNG images for use in game engines

## Supported Game Engine Formats

The exported PNG files are compatible with:
- Unity
- Godot
- GameMaker Studio
- Construct 3
- Any engine that supports standard PNG images

## License

MIT License
""")

setup(
    name="pixel-drawing",
    version="1.0.0",
    description="A cross-platform pixel art application for creating retro game assets",
    author="Pixel Drawing Team",
    python_requires=">=3.7",
    install_requires=[
        "PyQt6>=6.4.0",
        "Pillow>=9.0.0",
    ],
    py_modules=["pixel_drawing", "pixel_drawing_qt"],
    entry_points={
        "console_scripts": [
            "pixel-drawing=pixel_drawing:main",
            "pixel-drawing-qt=pixel_drawing_qt:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Graphics :: Editors",
        "Topic :: Games/Entertainment",
    ],
)