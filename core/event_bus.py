"""
Event Bus - Central publish/subscribe system for decoupled communication
Enables extensible, event-driven architecture
"""

from typing import Callable, Dict, List, Any
from collections import defaultdict
from PyQt6.QtCore import QObject, pyqtSignal
import threading


class EventBus(QObject):
    """
    Thread-safe event bus for application-wide communication
    
    Events are organized by topic (e.g., 'sensor.data', 'connection.status')
    Multiple subscribers can listen to the same topic
    """
    
    # Qt signal for thread-safe GUI updates
    event_signal = pyqtSignal(str, object)
    
    def __init__(self):
        super().__init__()
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._lock = threading.RLock()
        
        # Connect Qt signal to internal handler
        self.event_signal.connect(self._qt_event_handler)
        
    def subscribe(self, topic: str, callback: Callable):
        """
        Subscribe to a topic
        
        Args:
            topic: Event topic (e.g., 'sensor.gas', 'ml.prediction')
            callback: Function to call when event is published
        """
        with self._lock:
            if callback not in self._subscribers[topic]:
                self._subscribers[topic].append(callback)
                
    def unsubscribe(self, topic: str, callback: Callable):
        """
        Unsubscribe from a topic
        
        Args:
            topic: Event topic
            callback: Previously subscribed callback
        """
        with self._lock:
            if callback in self._subscribers[topic]:
                self._subscribers[topic].remove(callback)
                
    def publish(self, topic: str, data: Any = None, use_qt_signal: bool = True):
        """
        Publish an event to all subscribers
        
        Args:
            topic: Event topic
            data: Event data (any type)
            use_qt_signal: If True, use Qt signal for thread safety
        """
        if use_qt_signal:
            # Use Qt signal for GUI thread safety
            self.event_signal.emit(topic, data)
        else:
            # Direct call (use only if already in main thread)
            self._notify_subscribers(topic, data)
            
    def _qt_event_handler(self, topic: str, data: Any):
        """Internal handler for Qt signal"""
        self._notify_subscribers(topic, data)
        
    def _notify_subscribers(self, topic: str, data: Any):
        """Notify all subscribers of an event"""
        with self._lock:
            callbacks = self._subscribers.get(topic, []).copy()
            
        for callback in callbacks:
            try:
                callback(data)
            except Exception as e:
                print(f"Error in event handler for '{topic}': {e}")
                
    def clear_topic(self, topic: str):
        """Remove all subscribers from a topic"""
        with self._lock:
            self._subscribers.pop(topic, None)
            
    def clear_all(self):
        """Remove all subscribers from all topics"""
        with self._lock:
            self._subscribers.clear()
            
    def get_topics(self) -> List[str]:
        """Get list of all subscribed topics"""
        with self._lock:
            return list(self._subscribers.keys())
            
    def get_subscriber_count(self, topic: str) -> int:
        """Get number of subscribers for a topic"""
        with self._lock:
            return len(self._subscribers.get(topic, []))


# Standard event topics used throughout the application
class EventTopics:
    """Standard event topic constants"""
    
    # Connection events
    CONNECTION_STATUS = 'connection.status_changed'
    CONNECTION_ERROR = 'connection.error'
    DATA_RECEIVED = 'connection.data_received'
    
    # Sensor events
    SENSOR_GAS = 'sensor.gas'
    SENSOR_GPS = 'sensor.gps'
    SENSOR_TEMPERATURE = 'sensor.temperature'
    SENSOR_HUMIDITY = 'sensor.humidity'
    SENSOR_ACCELEROMETER = 'sensor.accelerometer'
    SENSOR_GYROSCOPE = 'sensor.gyroscope'
    
    # ML events
    ML_PREDICTION = 'ml.prediction'
    ML_MODEL_LOADED = 'ml.model_loaded'
    ML_TRAINING_STARTED = 'ml.training_started'
    ML_TRAINING_COMPLETED = 'ml.training_completed'
    
    # Alert events
    ALERT_HAZARD = 'alert.hazard'
    ALERT_FALL_DETECTED = 'alert.fall_detected'
    ALERT_GAS_THRESHOLD = 'alert.gas_threshold'
    
    # Application events
    APP_CLOSING = 'app.closing'
    APP_CONFIG_CHANGED = 'app.config_changed'
    APP_THEME_CHANGED = 'app.theme_changed'
    
    # Log events
    LOG_ENTRY = 'log.entry'
    LOG_EXPORT_REQUESTED = 'log.export_requested'