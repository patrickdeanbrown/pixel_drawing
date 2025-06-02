"""Main application entry point for pixel_drawing package."""

import sys
import atexit
from PyQt6.QtWidgets import QApplication

from .views import PixelDrawingApp
from .utils.logging import init_logging, shutdown_logging, log_info, log_error
from .i18n import TranslationManager
from .styles import initialize_style_manager, apply_modern_theme


def main() -> None:
    """Main entry point for the pixel drawing application.
    
    This function can be called directly or used as a console script
    entry point in setup.py. Includes full initialization with logging,
    error handling, and proper cleanup.
    """
    # Initialize logging system first
    init_logging()
    log_info("startup", "Initializing Pixel Drawing Application")
    
    # Register cleanup handler
    atexit.register(shutdown_logging)
    
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("Pixel Drawing")
        app.setOrganizationName("Pixel Drawing Team")
        
        # Initialize translation system
        translation_manager = TranslationManager.instance()
        translation_manager.initialize(app)
        log_info("startup", "Translation system initialized")
        
        # Initialize modern styling system
        style_manager = initialize_style_manager(app)
        if apply_modern_theme():
            log_info("startup", "Modern theme applied successfully")
        else:
            log_error("startup", "Failed to apply modern theme")
        
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