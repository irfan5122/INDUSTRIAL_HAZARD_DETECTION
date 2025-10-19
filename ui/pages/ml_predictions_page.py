"""
ML Predictions Page - Fall detection and prediction visualization
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QPushButton, QCheckBox, QGroupBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
import pyqtgraph as pg
import numpy as np
from collections import deque


class PredictionCard(QFrame):
    """Card showing current prediction status"""
    
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 2px solid #3d3d3d;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Fall Detection Status")
        title.setStyleSheet("color: #00bcd4; font-size: 14pt; font-weight: bold; border: none;")
        layout.addWidget(title)
        
        # Status
        self.status_label = QLabel("NORMAL")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            color: #00e676;
            font-size: 36pt;
            font-weight: bold;
            border: none;
        """)
        layout.addWidget(self.status_label)
        
        # Confidence
        confidence_layout = QHBoxLayout()
        conf_label = QLabel("Confidence:")
        conf_label.setStyleSheet("color: #888888; font-size: 11pt; border: none;")
        self.confidence_value = QLabel("98.5%")
        self.confidence_value.setStyleSheet("color: #e0e0e0; font-size: 11pt; font-weight: bold; border: none;")
        confidence_layout.addWidget(conf_label)
        confidence_layout.addWidget(self.confidence_value)
        confidence_layout.addStretch()
        layout.addLayout(confidence_layout)
        
        # Last prediction time
        time_layout = QHBoxLayout()
        time_label = QLabel("Last Update:")
        time_label.setStyleSheet("color: #888888; font-size: 10pt; border: none;")
        self.time_value = QLabel("00:00:00")
        self.time_value.setStyleSheet("color: #e0e0e0; font-size: 10pt; border: none;")
        time_layout.addWidget(time_label)
        time_layout.addWidget(self.time_value)
        time_layout.addStretch()
        layout.addLayout(time_layout)
        
    def update_prediction(self, is_fall: bool, confidence: float, timestamp: str):
        """Update prediction display"""
        if is_fall:
            self.status_label.setText("⚠️ FALL DETECTED")
            self.status_label.setStyleSheet("""
                color: #ff5252;
                font-size: 32pt;
                font-weight: bold;
                border: none;
            """)
        else:
            self.status_label.setText("✓ NORMAL")
            self.status_label.setStyleSheet("""
                color: #00e676;
                font-size: 36pt;
                font-weight: bold;
                border: none;
            """)
            
        self.confidence_value.setText(f"{confidence:.1f}%")
        self.time_value.setText(timestamp)


class MLPredictionsPage(QWidget):
    """ML Predictions page with fall detection visualization"""
    
    def __init__(self, event_bus, config_manager, logger):
        super().__init__()
        self.event_bus = event_bus
        self.config_manager = config_manager
        self.logger = logger
        
        # Data buffers
        self.accel_x = deque(maxlen=200)
        self.accel_y = deque(maxlen=200)
        self.accel_z = deque(maxlen=200)
        self.gyro_x = deque(maxlen=200)
        self.gyro_y = deque(maxlen=200)
        self.gyro_z = deque(maxlen=200)
        
        self.ml_enabled = True
        
        self.init_ui()
        self.connect_signals()
        self.start_simulation()
        
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Top controls
        controls_layout = QHBoxLayout()
        
        self.ml_toggle = QCheckBox("AI Prediction Enabled")
        self.ml_toggle.setChecked(True)
        self.ml_toggle.setStyleSheet("""
            QCheckBox {
                color: #e0e0e0;
                font-size: 11pt;
                font-weight: bold;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
            QCheckBox::indicator:checked {
                background-color: #00bcd4;
                border: 2px solid #00bcd4;
            }
        """)
        self.ml_toggle.toggled.connect(self.toggle_ml)
        controls_layout.addWidget(self.ml_toggle)
        
        controls_layout.addStretch()
        
        # Model info
        model_label = QLabel("Model: Fall Detection v1.0 | Accuracy: 95.3%")
        model_label.setStyleSheet("color: #888888; font-size: 10pt;")
        controls_layout.addWidget(model_label)
        
        layout.addLayout(controls_layout)
        
        # Prediction card
        self.prediction_card = PredictionCard()
        layout.addWidget(self.prediction_card)
        
        # Accelerometer graphs
        accel_group = QGroupBox("Accelerometer Data (m/s²)")
        accel_group.setStyleSheet("""
            QGroupBox {
                color: #00bcd4;
                font-weight: bold;
                font-size: 11pt;
            }
        """)
        accel_layout = QHBoxLayout(accel_group)
        
        self.accel_plot = pg.PlotWidget()
        self.accel_plot.setBackground('#1a1a1a')
        self.accel_plot.setLabel('left', 'Acceleration')
        self.accel_plot.setLabel('bottom', 'Time')
        self.accel_plot.showGrid(x=True, y=True, alpha=0.3)
        self.accel_plot.addLegend()
        
        self.accel_x_curve = self.accel_plot.plot(pen=pg.mkPen(color='#ff5252', width=2), name='X')
        self.accel_y_curve = self.accel_plot.plot(pen=pg.mkPen(color='#00e676', width=2), name='Y')
        self.accel_z_curve = self.accel_plot.plot(pen=pg.mkPen(color='#00bcd4', width=2), name='Z')
        
        accel_layout.addWidget(self.accel_plot)
        layout.addWidget(accel_group)
        
        # Gyroscope graphs
        gyro_group = QGroupBox("Gyroscope Data (°/s)")
        gyro_group.setStyleSheet("""
            QGroupBox {
                color: #00bcd4;
                font-weight: bold;
                font-size: 11pt;
            }
        """)
        gyro_layout = QHBoxLayout(gyro_group)
        
        self.gyro_plot = pg.PlotWidget()
        self.gyro_plot.setBackground('#1a1a1a')
        self.gyro_plot.setLabel('left', 'Angular Velocity')
        self.gyro_plot.setLabel('bottom', 'Time')
        self.gyro_plot.showGrid(x=True, y=True, alpha=0.3)
        self.gyro_plot.addLegend()
        
        self.gyro_x_curve = self.gyro_plot.plot(pen=pg.mkPen(color='#ff5252', width=2), name='X')
        self.gyro_y_curve = self.gyro_plot.plot(pen=pg.mkPen(color='#00e676', width=2), name='Y')
        self.gyro_z_curve = self.gyro_plot.plot(pen=pg.mkPen(color='#00bcd4', width=2), name='Z')
        
        gyro_layout.addWidget(self.gyro_plot)
        layout.addWidget(gyro_group)
        
    def connect_signals(self):
        """Connect to event bus"""
        self.event_bus.subscribe('sensor.accelerometer', self.on_accelerometer_data)
        self.event_bus.subscribe('sensor.gyroscope', self.on_gyroscope_data)
        self.event_bus.subscribe('ml.prediction', self.on_ml_prediction)
        
    def start_simulation(self):
        """Start simulation for demo"""
        self.sim_timer = QTimer()
        self.sim_timer.timeout.connect(self.simulate_data)
        self.sim_timer.start(50)
        
    def simulate_data(self):
        """Simulate IMU data"""
        # Simulate normal movement
        t = len(self.accel_x) * 0.05
        
        # Accelerometer
        ax = 0.5 * np.sin(t) + np.random.randn() * 0.1
        ay = 0.3 * np.cos(t * 1.5) + np.random.randn() * 0.1
        az = 9.8 + 0.5 * np.sin(t * 0.5) + np.random.randn() * 0.2
        
        self.accel_x.append(ax)
        self.accel_y.append(ay)
        self.accel_z.append(az)
        
        # Gyroscope
        gx = 10 * np.sin(t * 2) + np.random.randn() * 2
        gy = 8 * np.cos(t * 1.8) + np.random.randn() * 2
        gz = 5 * np.sin(t * 1.2) + np.random.randn() * 1
        
        self.gyro_x.append(gx)
        self.gyro_y.append(gy)
        self.gyro_z.append(gz)
        
        # Update plots
        self.accel_x_curve.setData(list(self.accel_x))
        self.accel_y_curve.setData(list(self.accel_y))
        self.accel_z_curve.setData(list(self.accel_z))
        
        self.gyro_x_curve.setData(list(self.gyro_x))
        self.gyro_y_curve.setData(list(self.gyro_y))
        self.gyro_z_curve.setData(list(self.gyro_z))
        
        # Simulate ML prediction (detect abnormal patterns)
        if self.ml_enabled and len(self.accel_x) > 50:
            # Simple fall detection: sudden change in Z acceleration
            recent_z = list(self.accel_z)[-10:]
            z_variance = np.var(recent_z)
            
            is_fall = z_variance > 5.0  # Threshold for fall
            confidence = min(z_variance * 10, 99.9) if is_fall else 98.5
            
            from datetime import datetime
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            self.prediction_card.update_prediction(is_fall, confidence, timestamp)
            
            if is_fall:
                self.event_bus.publish('alert.fall_detected', {
                    'confidence': confidence,
                    'timestamp': timestamp
                })
        
    def toggle_ml(self, enabled: bool):
        """Toggle ML prediction"""
        self.ml_enabled = enabled
        self.logger.info(f"ML prediction {'enabled' if enabled else 'disabled'}")
        
    def on_accelerometer_data(self, data):
        """Handle accelerometer data"""
        self.accel_x.append(data.get('x', 0))
        self.accel_y.append(data.get('y', 0))
        self.accel_z.append(data.get('z', 0))
        
    def on_gyroscope_data(self, data):
        """Handle gyroscope data"""
        self.gyro_x.append(data.get('x', 0))
        self.gyro_y.append(data.get('y', 0))
        self.gyro_z.append(data.get('z', 0))
        
    def on_ml_prediction(self, data):
        """Handle ML prediction results"""
        is_fall = data.get('fall_detected', False)
        confidence = data.get('confidence', 0) * 100
        timestamp = data.get('timestamp', '00:00:00')
        
        self.prediction_card.update_prediction(is_fall, confidence, timestamp)