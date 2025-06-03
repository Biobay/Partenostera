import yaml
import os
from typing import Any, Dict, Optional

class Config:
    """Configuration manager for the application"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self._config = {}
        self.load_config()
    
    def load_config(self):
        """Load configuration from YAML file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._config = yaml.safe_load(f) or {}
            else:
                print(f"Warning: Config file {self.config_path} not found, using defaults")
                self._config = self._get_default_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            self._config = self._get_default_config()
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation
        Example: config.get("server.host", "localhost")
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value using dot notation"""
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self._config, f, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "server": {
                "host": "0.0.0.0",
                "port": 8000,
                "debug": True
            },
            "generation": {
                "max_file_size": "50MB",
                "supported_formats": [".txt", ".pdf", ".docx"],
                "max_sequences": 20,
                "image_size": [1024, 1024],
                "video_fps": 24,
                "audio_sample_rate": 22050
            },
            "models": {
                "stable_diffusion": {
                    "model_id": "runwayml/stable-diffusion-v1-5",
                    "device": "auto"
                },
                "tts": {
                    "model_name": "tts_models/multilingual/multi-dataset/xtts_v2",
                    "language": "it"
                },
                "veo": {
                    "api_endpoint": "https://api.veo.dev/v1",
                    "api_key": "your-veo-api-key"
                }
            },
            "validation": {
                "min_image_quality": 0.7,
                "max_generation_time": 300,
                "content_safety": True
            },
            "storage": {
                "output_path": "./data/outputs",
                "books_path": "./data/books",
                "temp_path": "./data/temp"
            }
        }
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration"""
        return self._config.copy()
    
    def update(self, config_dict: Dict[str, Any]):
        """Update configuration with a dictionary"""
        self._deep_update(self._config, config_dict)
    
    def _deep_update(self, base_dict: Dict, update_dict: Dict):
        """Deep update dictionary"""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value
