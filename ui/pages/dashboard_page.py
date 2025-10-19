"""
Dashboard Page - Main overview with real-time gauges and status
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
    QLabel, QFrame, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPainter, QColor, QPen
import pyqtgraph as pg
import numpy as np
from collections import deque


class GaugeWidget(QWidget):
    """Circular gauge widget for sensor display"""
    
    def __init__(self, title: str, unit: str, min_val: float = 0, max_val: float = 100):
        super().__init__()
        self.title = title
        self.unit = unit
        self.min_val = min_val
        self.max_val = max_val
        self.current_value = 0
        self.warning_threshold = max_val * 0.7
        self.danger_threshold = max_val * 0.9
        
        self.setMinimumSize(200, 200)
        
    def set_value(self, value: float):
        """Set gauge value and trigger repaint"""
        self.current_value = max(self.min_val, min(self.max_val, value))
        self.update()
        
    def set_thresholds(self, warning: float, danger: float):
        """Set warning and danger thresholds"""
        self.warning_threshold = warning
        self.danger_threshold = danger
        
    def paintEvent(self, event):
        """Draw the gauge"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        side = min(width, height)
        
        painter.translate(width / 2, height / 2)
        painter.scale(side / 200.0, side / 200.0)
        
        # Draw background circle
        painter.setPen(QPen(QColor("#2d2d2d"), 12))
        painter.drawArc(-80, -80, 160, 160, 0, 360 * 16)
        
        # Calculate value angle (270 degrees total, starting from -225)
        value_ratio = (self.current_value - self.min_val) / (self.max_val - self.min_val)
        value_angle = int(value_ratio * 270 * 16)
        
        # Determine color based on value
        if self.current_value >= self.danger_threshold:
            color = QColor("#ff5252")
        elif self.current_value >= self.warning_threshold:
            color = QColor("#ffa726")
        else:
            color = QColor("#00e676")
            
        # Draw value arc
        painter.setPen(QPen(color, 12, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawArc(-80, -80, 160, 160, 225 * 16, -value_angle)
        
        # Draw title
        painter.setPen(QColor("#e0e0e0"))
        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        painter.drawText(-60, -50, 120, 20, Qt.AlignmentFlag.AlignCenter, self.title)
        
        # Draw value
        painter.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        painter.drawText(-60, -10, 120, 40, Qt.AlignmentFlag.AlignCenter, 
                        f"{self.current_value:.1f}")
        
        # Draw unit
        painter.setFont(QFont("Segoe UI", 9))
        painter.setPen(QColor("#888888"))
        painter.drawText(-60, 30, 120, 20, Qt.AlignmentFlag.AlignCenter, self.unit)


class StatusCard(QFrame):
    """Status card widget"""
    
    def __init__(self, title: str):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 2px solid #3d3d3d;
                border-radius: 10px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #00bcd4; font-size: 14pt; font-weight: bold; border: none;")
        layout.addWidget(title_label)
        
        self.status_label = QLabel("SAFE")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            color: #00e676;
            font-size: 32pt;
            font-weight: bold;
            padding: 20px;
            border: none;
        """)
        layout.addWidget(self.status_label)
        
        self.detail_label = QLabel("All systems operational")
        self.detail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.detail_label.setStyleSheet("color: #888888; font-size: 11pt; border: none;")
        layout.addWidget(self.detail_label)
        
    def update_status(self, status: str, detail: str, color: str):
        """Update status display"""
        self.status_label.setText(status)
        self.status_label.setStyleSheet(f"""
            color: {color};
            font-size: 32pt;
            font-weight: bold;
            padding: 20px;
            border: none;
        """)
        self.detail_label.setText(detail)


class DashboardPage(QWidget):
    """Main dashboard page with real-time sensor visualization"""
    
    def __init__(self, event_bus, config_manager, logger):
        super().__init__()
        self.event_bus = event_bus
        self.config_manager = config_manager
        self.logger = logger
        
        # Data buffers for simulation
        self.gas_buffer = deque(maxlen=100)
        self.temp_buffer = deque(maxlen=100)
        
        self.init_ui()
        self.connect_signals()
        self.start_simulation()
        
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Top row - Status card
        self.status_card = StatusCard("System Status")
        layout.addWidget(self.status_card)
        
        # Middle row - Gauges
        gauges_layout = QHBoxLayout()
        gauges_layout.setSpacing(20)
        
        self.gas_gauge = GaugeWidget("Gas Level", "ppm", 0, 200)
        self.temp_gauge = GaugeWidget("Temperature", "°C", 0, 60)
        self.humidity_gauge = GaugeWidget("Humidity", "%", 0, 100)
        
        gauges_layout.addWidget(self.gas_gauge)
        gauges_layout.addWidget(self.temp_gauge)
        gauges_layout.addWidget(self.humidity_gauge)
        
        layout.addLayout(gauges_layout)
        
        # Bottom row - Time series graphs
        graphs_layout = QHBoxLayout()
        graphs_layout.setSpacing(20)
        
        # Gas concentration graph
        self.gas_plot = pg.PlotWidget(title="Gas Concentration Over Time")
        self.gas_plot.setBackground('#1a1a1a')
        self.gas_plot.setLabel('left', 'Concentration (ppm)')
        self.gas_plot.setLabel('bottom', 'Time (s)')
        self.gas_plot.showGrid(x=True, y=True, alpha=0.3)
        self.gas_curve = self.gas_plot.plot(pen=pg.mkPen(color='#00bcd4', width=2))
        
        # Temperature graph
        self.temp_plot = pg.PlotWidget(title="Temperature Over Time")
        self.temp_plot.setBackground('#1a1a1a')
        self.temp_plot.setLabel('left', 'Temperature (°C)')
        self.temp_plot.setLabel('bottom', 'Time (s)')
        self.temp_plot.showGrid(x=True, y=True, alpha=0.3)
        self.temp_curve = self.temp_plot.plot(pen=pg.mkPen(color='#ffa726', width=2))
        
        graphs_layout.addWidget(self.gas_plot)
        graphs_layout.addWidget(self.temp_plot)
        
        layout.addLayout(graphs_layout)
        
    def connect_signals(self):
        """Connect to event bus"""
        self.event_bus.subscribe('sensor.gas', self.on_gas_data)
        self.event_bus.subscribe('sensor.temperature', self.on_temperature_data)
        self.event_bus.subscribe('sensor.humidity', self.on_humidity_data)
        
    def start_simulation(self):
        """Start simulation timer for demo purposes"""
        self.sim_timer = QTimer()
        self.sim_timer.timeout.connect(self.simulate_data)
        self.sim_timer.start(100)  # Update every 100ms
        
    def simulate_data(self):
        """Simulate sensor data for testing"""
        # Simulate gas sensor
        gas_value = 30 + 20 * np.sin(len(self.gas_buffer) * 0.1) + np.random.randn() * 5
        self.gas_buffer.append(gas_value)
        self.gas_gauge.set_value(gas_value)
        self.gas_curve.setData(list(self.gas_buffer))
        
        # Simulate temperature
        temp_value = 25 + 5 * np.sin(len(self.temp_buffer) * 0.05) + np.random.randn() * 2
        self.temp_buffer.append(temp_value)
        self.temp_gauge.set_value(temp_value)
        self.temp_curve.setData(list(self.temp_buffer))
        
        # Simulate humidity
        humidity_value = 50 + 10 * np.sin(len(self.gas_buffer) * 0.07) + np.random.randn() * 3
        self.humidity_gauge.set_value(humidity_value)
        
        # Update status based on readings
        self.update_system_status(gas_value, temp_value)
        
    def update_system_status(self, gas: float, temp: float):
        """Update system status based on sensor readings"""
        if gas > 100 or temp > 45:
            self.status_card.update_status("HAZARD", "Critical levels detected!", "#ff5252")
        elif gas > 50 or temp > 35:
            self.status_card.update_status("WARNING", "Elevated readings detected", "#ffa726")
        else:
            self.status_card.update_status("SAFE", "All systems operational", "#00e676")
            
    def on_gas_data(self, data):
        """Handle gas sensor data from ESP32"""
        value = data.get('value', 0)
        self.gas_buffer.append(value)
        self.gas_gauge.set_value(value)
        self.gas_curve.setData(list(self.gas_buffer))
        
    def on_temperature_data(self, data):
        """Handle temperature data from ESP32"""
        value = data.get('value', 0)
        self.temp_buffer.append(value)
        self.temp_gauge.set_value(value)
        self.temp_curve.setData(list(self.temp_buffer))
        
    def on_humidity_data(self, data):
        """Handle humidity data from ESP32"""
        value = data.get('value', 0)
        self.humidity_gauge.set_value(value)