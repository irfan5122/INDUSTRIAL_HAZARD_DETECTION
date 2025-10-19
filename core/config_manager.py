"""
Configuration Manager - Handles application settings and persistence
"""

import json
from pathlib import Path
from typing import Any, Dict
import threading


class ConfigManager:
    """
    Manages application configuration with file persistence
    Thread-safe access to settings
    """
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self._config: Dict[str, Any] = {}
        self._lock = threading.RLock()
        self._load_config()
        
    def _load_config(self):
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self._config = json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
                self._config = self._get_default_config()
        else:
            self._config = self._get_default_config()
            self._save_config()
            
    def _save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self._config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
            
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration"""
        return {
            'ui': {
                'theme': 'dark',
                'sidebar_collapsed': False,
                'default_page': 'Dashboard'
            },
            'network': {
                'esp32_ip': '192.168.1.100',
                'port': 8080,
                'protocol': 'websocket',
                'auto_reconnect': True,
                'reconnect_interval': 5
            },
            'sensors': {
                'gas': {
                    'enabled': True,
                    'warning_threshold': 50,
                    'danger_threshold': 100,
                    'unit': 'ppm'
                },
                'temperature': {
                    'enabled': True,
                    'warning_threshold': 40,
                    'danger_threshold': 50,
                    'unit': '°C'
                },
                'humidity': {
                    'enabled': True,
                    'unit': '%'
                },
                'gps': {
                    'enabled': True,
                    'update_interval': 1
                },
                'accelerometer': {
                    'enabled': True,
                    'sampling_rate': 100
                },
                'gyroscope': {
                    'enabled': True,
                    'sampling_rate': 100
                }
            },
            'ml': {
                'fall_detection': {
                    'enabled': True,
                    'model_path': 'models/fall_detection.pkl',
                    'threshold': 0.7,
                    'window_size': 50
                }
            },
            'alerts': {
                'sound_enabled': True,
                'notification_enabled': True,
                'log_all_events': True
            },
            'data': {
                'log_retention_days': 30,
                'export_format': 'csv',
                'auto_export': False
            }
        }
        
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation
        
        Args:
            key: Configuration key (e.g., 'ui.theme')
            default: Default value if key doesn't exist
            
        Returns:
            Configuration value
        """
        with self._lock:
            keys = key.split('.')
            value = self._config
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
                    
            return value
            
    def set(self, key: str, value: Any, save: bool = True):
        """
        Set configuration value using dot notation
        
        Args:
            key: Configuration key (e.g., 'ui.theme')
            value: Value to set
            save: Whether to immediately save to file
        """
        with self._lock:
            keys = key.split('.')
            config = self._config
            
            # Navigate to the parent dictionary
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
                
            # Set the value
            config[keys[-1]] = value
            
            if save:
                self._save_config()
                
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section"""
        return self.get(section, {})
        
    def set_section(self, section: str, values: Dict[str, Any], save: bool = True):
        """Set entire configuration section"""
        self.set(section, values, save)
        
    def reset_to_defaults(self):
        """Reset configuration to default values"""
        with self._lock:
            self._config = self._get_default_config()
            self._save_config()
            
    def reload(self):
        """Reload configuration from file"""
        self._load_config()