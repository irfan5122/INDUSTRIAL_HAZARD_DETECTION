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

class LogsPage(QWidget):
    """Logs and reports page"""
    
    def __init__(self, event_bus, config_manager, logger):
        super().__init__()
        self.event_bus = event_bus
        self.config_manager = config_manager
        self.logger = logger
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("System Logs & Reports")
        title.setStyleSheet("color: #00bcd4; font-size: 16pt; font-weight: bold;")
        layout.addWidget(title)
        
        # Log viewer
        self.log_viewer = QTextEdit()
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setStyleSheet("""
            QTextEdit {
                background-color: #0d0d0d;
                color: #00ff00;
                font-family: 'Courier New', monospace;
                font-size: 10pt;
                border: 2px solid #3d3d3d;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.log_viewer)
        
        # Export controls
        export_layout = QHBoxLayout()
        
        export_layout.addWidget(QLabel("Export Format:"))
        
        format_combo = QComboBox()
        format_combo.addItems(["CSV", "Excel", "PDF", "JSON"])
        export_layout.addWidget(format_combo)
        
        date_from = QLineEdit("2025-01-01")
        date_from.setPlaceholderText("Date From")
        export_layout.addWidget(date_from)
        
        date_to = QLineEdit("2025-12-31")
        date_to.setPlaceholderText("Date To")
        export_layout.addWidget(date_to)
        
        export_layout.addStretch()
        
        export_btn = QPushButton("Export Logs")
        export_btn.clicked.connect(self.export_logs)
        export_layout.addWidget(export_btn)
        
        clear_btn = QPushButton("Clear Logs")
        clear_btn.clicked.connect(self.clear_logs)
        export_layout.addWidget(clear_btn)
        
        layout.addLayout(export_layout)
        
        # Subscribe to log events
        self.event_bus.subscribe('log.entry', self.add_log_entry)
        
        # Add initial message
        self.add_log_entry("System initialized - Smart Helmet Dashboard v1.0.0")
        
    def add_log_entry(self, message):
        """Add log entry"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] {message}"
        self.log_viewer.append(log_line)
        
    def export_logs(self):
        """Export logs"""
        self.logger.info("Log export initiated")
        self.add_log_entry("Export requested by user")
        
    def clear_logs(self):
        """Clear log viewer"""
        self.log_viewer.clear()
        self.add_log_entry("Logs cleared")