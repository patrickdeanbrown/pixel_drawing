#!/usr/bin/env python3
"""
Pixel Drawing - A modern pixel art application for creating retro game assets.
Cross-platform GUI application built with PyQt6 using modular architecture.

This is the main entry point that uses the modular package structure.
"""

import sys
from PyQt6.QtWidgets import QApplication

from pixel_drawing.views import PixelDrawingApp


def main() -> None:
    """Main entry point for the pixel drawing application."""
    app = QApplication(sys.argv)
    app.setApplicationName("Pixel Drawing")
    app.setOrganizationName("Pixel Drawing Team")
    
    window = PixelDrawingApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()