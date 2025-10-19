"""
Network Manager - Handles ESP32 communication via WebSocket/TCP/UDP
"""

import socket
import json
import threading
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from typing import Dict, Any
import time


class NetworkWorker(QObject):
    """Worker thread for network communication"""
    
    data_received = pyqtSignal(dict)
    connection_status_changed = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, host: str, port: int, protocol: str = 'tcp'):
        super().__init__()
        self.host = host
        self.port = port
        self.protocol = protocol.lower()
        self.running = False
        self.socket = None
        self.connected = False
        
    def start(self):
        """Start the network worker"""
        self.running = True
        
        if self.protocol == 'tcp':
            self.run_tcp()
        elif self.protocol == 'udp':
            self.run_udp()
        else:
            self.error_occurred.emit(f"Unsupported protocol: {self.protocol}")
            
    def stop(self):
        """Stop the network worker"""
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.connected = False
        self.connection_status_changed.emit({'connected': False})
        
    def run_tcp(self):
        """Run TCP client"""
        while self.running:
            try:
                # Create socket
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.settimeout(5.0)
                
                # Connect
                self.socket.connect((self.host, self.port))
                self.connected = True
                self.connection_status_changed.emit({
                    'connected': True,
                    'protocol': 'TCP',
                    'host': self.host,
                    'port': self.port
                })
                
                # Receive data loop
                buffer = b''
                while self.running and self.connected:
                    try:
                        data = self.socket.recv(4096)
                        if not data:
                            break
                            
                        buffer += data
                        
                        # Process complete JSON messages (assuming newline delimited)
                        while b'\n' in buffer:
                            line, buffer = buffer.split(b'\n', 1)
                            try:
                                message = json.loads(line.decode('utf-8'))
                                self.data_received.emit(message)
                            except json.JSONDecodeError:
                                pass
                                
                    except socket.timeout:
                        continue
                    except Exception as e:
                        self.error_occurred.emit(f"Receive error: {e}")
                        break
                        
            except Exception as e:
                self.error_occurred.emit(f"Connection error: {e}")
                self.connected = False
                self.connection_status_changed.emit({'connected': False})
                
            finally:
                if self.socket:
                    self.socket.close()
                    
            # Wait before reconnecting
            if self.running:
                time.sleep(5)
                
    def run_udp(self):
        """Run UDP client"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.bind(('0.0.0.0', self.port))
            self.socket.settimeout(1.0)
            
            self.connected = True
            self.connection_status_changed.emit({
                'connected': True,
                'protocol': 'UDP',
                'port': self.port
            })
            
            while self.running:
                try:
                    data, addr = self.socket.recvfrom(4096)
                    try:
                        message = json.loads(data.decode('utf-8'))
                        self.data_received.emit(message)
                    except json.JSONDecodeError:
                        pass
                except socket.timeout:
                    continue
                except Exception as e:
                    self.error_occurred.emit(f"Receive error: {e}")
                    
        except Exception as e:
            self.error_occurred.emit(f"UDP setup error: {e}")
        finally:
            if self.socket:
                self.socket.close()
            self.connected = False
            self.connection_status_changed.emit({'connected': False})
            
    def send_data(self, data: dict):
        """Send data to ESP32"""
        if not self.connected or not self.socket:
            return False
            
        try:
            message = json.dumps(data) + '\n'
            self.socket.send(message.encode('utf-8'))
            return True
        except Exception as e:
            self.error_occurred.emit(f"Send error: {e}")
            return False


class NetworkManager(QObject):
    """Main network manager for ESP32 communication"""
    
    def __init__(self, event_bus, config_manager, logger):
        super().__init__()
        self.event_bus = event_bus
        self.config_manager = config_manager
        self.logger = logger
        
        self.worker = None
        self.worker_thread = None
        
        self.setup_worker()
        
    def setup_worker(self):
        """Setup network worker thread"""
        # Get configuration
        host = self.config_manager.get('network.esp32_ip', '192.168.1.100')
        port = self.config_manager.get('network.port', 8080)
        protocol = self.config_manager.get('network.protocol', 'tcp')
        
        # Create worker
        self.worker = NetworkWorker(host, port, protocol)
        
        # Create thread
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)
        
        # Connect signals
        self.worker.data_received.connect(self.on_data_received)
        self.worker.connection_status_changed.connect(self.on_connection_status_changed)
        self.worker.error_occurred.connect(self.on_error)
        
        # Start on thread start
        self.worker_thread.started.connect(self.worker.start)
        
    def start(self):
        """Start network connection"""
        self.logger.info("Starting network manager...")
        self.worker_thread.start()
        
    def stop(self):
        """Stop network connection"""
        self.logger.info("Stopping network manager...")
        if self.worker:
            self.worker.stop()
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()
            
    def send_command(self, command: str, params: dict = None):
        """Send command to ESP32"""
        data = {
            'command': command,
            'params': params or {},
            'timestamp': time.time()
        }
        if self.worker:
            self.worker.send_data(data)
            
    def on_data_received(self, data: dict):
        """Handle received data from ESP32"""
        # Route data to appropriate event topics
        sensor_type = data.get('type', '')
        
        if sensor_type == 'gas':
            self.event_bus.publish('sensor.gas', data)
        elif sensor_type == 'gps':
            self.event_bus.publish('sensor.gps', data)
        elif sensor_type == 'temperature':
            self.event_bus.publish('sensor.temperature', data)
        elif sensor_type == 'humidity':
            self.event_bus.publish('sensor.humidity', data)
        elif sensor_type == 'accelerometer':
            self.event_bus.publish('sensor.accelerometer', data)
        elif sensor_type == 'gyroscope':
            self.event_bus.publish('sensor.gyroscope', data)
        elif sensor_type == 'combined':
            # Handle combined sensor data packet
            for key, value in data.get('sensors', {}).items():
                self