"""Main application entry point for pixel_drawing package."""

import sys
from PyQt6.QtWidgets import QApplication

from .views import PixelDrawingApp


def main() -> None:
    """Main entry point for the pixel drawing application.
    
    This function can be called directly or used as a console script
    entry point in setup.py.
    """
    app = QApplication(sys.argv)
    app.setApplicationName("Pixel Drawing")
    app.setOrganizationName("Pixel Drawing Team")
    
    window = PixelDrawingApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()