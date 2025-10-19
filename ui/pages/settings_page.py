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

class SettingsPage(QWidget):
    """Settings and configuration page"""
    
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
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Application Settings")
        title.setStyleSheet("color: #00bcd4; font-size: 16pt; font-weight: bold;")
        layout.addWidget(title)
        
        # Network settings
        network_group = QGroupBox("Network Configuration")
        network_layout = QVBoxLayout(network_group)
        
        ip_layout = QHBoxLayout()
        ip_layout.addWidget(QLabel("ESP32 IP Address:"))
        self.ip_input = QLineEdit(self.config_manager.get('network.esp32_ip', '192.168.1.100'))
        ip_layout.addWidget(self.ip_input)
        network_layout.addLayout(ip_layout)
        
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("Port:"))
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(self.config_manager.get('network.port', 8080))
        port_layout.addWidget(self.port_input)
        port_layout.addStretch()
        network_layout.addLayout(port_layout)
        
        protocol_layout = QHBoxLayout()
        protocol_layout.addWidget(QLabel("Protocol:"))
        self.protocol_combo = QComboBox()
        self.protocol_combo.addItems(["TCP", "UDP", "WebSocket"])
        protocol_layout.addWidget(self.protocol_combo)
        protocol_layout.addStretch()
        network_layout.addLayout(protocol_layout)
        
        self.auto_reconnect = QCheckBox("Auto Reconnect")
        self.auto_reconnect.setChecked(self.config_manager.get('network.auto_reconnect', True))
        network_layout.addWidget(self.auto_reconnect)
        
        layout.addWidget(network_group)
        
        # Sensor settings
        sensor_group = QGroupBox("Sensor Configuration")
        sensor_layout = QVBoxLayout(sensor_group)
        
        # Gas threshold
        gas_layout = QHBoxLayout()
        gas_layout.addWidget(QLabel("Gas Warning Threshold (ppm):"))
        self.gas_warning = QSpinBox()
        self.gas_warning.setRange(0, 500)
        self.gas_warning.setValue(self.config_manager.get('sensors.gas.warning_threshold', 50))
        gas_layout.addWidget(self.gas_warning)
        gas_layout.addStretch()
        sensor_layout.addLayout(gas_layout)
        
        # Temperature threshold
        temp_layout = QHBoxLayout()
        temp_layout.addWidget(QLabel("Temperature Warning (°C):"))
        self.temp_warning = QSpinBox()
        self.temp_warning.setRange(0, 100)
        self.temp_warning.setValue(self.config_manager.get('sensors.temperature.warning_threshold', 40))
        temp_layout.addWidget(self.temp_warning)
        temp_layout.addStretch()
        sensor_layout.addLayout(temp_layout)
        
        # Sampling rate
        sample_layout = QHBoxLayout()
        sample_layout.addWidget(QLabel("IMU Sampling Rate (Hz):"))
        self.sampling_rate = QSpinBox()
        self.sampling_rate.setRange(10, 1000)
        self.sampling_rate.setValue(self.config_manager.get('sensors.accelerometer.sampling_rate', 100))
        sample_layout.addWidget(self.sampling_rate)
        sample_layout.addStretch()
        sensor_layout.addLayout(sample_layout)
        
        layout.addWidget(sensor_group)
        
        # ML settings
        ml_group = QGroupBox("Machine Learning")
        ml_layout = QVBoxLayout(ml_group)
        
        self.ml_enabled = QCheckBox("Enable Fall Detection")
        self.ml_enabled.setChecked(self.config_manager.get('ml.fall_detection.enabled', True))
        ml_layout.addWidget(self.ml_enabled)
        
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("Detection Threshold:"))
        self.ml_threshold = QSpinBox()
        self.ml_threshold.setRange(0, 100)
        self.ml_threshold.setValue(int(self.config_manager.get('ml.fall_detection.threshold', 0.7) * 100))
        self.ml_threshold.setSuffix("%")
        threshold_layout.addWidget(self.ml_threshold)
        threshold_layout.addStretch()
        ml_layout.addLayout(threshold_layout)
        
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Model Path:"))
        self.model_path = QLineEdit(self.config_manager.get('ml.fall_detection.model_path', 'models/fall_detection.pkl'))
        model_layout.addWidget(self.model_path)
        reload_model_btn = QPushButton("Reload Model")
        reload_model_btn.clicked.connect(self.reload_model)
        model_layout.addWidget(reload_model_btn)
        ml_layout.addLayout(model_layout)
        
        layout.addWidget(ml_group)
        
        # UI settings
        ui_group = QGroupBox("User Interface")
        ui_layout = QVBoxLayout(ui_group)
        
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        ui_layout.addLayout(theme_layout)
        
        self.sound_alerts = QCheckBox("Enable Sound Alerts")
        self.sound_alerts.setChecked(self.config_manager.get('alerts.sound_enabled', True))
        ui_layout.addWidget(self.sound_alerts)
        
        self.notifications = QCheckBox("Enable Desktop Notifications")
        self.notifications.setChecked(self.config_manager.get('alerts.notification_enabled', True))
        ui_layout.addWidget(self.notifications)
        
        layout.addWidget(ui_group)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        save_btn = QPushButton("Save Settings")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #00bcd4;
                color: #0d0d0d;
                font-weight: bold;
                padding: 10px 30px;
            }
            QPushButton:hover {
                background-color: #00e5ff;
            }
        """)
        save_btn.clicked.connect(self.save_settings)
        buttons_layout.addWidget(save_btn)
        
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self.reset_to_defaults)
        buttons_layout.addWidget(reset_btn)
        
        layout.addLayout(buttons_layout)
        
        layout.addStretch()
        
    def save_settings(self):
        """Save all settings"""
        # Network
        self.config_manager.set('network.esp32_ip', self.ip_input.text())
        self.config_manager.set('network.port', self.port_input.value())
        self.config_manager.set('network.protocol', self.protocol_combo.currentText().lower())
        self.config_manager.set('network.auto_reconnect', self.auto_reconnect.isChecked())
        
        # Sensors
        self.config_manager.set('sensors.gas.warning_threshold', self.gas_warning.value())
        self.config_manager.set('sensors.temperature.warning_threshold', self.temp_warning.value())
        self.config_manager.set('sensors.accelerometer.sampling_rate', self.sampling_rate.value())
        
        # ML
        self.config_manager.set('ml.fall_detection.enabled', self.ml_enabled.isChecked())
        self.config_manager.set('ml.fall_detection.threshold', self.ml_threshold.value() / 100.0)
        self.config_manager.set('ml.fall_detection.model_path', self.model_path.text())
        
        # Alerts
        self.config_manager.set('alerts.sound_enabled', self.sound_alerts.isChecked())
        self.config_manager.set('alerts.notification_enabled', self.notifications.isChecked())
        
        self.logger.info("Settings saved successfully")
        self.event_bus.publish('app.config_changed', {})
        
    def reset_to_defaults(self):
        """Reset settings to defaults"""
        self.config_manager.reset_to_defaults()
        self.logger.info("Settings reset to defaults")
        
        # Reload UI with default values
        self.ip_input.setText(self.config_manager.get('network.esp32_ip'))
        self.port_input.setValue(self.config_manager.get('network.port'))
        
    def change_theme(self, theme: str):
        """Change application theme"""
        self.config_manager.set('ui.theme', theme.lower())
        self.event_bus.publish('app.theme_changed', {'theme': theme.lower()})
        self.logger.info(f"Theme changed to {theme}")
        
    def reload_model(self):
        """Reload ML model"""
        self.logger.info("ML model reload requested")
        self.event_bus.publish('ml.model_reload_requested', {})