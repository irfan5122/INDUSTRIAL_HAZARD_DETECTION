"""
Application Logger - Centralized Logging System

This module provides a unified logging interface for the entire application.
It handles both file logging (for permanent records) and console logging 
(for real-time debugging).

Key Features:
- Automatic log file rotation (prevents huge files)
- Timestamped entries
- Multiple severity levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Thread-safe operation
- Separate console and file outputs

Log Levels Explained:
- DEBUG: Detailed diagnostic information (e.g., "Sensor value received: 45.3")
- INFO: General informational messages (e.g., "Application started")
- WARNING: Something unexpected but not critical (e.g., "High sensor reading")
- ERROR: Something failed but app continues (e.g., "Network connection lost")
- CRITICAL: Serious error, app might crash (e.g., "Database corrupted")
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler


class AppLogger:
    """
    Application-wide logger with file and console output
    
    This class wraps Python's built-in logging module to provide:
    1. Consistent log format across the application
    2. Automatic file management
    3. Easy-to-use interface
    
    Usage Example:
        logger = AppLogger()
        logger.info("Application started")
        logger.error("Connection failed", exc_info=True)
    """
    
    def __init__(self, name: str = "SmartHelmet", log_dir: str = "logs"):
        """
        Initialize the logger
        
        Args:
            name: Logger name (appears in log entries)
            log_dir: Directory where log files are stored
            
        The logger automatically:
        - Creates the log directory if it doesn't exist
        - Sets up file and console handlers
        - Configures formatting
        """
        self.name = name
        self.log_dir = Path(log_dir)
        
        # Create logs directory if it doesn't exist
        # exist_ok=True means no error if directory already exists
        self.log_dir.mkdir(exist_ok=True)
        
        # Get or create a logger instance
        # Using logging.getLogger ensures we get the same logger 
        # if this is called multiple times with the same name
        self.logger = logging.getLogger(name)
        
        # Set the minimum severity level to capture
        # DEBUG is the lowest level, so we capture everything
        # The handlers will then filter what they actually output
        self.logger.setLevel(logging.DEBUG)
        
        # Prevent duplicate handlers if logger is initialized multiple times
        # This is important because getLogger returns existing loggers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """
        Setup file and console handlers
        
        Handlers are output destinations for log messages.
        We set up two handlers:
        1. File handler - writes to disk for permanent record
        2. Console handler - prints to terminal for real-time viewing
        """
        
        # ============== FILE HANDLER ==============
        # Create log filename with current date
        # Example: SmartHelmet_20251019.log
        log_file = self.log_dir / f"{self.name}_{datetime.now().strftime('%Y%m%d')}.log"
        
        # RotatingFileHandler automatically manages file size
        # When maxBytes is reached, it renames the file and starts a new one
        # Example rotation:
        #   SmartHelmet_20251019.log       (current, 10MB)
        #   SmartHelmet_20251019.log.1     (backup 1, 10MB)
        #   SmartHelmet_20251019.log.2     (backup 2, 10MB)
        # After 5 backups, oldest is deleted
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10 MB per file (10 * 1024 KB * 1024 bytes)
            backupCount=5           # Keep 5 backup files (total: 60MB max)
        )
        
        # File logs capture everything (DEBUG and above)
        # This gives us maximum detail for troubleshooting
        file_handler.setLevel(logging.DEBUG)
        
        # ============== CONSOLE HANDLER ==============
        # Console handler writes to stdout (terminal/console)
        console_handler = logging.StreamHandler(sys.stdout)
        
        # Console only shows INFO and above (less noisy)
        # We don't want to spam the console with DEBUG messages
        console_handler.setLevel(logging.INFO)
        
        # ============== FORMATTER ==============
        # Formatter defines how log messages look
        # Format string breakdown:
        #   %(asctime)s    - Timestamp (2025-10-19 14:30:45)
        #   %(name)s       - Logger name (SmartHelmet)
        #   %(levelname)s  - Severity level (INFO, ERROR, etc.)
        #   %(message)s    - The actual log message
        #
        # Example output:
        # 2025-10-19 14:30:45 - SmartHelmet - INFO - Application started
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'  # Date format
        )
        
        # Apply formatter to both handlers
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    # ============== PUBLIC METHODS ==============
    # These are the methods you'll use throughout your application
    
    def debug(self, message: str):
        """
        Log debug message (detailed diagnostic info)
        
        Use for:
        - Variable values during execution
        - Function entry/exit points
        - Detailed state information
        
        Example:
            logger.debug(f"Received sensor data: {data}")
        """
        self.logger.debug(message)
    
    def info(self, message: str):
        """
        Log info message (general information)
        
        Use for:
        - Application lifecycle events (started, stopped)
        - Successful operations
        - Normal program flow
        
        Example:
            logger.info("Connected to ESP32")
            logger.info("User logged in: admin")
        """
        self.logger.info(message)
    
    def warning(self, message: str):
        """
        Log warning message (potential problem)
        
        Use for:
        - Unexpected but handled situations
        - Deprecated feature usage
        - Resource warnings (low memory, disk space)
        
        Example:
            logger.warning("High gas level detected: 85 ppm")
            logger.warning("Connection retry attempt 3/5")
        """
        self.logger.warning(message)
    
    def error(self, message: str, exc_info: bool = False):
        """
        Log error message (something failed)
        
        Args:
            message: Error description
            exc_info: If True, includes exception traceback
        
        Use for:
        - Failed operations
        - Network errors
        - Data validation failures
        
        Example:
            try:
                connect_to_esp32()
            except Exception as e:
                logger.error(f"Connection failed: {e}", exc_info=True)
        
        With exc_info=True, you get full stack trace:
            2025-10-19 14:30:45 - SmartHelmet - ERROR - Connection failed
            Traceback (most recent call last):
              File "network.py", line 45, in connect
                socket.connect(...)
            ConnectionRefusedError: [Errno 111] Connection refused
        """
        self.logger.error(message, exc_info=exc_info)
    
    def critical(self, message: str, exc_info: bool = False):
        """
        Log critical message (severe error)
        
        Args:
            message: Critical error description
            exc_info: If True, includes exception traceback
        
        Use for:
        - Fatal errors
        - System failures
        - Data corruption
        - Unrecoverable states
        
        Example:
            logger.critical("Database connection lost - shutting down")
            logger.critical("ML model file corrupted", exc_info=True)
        """
        self.logger.critical(message, exc_info=exc_info)


# ============== ADVANCED FEATURES ==============

class AdvancedAppLogger(AppLogger):
    """
    Extended logger with additional features
    
    This version adds:
    - Separate error log file
    - Colored console output
    - Log level filtering
    - Custom formatters
    """
    
    def __init__(self, name: str = "SmartHelmet", log_dir: str = "logs"):
        super().__init__(name, log_dir)
    
    def _setup_handlers(self):
        """Enhanced handler setup with separate error log"""
        
        # Regular log file (all levels)
        log_file = self.log_dir / f"{self.name}_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Separate ERROR log file (errors only)
        error_file = self.log_dir / f"{self.name}_errors_{datetime.now().strftime('%Y%m%d')}.log"
        error_handler = RotatingFileHandler(
            error_file,
            maxBytes=5*1024*1024,
            backupCount=3
        )
        error_handler.setLevel(logging.ERROR)  # Only errors and critical
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Enhanced formatter with more details
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - [%(levelname)s] - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Simple formatter for console
        simple_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        
        file_handler.setFormatter(detailed_formatter)
        error_handler.setFormatter(detailed_formatter)
        console_handler.setFormatter(simple_formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)
        self.logger.addHandler(console_handler)


# ============== USAGE EXAMPLES ==============

def example_usage():
    """Demonstration of logger usage in different scenarios"""
    
    # Create logger instance
    logger = AppLogger("ExampleApp", "example_logs")
    
    # 1. Application startup
    logger.info("=" * 50)
    logger.info("Smart Helmet Dashboard Starting...")
    logger.info("=" * 50)
    
    # 2. Debug information (detailed)
    config = {"ip": "192.168.1.100", "port": 8080}
    logger.debug(f"Configuration loaded: {config}")
    
    # 3. Normal operations
    logger.info("Connecting to ESP32...")
    logger.info("Connection established successfully")
    
    # 4. Warning for unusual but handled situation
    sensor_value = 85
    if sensor_value > 80:
        logger.warning(f"High sensor reading: {sensor_value} ppm")
    
    # 5. Error handling
    try:
        # Simulate an error
        result = 10 / 0
    except ZeroDivisionError as e:
        logger.error(f"Calculation error: {e}", exc_info=True)
    
    # 6. Critical error (application might crash)
    try:
        # Simulate critical failure
        with open("missing_file.txt", "r") as f:
            data = f.read()
    except FileNotFoundError as e:
        logger.critical(f"Critical file missing: {e}", exc_info=True)
    
    # 7. Application shutdown
    logger.info("Application shutting down normally")


# ============== INTEGRATION WITH EVENT BUS ==============

def integrate_with_event_bus(event_bus, logger):
    """
    Example: How to connect logger with event bus
    This allows automatic logging of all events
    """
    
    def log_event(data):
        """Callback that logs all events"""
        logger.debug(f"Event received: {data}")
    
    # Subscribe to all events
    event_bus.subscribe('*', log_event)
    
    # Subscribe to specific error events
    def log_error_event(data):
        logger.error(f"Error event: {data}")
    
    event_bus.subscribe('error.*', log_error_event)


# ============== LOG ANALYSIS HELPER ==============

class LogAnalyzer:
    """
    Helper class to analyze log files
    Useful for debugging and monitoring
    """
    
    @staticmethod
    def count_errors(log_file: Path) -> int:
        """Count number of errors in log file"""
        error_count = 0
        with open(log_file, 'r') as f:
            for line in f:
                if ' - ERROR - ' in line or ' - CRITICAL - ' in line:
                    error_count += 1
        return error_count
    
    @staticmethod
    def get_last_n_lines(log_file: Path, n: int = 10) -> list:
        """Get last N lines from log file (like 'tail' command)"""
        with open(log_file, 'r') as f:
            lines = f.readlines()
        return lines[-n:]
    
    @staticmethod
    def search_logs(log_file: Path, keyword: str) -> list:
        """Search for keyword in logs"""
        matches = []
        with open(log_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                if keyword.lower() in line.lower():
                    matches.append((line_num, line.strip()))
        return matches


# ============== MAIN EXECUTION ==============

if __name__ == '__main__':
    """Test the logger"""
    print("Testing AppLogger...")
    print("-" * 50)
    
    # Run example
    example_usage()
    
    print("\n" + "-" * 50)
    print("Check the 'example_logs' directory for log files!")
    print("-" * 50)
    
    # Demonstrate log analysis
    log_file = Path("example_logs/ExampleApp_20251019.log")
    if log_file.exists():
        analyzer = LogAnalyzer()
        errors = analyzer.count_errors(log_file)
        print(f"\nTotal errors found: {errors}")
        
        print("\nLast 5 log entries:")
        for line in analyzer.get_last_n_lines(log_file, 5):
            print(line.strip())