"""
Main Window - Central UI Controller
Manages navigation, page switching, and top-level UI components
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QStackedWidget, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QIcon, QFont

from ui.pages.dashboard_page import DashboardPage
from ui.pages.live_data_page import LiveDataPage
from ui.pages.map_view_page import MapViewPage
from ui.pages.ml_predictions_page import MLPredictionsPage
from ui.pages.logs_page import LogsPage
from ui.pages.settings_page import SettingsPage
from ui.widgets.top_bar import TopBar
from ui.widgets.sidebar import Sidebar


class MainWindow(QMainWindow):
    """Main application window with navigation and page management"""
    
    page_changed = pyqtSignal(str)
    
    def __init__(self, event_bus, config_manager, logger):
        super().__init__()
        
        self.event_bus = event_bus
        self.config_manager = config_manager
        self.logger = logger
        
        self.current_page = "Dashboard"
        
        self.init_ui()
        self.connect_signals()
        self.logger.info("Main window initialized")
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Smart Helmet Dashboard - Industrial IoT Monitoring")
        self.setMinimumSize(1400, 900)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create top bar
        self.top_bar = TopBar(self.event_bus, self.config_manager)
        main_layout.addWidget(self.top_bar)
        
        # Create content area with sidebar and pages
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Create sidebar
        self.sidebar = Sidebar()
        self.sidebar.page_requested.connect(self.switch_page)
        content_layout.addWidget(self.sidebar)
        
        # Create stacked widget for pages
        self.pages = QStackedWidget()
        self.pages.setStyleSheet("QStackedWidget { background-color: #1a1a1a; }")
        content_layout.addWidget(self.pages, 1)
        
        main_layout.addLayout(content_layout)
        
        # Initialize all pages
        self.init_pages()
        
    def init_pages(self):
        """Initialize and add all application pages"""
        # Dashboard Page
        self.dashboard_page = DashboardPage(
            self.event_bus, 
            self.config_manager,
            self.logger
        )
        self.pages.addWidget(self.dashboard_page)
        
        # Live Data Page
        self.live_data_page = LiveDataPage(
            self.event_bus,
            self.config_manager,
            self.logger
        )
        self.pages.addWidget(self.live_data_page)
        
        # Map View Page
        self.map_view_page = MapViewPage(
            self.event_bus,
            self.config_manager,
            self.logger
        )
        self.pages.addWidget(self.map_view_page)
        
        # ML Predictions Page
        self.ml_predictions_page = MLPredictionsPage(
            self.event_bus,
            self.config_manager,
            self.logger
        )
        self.pages.addWidget(self.ml_predictions_page)
        
        # Logs Page
        self.logs_page = LogsPage(
            self.event_bus,
            self.config_manager,
            self.logger
        )
        self.pages.addWidget(self.logs_page)
        
        # Settings Page
        self.settings_page = SettingsPage(
            self.event_bus,
            self.config_manager,
            self.logger
        )
        self.pages.addWidget(self.settings_page)
        
        # Store page mapping
        self.page_map = {
            "Dashboard": 0,
            "Live Data": 1,
            "Map View": 2,
            "ML Predictions": 3,
            "Logs": 4,
            "Settings": 5
        }
        
    def switch_page(self, page_name):
        """Switch to the specified page"""
        if page_name in self.page_map:
            self.pages.setCurrentIndex(self.page_map[page_name])
            self.current_page = page_name
            self.page_changed.emit(page_name)
            self.logger.info(f"Switched to {page_name} page")
            
            # Update top bar title
            self.top_bar.set_current_page(page_name)
            
    def connect_signals(self):
        """Connect event bus signals"""
        # Subscribe to connection status changes
        self.event_bus.subscribe('connection.status_changed', 
                                self.on_connection_status_changed)
        
    def on_connection_status_changed(self, status):
        """Handle connection status changes"""
        self.top_bar.update_connection_status(status)
        
    def closeEvent(self, event):
        """Handle window close event"""
        self.logger.info("Application closing...")
        # Clean up resources, stop threads, etc.
        self.event_bus.publish('app.closing', {})
        event.accept()