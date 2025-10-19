"""
Top Bar Widget - Application header with status indicators
"""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PyQt6.QtCore import Qt, QTimer, QDateTime
from PyQt6.QtGui import QFont
from datetime import datetime


class TopBar(QWidget):
    """Top bar with app info, connection status, and controls"""
    
    def __init__(self, event_bus, config_manager):
        super().__init__()
        self.event_bus = event_bus
        self.config_manager = config_manager
        
        self.is_connected = False
        self.last_data_time = None
        
        self.init_ui()
        self.setup_timer()
        
    def init_ui(self):
        """Initialize UI components"""
        self.setFixedHeight(60)
        self.setStyleSheet("""
            QWidget {
                background-color: #0d0d0d;
                border-bottom: 2px solid #00bcd4;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        
        # App name and logo
        title_label = QLabel("⚡ Smart Helmet Dashboard")
        title_font = QFont("Segoe UI", 16, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #00bcd4; border: none;")
        layout.addWidget(title_label)
        
        # Current page indicator
        self.page_label = QLabel("| Dashboard")
        page_font = QFont("Segoe UI", 12)
        self.page_label.setFont(page_font)
        self.page_label.setStyleSheet("color: #888888; border: none;")
        layout.addWidget(self.page_label)
        
        layout.addStretch()
        
        # Last data received time
        self.last_data_label = QLabel("Last Update: --:--:--")
        self.last_data_label.setStyleSheet("color: #888888; border: none;")
        layout.addWidget(self.last_data_label)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setStyleSheet("color: #3d3d3d; border: none;")
        layout.addWidget(separator)
        
        # Connection status
        self.connection_frame = QFrame()
        connection_layout = QHBoxLayout(self.connection_frame)
        connection_layout.setContentsMargins(10, 5, 10, 5)
        connection_layout.setSpacing(8)
        
        self.status_indicator = QLabel("●")
        self.status_indicator.setStyleSheet("color: #ff5252; font-size: 20px; border: none;")
        connection_layout.addWidget(self.status_indicator)
        
        self.status_label = QLabel("Disconnected")
        self.status_label.setStyleSheet("color: #ff5252; font-weight: bold; border: none;")
        connection_layout.addWidget(self.status_label)
        
        self.connection_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 1px solid #3d3d3d;
                border-radius: 6px;
            }
        """)
        layout.addWidget(self.connection_frame)
        
        # Settings button
        settings_btn = QPushButton("⚙")
        settings_btn.setFixedSize(40, 40)
        settings_btn.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 20px;
                font-size: 18px;
                color: #00bcd4;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border-color: #00bcd4;
            }
        """)
        settings_btn.clicked.connect(lambda: self.event_bus.publish('ui.navigate', 'Settings'))
        layout.addWidget(settings_btn)
        
    def setup_timer(self):
        """Setup timer for clock updates"""
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_time_display)
        self.clock_timer.start(1000)  # Update every second
        
    def update_time_display(self):
        """Update the last data time display"""
        if self.last_data_time:
            elapsed = (datetime.now() - self.last_data_time).total_seconds()
            if elapsed < 60:
                self.last_data_label.setText(f"Last Update: {int(elapsed)}s ago")
            elif elapsed < 3600:
                self.last_data_label.setText(f"Last Update: {int(elapsed/60)}m ago")
            else:
                self.last_data_label.setText(f"Last Update: {self.last_data_time.strftime('%H:%M:%S')}")
        
    def update_connection_status(self, status: dict):
        """Update connection status display"""
        self.is_connected = status.get('connected', False)
        
        if self.is_connected:
            self.status_indicator.setStyleSheet("color: #00e676; font-size: 20px; border: none;")
            self.status_label.setStyleSheet("color: #00e676; font-weight: bold; border: none;")
            self.status_label.setText("Connected")
            self.last_data_time = datetime.now()
        else:
            self.status_indicator.setStyleSheet("color: #ff5252; font-size: 20px; border: none;")
            self.status_label.setStyleSheet("color: #ff5252; font-weight: bold; border: none;")
            self.status_label.setText("Disconnected")
            
    def set_current_page(self, page_name: str):
        """Update current page indicator"""
        self.page_label.setText(f"| {page_name}")