"""
Remaining UI Pages - Live Data, Map View, Logs, and Settings
"""

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


# ============== LIVE DATA PAGE ==============

class LiveDataPage(QWidget):
    """Live data page showing real-time sensor readings in table format"""
    
    def __init__(self, event_bus, config_manager, logger):
        super().__init__()
        self.event_bus = event_bus
        self.config_manager = config_manager
        self.logger = logger
        
        self.data_log = []
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Live Sensor Data Stream")
        title.setStyleSheet("color: #00bcd4; font-size: 16pt; font-weight: bold;")
        layout.addWidget(title)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Timestamp", "Sensor Type", "Value", "Unit", "Status", "Notes"
        ])
        
        # Style table
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #1a1a1a;
                gridline-color: #3d3d3d;
                color: #e0e0e0;
            }
            QHeaderView::section {
                background-color: #0d0d0d;
                color: #00bcd4;
                font-weight: bold;
                padding: 8px;
                border: 1px solid #3d3d3d;
            }
        """)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.table)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        clear_btn = QPushButton("Clear Log")
        clear_btn.clicked.connect(self.clear_log)
        controls_layout.addWidget(clear_btn)
        
        pause_btn = QPushButton("Pause")
        controls_layout.addWidget(pause_btn)
        
        controls_layout.addStretch()
        
        export_btn = QPushButton("Export CSV")
        export_btn.clicked.connect(self.export_csv)
        controls_layout.addWidget(export_btn)
        
        layout.addLayout(controls_layout)
        
        # Connect signals
        self.event_bus.subscribe('connection.data_received', self.add_data_row)
        
    def add_data_row(self, data):
        """Add new data row to table"""
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sensor_type = data.get('type', 'Unknown')
        value = str(data.get('value', '--'))
        unit = data.get('unit', '')
        status = "OK" if data.get('status') != 'error' else "ERROR"
        notes = data.get('notes', '')
        
        self.table.setItem(row, 0, QTableWidgetItem(timestamp))
        self.table.setItem(row, 1, QTableWidgetItem(sensor_type))
        self.table.setItem(row, 2, QTableWidgetItem(value))
        self.table.setItem(row, 3, QTableWidgetItem(unit))
        self.table.setItem(row, 4, QTableWidgetItem(status))
        self.table.setItem(row, 5, QTableWidgetItem(notes))
        
        # Auto-scroll to bottom
        self.table.scrollToBottom()
        
        # Limit rows
        if self.table.rowCount() > 1000:
            self.table.removeRow(0)
            
    def clear_log(self):
        """Clear all data from table"""
        self.table.setRowCount(0)
        
    def export_csv(self):
        """Export data to CSV"""
        self.logger.info("CSV export requested")
        self.event_bus.publish('log.export_requested', {'format': 'csv'})

