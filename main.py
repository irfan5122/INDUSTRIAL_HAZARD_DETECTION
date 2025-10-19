"""
Smart Helmet Dashboard - Industrial IoT Monitoring System
Main Application Entry Point

Architecture:
- MVC pattern with event-driven communication
- Modular plugin-based sensor system
- Real-time data processing with thread safety
- Extensible UI components
"""

import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QSplashScreen
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QFont

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from ui.main_window import MainWindow
from core.event_bus import EventBus
from core.config_manager import ConfigManager
from core.logger import AppLogger


class SmartHelmetApp(QApplication):
    """Main application class with initialization logic"""
    
    def __init__(self, argv):
        super().__init__(argv)
        self.setApplicationName("Smart Helmet Dashboard")
        self.setApplicationVersion("1.0.0")
        self.setOrganizationName("Industrial IoT Systems")
        
        # Initialize core components
        self.event_bus = EventBus()
        self.config_manager = ConfigManager()
        self.logger = AppLogger()
        
        # Set application-wide stylesheet
        self.setStyleSheet(self.load_stylesheet())
        
        # Store references for global access
        self.main_window = None
        
    def load_stylesheet(self):
        """Load the application stylesheet"""
        theme = self.config_manager.get('ui.theme', 'dark')
        stylesheet_path = PROJECT_ROOT / 'assets' / 'styles' / f'{theme}.qss'
        
        if stylesheet_path.exists():
            with open(stylesheet_path, 'r') as f:
                return f.read()
        
        # Fallback to embedded dark theme
        return """
            QMainWindow {
                background-color: #1a1a1a;
                color: #e0e0e0;
            }
            
            QWidget {
                background-color: #1a1a1a;
                color: #e0e0e0;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 10pt;
            }
            
            QPushButton {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 8px 16px;
                color: #e0e0e0;
            }
            
            QPushButton:hover {
                background-color: #3d3d3d;
                border-color: #00bcd4;
            }
            
            QPushButton:pressed {
                background-color: #1d1d1d;
            }
            
            QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 6px;
                color: #e0e0e0;
            }
            
            QLineEdit:focus, QTextEdit:focus {
                border-color: #00bcd4;
            }
            
            QLabel {
                background-color: transparent;
                color: #e0e0e0;
            }
            
            QGroupBox {
                border: 1px solid #3d3d3d;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 12px;
                font-weight: bold;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            
            QTabWidget::pane {
                border: 1px solid #3d3d3d;
                background-color: #1a1a1a;
            }
            
            QTabBar::tab {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                padding: 8px 16px;
                margin-right: 2px;
            }
            
            QTabBar::tab:selected {
                background-color: #00bcd4;
                color: #1a1a1a;
            }
            
            QScrollBar:vertical {
                background-color: #2d2d2d;
                width: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #00bcd4;
                border-radius: 6px;
                min-height: 20px;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            
            QTableWidget {
                background-color: #2d2d2d;
                gridline-color: #3d3d3d;
                border: 1px solid #3d3d3d;
            }
            
            QHeaderView::section {
                background-color: #1a1a1a;
                color: #00bcd4;
                padding: 6px;
                border: 1px solid #3d3d3d;
                font-weight: bold;
            }
            
            QTableWidget::item:selected {
                background-color: #00bcd4;
                color: #1a1a1a;
            }
        """
    
    def show_splash(self):
        """Show splash screen during initialization"""
        splash_pix = QPixmap(400, 300)
        splash_pix.fill(Qt.GlobalColor.transparent)
        
        splash = QSplashScreen(splash_pix, Qt.WindowType.WindowStaysOnTopHint)
        splash.setStyleSheet("""
            QSplashScreen {
                background-color: #1a1a1a;
                border: 2px solid #00bcd4;
                border-radius: 10px;
            }
        """)
        
        splash.showMessage(
            "Smart Helmet Dashboard\nInitializing...",
            Qt.AlignmentFlag.AlignCenter,
            Qt.GlobalColor.white
        )
        splash.show()
        self.processEvents()
        
        return splash
    
    def initialize_main_window(self):
        """Initialize and show the main application window"""
        self.main_window = MainWindow(
            self.event_bus,
            self.config_manager,
            self.logger
        )
        self.main_window.show()


def main():
    """Application entry point"""
    # Create application instance
    app = SmartHelmetApp(sys.argv)
    
    # Show splash screen
    splash = app.show_splash()
    
    # Simulate initialization delay (replace with actual loading tasks)
    QTimer.singleShot(2000, lambda: finish_loading(app, splash))
    
    # Start event loop
    sys.exit(app.exec())


def finish_loading(app, splash):
    """Complete initialization and show main window"""
    app.initialize_main_window()
    splash.finish(app.main_window)


if __name__ == '__main__':
    main()
