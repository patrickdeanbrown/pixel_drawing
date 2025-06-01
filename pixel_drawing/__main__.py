"""Entry point for running pixel_drawing as a module.

This allows the application to be run as:
    python -m pixel_drawing
"""

import sys
from PyQt6.QtWidgets import QApplication

from .views import PixelDrawingApp


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