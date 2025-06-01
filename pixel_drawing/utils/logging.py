"""Qt-based logging system for pixel drawing application.

Provides comprehensive logging with file output, category-based filtering,
and customer-safe disable mechanism for production builds.
"""

import os
import sys
import datetime
from pathlib import Path
from typing import Optional, TextIO
from PyQt6.QtCore import QLoggingCategory, qInstallMessageHandler, QtMsgType, QMessageLogContext


class PixelDrawingLogger:
    """Qt-based logging system with file output and configurable categories."""
    
    def __init__(self, log_dir: str = "logs", max_log_files: int = 30):
        """Initialize the logging system.
        
        Args:
            log_dir: Directory to store log files
            max_log_files: Maximum number of log files to keep
        """
        self.log_dir = Path(log_dir)
        self.max_log_files = max_log_files
        self.log_file: Optional[TextIO] = None
        self.enabled = self._check_logging_enabled()
        
        # Create log categories
        self.canvas_category = QLoggingCategory("pixel.canvas")
        self.tools_category = QLoggingCategory("pixel.tools") 
        self.file_category = QLoggingCategory("pixel.file")
        self.perf_category = QLoggingCategory("pixel.performance")
        self.error_category = QLoggingCategory("pixel.error")
        self.ui_category = QLoggingCategory("pixel.ui")
        
        if self.enabled:
            self._setup_logging()
    
    def _check_logging_enabled(self) -> bool:
        """Check if logging is enabled via environment variable.
        
        Returns:
            True if logging should be enabled, False if disabled for customers
        """
        # Check environment variable for customer disable
        env_logging = os.environ.get("PIXEL_DRAWING_LOGGING", "on").lower()
        return env_logging not in ("off", "false", "0", "disabled")
    
    def _setup_logging(self) -> None:
        """Set up the logging system with file output."""
        try:
            # Create logs directory
            self.log_dir.mkdir(exist_ok=True)
            
            # Clean up old log files
            self._cleanup_old_logs()
            
            # Create new log file with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            log_filename = f"pixel_drawing_{timestamp}.log"
            log_path = self.log_dir / log_filename
            
            # Open log file
            self.log_file = open(log_path, 'w', encoding='utf-8')
            
            # Install Qt message handler
            qInstallMessageHandler(self._qt_message_handler)
            
            # Log startup information
            self._log_startup_info()
            
        except Exception as e:
            # If logging setup fails, disable logging to prevent crashes
            print(f"Warning: Failed to setup logging: {e}")
            self.enabled = False
            self.log_file = None
    
    def _cleanup_old_logs(self) -> None:
        """Remove old log files to prevent disk space issues."""
        try:
            log_files = list(self.log_dir.glob("pixel_drawing_*.log"))
            log_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            
            # Remove excess log files
            for old_log in log_files[self.max_log_files:]:
                old_log.unlink()
                
        except Exception as e:
            print(f"Warning: Failed to cleanup old logs: {e}")
    
    def _qt_message_handler(self, msg_type: QtMsgType, context: QMessageLogContext, message: str) -> None:
        """Qt message handler for unified logging.
        
        Args:
            msg_type: Type of Qt message (Debug, Warning, Critical, etc.)
            context: Context information about the message
            message: The actual message text
        """
        if not self.enabled or not self.log_file:
            return
        
        try:
            # Format timestamp
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            
            # Determine log level
            level_map = {
                QtMsgType.QtDebugMsg: "DEBUG",
                QtMsgType.QtInfoMsg: "INFO", 
                QtMsgType.QtWarningMsg: "WARNING",
                QtMsgType.QtCriticalMsg: "ERROR",
                QtMsgType.QtFatalMsg: "FATAL"
            }
            level = level_map.get(msg_type, "UNKNOWN")
            
            # Format category if available
            category = context.category if context.category else "general"
            
            # Format file/line info if available
            location = ""
            if context.file and context.line:
                filename = os.path.basename(context.file)
                location = f" [{filename}:{context.line}]"
            
            # Write formatted log entry
            log_entry = f"[{timestamp}] {level:8} {category:15} {message}{location}\n"
            self.log_file.write(log_entry)
            self.log_file.flush()  # Ensure immediate write
            
        except Exception as e:
            # Prevent logging errors from crashing the application
            print(f"Logging error: {e}")
    
    def _log_startup_info(self) -> None:
        """Log application startup information."""
        if not self.enabled:
            return
            
        startup_info = [
            "=" * 80,
            f"Pixel Drawing Application Started - {datetime.datetime.now()}",
            f"Python: {sys.version}",
            f"Platform: {sys.platform}",
            f"Working Directory: {os.getcwd()}",
            f"Log Directory: {self.log_dir.absolute()}",
            "=" * 80
        ]
        
        for line in startup_info:
            self.log_info("startup", line)
    
    def log_debug(self, category: str, message: str) -> None:
        """Log debug message."""
        if self.enabled:
            qDebug = __import__('PyQt6.QtCore', fromlist=['qDebug']).qDebug
            qDebug(f"[{category}] {message}")
    
    def log_info(self, category: str, message: str) -> None:
        """Log info message."""
        if self.enabled:
            qInfo = __import__('PyQt6.QtCore', fromlist=['qInfo']).qInfo
            qInfo(f"[{category}] {message}")
    
    def log_warning(self, category: str, message: str) -> None:
        """Log warning message."""
        if self.enabled:
            qWarning = __import__('PyQt6.QtCore', fromlist=['qWarning']).qWarning
            qWarning(f"[{category}] {message}")
    
    def log_error(self, category: str, message: str) -> None:
        """Log error message."""
        if self.enabled:
            qCritical = __import__('PyQt6.QtCore', fromlist=['qCritical']).qCritical
            qCritical(f"[{category}] {message}")
    
    def log_performance(self, operation: str, duration_ms: float, details: str = "") -> None:
        """Log performance metrics.
        
        Args:
            operation: Name of the operation being measured
            duration_ms: Duration in milliseconds
            details: Additional details about the operation
        """
        if self.enabled:
            details_str = f" - {details}" if details else ""
            self.log_info("performance", f"{operation}: {duration_ms:.2f}ms{details_str}")
    
    def log_canvas_event(self, event_type: str, details: str) -> None:
        """Log canvas-related events."""
        if self.enabled:
            self.log_debug("canvas", f"{event_type}: {details}")
    
    def log_tool_usage(self, tool_name: str, action: str, coordinates: str = "") -> None:
        """Log tool usage for UX analysis."""
        if self.enabled:
            coord_str = f" at {coordinates}" if coordinates else ""
            self.log_info("tools", f"{tool_name} {action}{coord_str}")
    
    def log_file_operation(self, operation: str, file_path: str, success: bool, duration_ms: float = 0) -> None:
        """Log file operations."""
        if self.enabled:
            status = "SUCCESS" if success else "FAILED"
            duration_str = f" ({duration_ms:.2f}ms)" if duration_ms > 0 else ""
            filename = os.path.basename(file_path)
            self.log_info("file", f"{operation} {filename}: {status}{duration_str}")
    
    def shutdown(self) -> None:
        """Clean shutdown of logging system."""
        if self.enabled and self.log_file:
            self.log_info("startup", "Pixel Drawing Application Shutdown")
            self.log_file.close()
            self.log_file = None


# Global logger instance
_logger: Optional[PixelDrawingLogger] = None


def init_logging() -> None:
    """Initialize the global logging system."""
    global _logger
    _logger = PixelDrawingLogger()


def get_logger() -> Optional[PixelDrawingLogger]:
    """Get the global logger instance."""
    return _logger


def shutdown_logging() -> None:
    """Shutdown the logging system."""
    global _logger
    if _logger:
        _logger.shutdown()
        _logger = None


# Convenience functions for common logging operations
def log_debug(category: str, message: str) -> None:
    """Log debug message via global logger."""
    if _logger:
        _logger.log_debug(category, message)


def log_info(category: str, message: str) -> None:
    """Log info message via global logger."""
    if _logger:
        _logger.log_info(category, message)


def log_warning(category: str, message: str) -> None:
    """Log warning message via global logger."""
    if _logger:
        _logger.log_warning(category, message)


def log_error(category: str, message: str) -> None:
    """Log error message via global logger."""
    if _logger:
        _logger.log_error(category, message)


def log_performance(operation: str, duration_ms: float, details: str = "") -> None:
    """Log performance metrics via global logger."""
    if _logger:
        _logger.log_performance(operation, duration_ms, details)


def log_canvas_event(event_type: str, details: str) -> None:
    """Log canvas events via global logger."""
    if _logger:
        _logger.log_canvas_event(event_type, details)


def log_tool_usage(tool_name: str, action: str, coordinates: str = "") -> None:
    """Log tool usage via global logger."""
    if _logger:
        _logger.log_tool_usage(tool_name, action, coordinates)


def log_file_operation(operation: str, file_path: str, success: bool, duration_ms: float = 0) -> None:
    """Log file operations via global logger."""
    if _logger:
        _logger.log_file_operation(operation, file_path, success, duration_ms)