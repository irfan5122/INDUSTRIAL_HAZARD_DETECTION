from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QPushButton, QLineEdit, QComboBox, QSpinBox,
    QCheckBox, QGroupBox, QTextEdit, QHeaderView, QFrame
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWebEngineWidgets import QWebEngineView
from datetime import datetime
import json


class MapViewPage(QWidget):
    """Map view page showing GPS location"""
    
    def __init__(self, event_bus, config_manager, logger):
        super().__init__()
        self.event_bus = event_bus
        self.config_manager = config_manager
        self.logger = logger
        
        self.current_lat = 0.0
        self.current_lon = 0.0
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title and coordinates
        header_layout = QHBoxLayout()
        
        title = QLabel("GPS Location Tracking")
        title.setStyleSheet("color: #00bcd4; font-size: 16pt; font-weight: bold;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        self.coords_label = QLabel("Lat: 0.00000°, Lon: 0.00000°")
        self.coords_label.setStyleSheet("color: #e0e0e0; font-size: 11pt;")
        header_layout.addWidget(self.coords_label)
        
        layout.addLayout(header_layout)
        
        # Map placeholder (would use QWebEngineView for real map)
        map_frame = QFrame()
        map_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 2px solid #3d3d3d;
                border-radius: 10px;
            }
        """)
        map_layout = QVBoxLayout(map_frame)
        
        map_placeholder = QLabel("🗺️\n\nMap View\n(OpenStreetMap / Google Maps Integration)")
        map_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        map_placeholder.setStyleSheet("""
            color: #888888;
            font-size: 24pt;
            border: none;
        """)
        map_layout.addWidget(map_placeholder)
        
        # Info text
        info_label = QLabel(
            "GPS coordinates from helmet will be displayed here.\n"
            "Integration with folium or web map APIs required."
        )
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("color: #666666; font-size: 10pt; border: none;")
        map_layout.addWidget(info_label)
        
        layout.addWidget(map_frame)
        
        # Hazard markers list
        markers_group = QGroupBox("Recent Hazard Events")
        markers_layout = QVBoxLayout(markers_group)
        
        self.markers_list = QTextEdit()
        self.markers_list.setReadOnly(True)
        self.markers_list.setMaximumHeight(150)
        self.markers_list.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                color: #e0e0e0;
                border: 1px solid #3d3d3d;
            }
        """)
        markers_layout.addWidget(self.markers_list)
        
        layout.addWidget(markers_group)
        
        # Connect signals
        self.event_bus.subscribe('sensor.gps', self.on_gps_data)
        self.event_bus.subscribe('alert.hazard', self.on_hazard_alert)
        
    def on_gps_data(self, data):
        """Handle GPS data updates"""
        self.current_lat = data.get('latitude', 0.0)
        self.current_lon = data.get('longitude', 0.0)
        self.coords_label.setText(f"Lat: {self.current_lat:.5f}°, Lon: {self.current_lon:.5f}°")
        
    def on_hazard_alert(self, data):
        """Add hazard event to markers list"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        event_type = data.get('type', 'Unknown')
        message = f"[{timestamp}] {event_type} at ({self.current_lat:.5f}, {self.current_lon:.5f})\n"
        self.markers_list.append(message)