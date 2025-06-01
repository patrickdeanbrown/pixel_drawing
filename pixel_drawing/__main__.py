"""Entry point for running pixel_drawing as a module.

This allows the application to be run as:
    python -m pixel_drawing
"""

import sys
import atexit
from PyQt6.QtWidgets import QApplication

from .views import PixelDrawingApp
from .utils.logging import init_logging, shutdown_logging, log_info, log_error


def main() -> None:
    """Main entry point for the pixel drawing application."""
    # Initialize logging system first
    init_logging()
    log_info("startup", "Initializing Pixel Drawing Application")
    
    # Register cleanup handler
    atexit.register(shutdown_logging)
    
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("Pixel Drawing")
        app.setOrganizationName("Pixel Drawing Team")
        
        log_info("startup", "Creating main window")
        window = PixelDrawingApp()
        window.show()
        
        log_info("startup", "Application ready - entering main loop")
        sys.exit(app.exec())
        
    except Exception as e:
        log_error("startup", f"Application startup failed: {e}")
        raise
    finally:
        log_info("startup", "Application main loop ended")


if __name__ == "__main__":
    main()