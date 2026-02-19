"""PRODUCTION CONFIGURATION LOADER"""
import os
import yaml
from typing import Dict

def load_config(config_path: str) -> Dict:
    """Load production configuration"""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Override with environment variables
    for key, value in os.environ.items():
        if key in config:
            config[key] = value
    
    return config
