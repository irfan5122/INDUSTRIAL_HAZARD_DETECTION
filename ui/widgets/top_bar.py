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
        connection_layout = QHBoxLayout