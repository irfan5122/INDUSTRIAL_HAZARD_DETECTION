# Smart Helmet Dashboard - Project Structure & Setup

## 📁 Project Structure

```
smart_helmet_dashboard/
│
├── main.py                          # Application entry point
│
├── core/                            # Core functionality
│   ├── __init__.py
│   ├── event_bus.py                # Event bus for pub/sub communication
│   ├── config_manager.py           # Configuration management
│   └── logger.py                   # Application logging
│
├── ui/                              # User interface components
│   ├── __init__.py
│   ├── main_window.py              # Main application window
│   │
│   ├── widgets/                    # Reusable UI widgets
│   │   ├── __init__.py
│   │   ├── top_bar.py             # Top navigation bar
│   │   ├── sidebar.py             # Collapsible sidebar
│   │   └── gauge_widget.py        # Custom gauge displays
│   │
│   └── pages/                      # Application pages
│       ├── __init__.py
│       ├── dashboard_page.py      # Main dashboard
│       ├── live_data_page.py      # Live data stream
│       ├── map_view_page.py       # GPS map view
│       ├── ml_predictions_page.py # ML predictions
│       ├── logs_page.py           # Logs and reports
│       └── settings_page.py       # Settings configuration
│
├── network/                         # Network communication
│   ├── __init__.py
│   ├── network_manager.py         # ESP32 communication manager
│   ├── websocket_client.py        # WebSocket client (optional)
│   └── tcp_client.py              # TCP client
│
├── ml/                             # Machine learning modules
│   ├── __init__.py
│   ├── fall_detection.py          # Fall detection model
│   ├── feature_extractor.py       # Feature extraction
│   └── model_trainer.py           # Model training utilities
│
├── data/                           # Data storage
│   ├── logs/                      # Application logs
│   ├── exports/                   # Exported reports
│   └── sensor_data/               # Raw sensor data
│
├── models/                         # ML models
│   └── fall_detection.pkl         # Trained fall detection model
│
├── assets/                         # Static assets
│   ├── styles/                    # QSS stylesheets
│   │   ├── dark.qss
│   │   └── light.qss
│   ├── icons/                     # Application icons
│   └── images/                    # Images and graphics
│
├── tests/                          # Unit tests
│   ├── __init__.py
│   ├── test_event_bus.py
│   ├── test_network.py
│   └── test_ml.py
│
├── config.json                     # Application configuration
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
└── LICENSE                         # License file
```

## 🚀 Installation & Setup

### Prerequisites

- Python 3.9 or higher
- PyQt6
- NumPy
- PyQtGraph
- (Optional) PyQt6-WebEngine for map integration

### Installation Steps

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/smart-helmet-dashboard.git
cd smart-helmet-dashboard
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Create required directories:**
```bash
mkdir -p data/logs data/exports data/sensor_data models assets/styles assets/icons
```

5. **Run the application:**
```bash
python main.py
```

## 📦 Requirements.txt

```
PyQt6>=6.4.0
PyQt6-WebEngine>=6.4.0
pyqtgraph>=0.13.0
numpy>=1.24.0
scikit-learn>=1.2.0
pandas>=2.0.0
folium>=0.14.0
websockets>=11.0
```

## ⚙️ Configuration

The application uses `config.json` for persistent settings. Key configuration options:

### Network Configuration
```json
{
  "network": {
    "esp32_ip": "192.168.1.100",
    "port": 8080,
    "protocol": "tcp",
    "auto_reconnect": true,
    "reconnect_interval": 5
  }
}
```

### Sensor Configuration
```json
{
  "sensors": {
    "gas": {
      "enabled": true,
      "warning_threshold": 50,
      "danger_threshold": 100,
      "unit": "ppm"
    },
    "temperature": {
      "enabled": true,
      "warning_threshold": 40,
      "danger_threshold": 50,
      "unit": "°C"
    }
  }
}
```

### ML Configuration
```json
{
  "ml": {
    "fall_detection": {
      "enabled": true,
      "model_path": "models/fall_detection.pkl",
      "threshold": 0.7,
      "window_size": 50
    }
  }
}
```

## 🔌 ESP32 Communication Protocol

### Data Format (JSON)

The ESP32 should send data in the following JSON format:

#### Single Sensor Reading
```json
{
  "type": "gas",
  "value": 45.3,
  "unit": "ppm",
  "timestamp": 1634567890.123
}
```

#### Combined Sensor Packet
```json
{
  "type": "combined",
  "timestamp": 1634567890.123,
  "sensors": {
    "gas": 45.3,
    "temperature": 28.5,
    "humidity": 65.2,
    "latitude": 37.7749,
    "longitude": -122.4194
  }
}
```

#### IMU Data
```json
{
  "type": "accelerometer",
  "x": 0.5,
  "y": -0.3,
  "z": 9.8,
  "timestamp": 1634567890.123
}
```

```json
{
  "type": "gyroscope",
  "x": 10.5,
  "y": -5.2,
  "z": 2.1,
  "timestamp": 1634567890.123
}
```

## 🎨 Extending the Application

### Adding a New Sensor

1. **Add sensor configuration in `config.json`:**
```json
"sensors": {
  "your_sensor": {
    "enabled": true,
    "threshold": 100,
    "unit": "units"
  }
}
```

2. **Create event topic in `event_bus.py`:**
```python
SENSOR_YOUR_SENSOR = 'sensor.your_sensor'
```

3. **Add widget in dashboard page:**
```python
self.your_gauge = GaugeWidget("Your Sensor", "units", 0, 200)
```

4. **Subscribe to sensor data:**
```python
self.event_bus.subscribe('sensor.your_sensor', self.on_your_sensor_data)
```

### Adding a New Page

1. **Create page class in `ui/pages/your_page.py`:**
```python
class YourPage(QWidget):
    def __init__(self, event_bus, config_manager, logger):
        super().__init__()
        self.init_ui()
```

2. **Add to main window's page map:**
```python
self.your_page = YourPage(self.event_bus, self.config_manager, self.logger)
self.pages.addWidget(self.your_page)
self.page_map["Your Page"] = page_index
```

3. **Add navigation button in sidebar:**
```python
("🔧", "Your Page")
```

### Integrating a New ML Model

1. **Create model class in `ml/`:**
```python
class YourModel:
    def predict(self, features):
        # Your prediction logic
        pass
```

2. **Add model manager:**
```python
class YourModelManager(QObject):
    def __init__(self, event_bus, config_manager, logger):
        # Setup model
        pass
```

3. **Register event topics and subscribe:**
```python
self.event_bus.subscribe('sensor.data', self.process_data)
```

## 🧪 Testing

Run unit tests:
```bash
python -m pytest tests/
```

Run specific test:
```bash
python -m pytest tests/test_event_bus.py
```

## 🔧 Troubleshooting

### Connection Issues
- Verify ESP32 IP address in settings
- Check firewall settings
- Ensure ESP32 and laptop are on same network
- Try different protocols (TCP/UDP/WebSocket)

### Performance Issues
- Reduce sensor sampling rates
- Decrease graph buffer sizes
- Disable unnecessary sensors
- Close other applications

### ML Prediction Errors
- Check model file exists
- Verify feature dimensions match model
- Ensure sufficient data buffer size
- Review threshold settings

## 📝 License

MIT License - See LICENSE file for details

## 👥 Contributors

- Your Name - Initial work

## 🙏 Acknowledgments

- PyQt6 for the excellent GUI framework
- PyQtGraph for real-time plotting
- Industrial IoT community

## 📧 Support

For issues and questions:
- GitHub Issues: https://github.com/yourusername/smart-helmet-dashboard/issues
- Email: support@example.com
