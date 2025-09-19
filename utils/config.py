#!/usr/bin/env python3
"""
Shared configuration utilities
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ConfigManager:
    """Centralized configuration management"""

    def __init__(self):
        self.config_dir = Path("config")
        self.env_loaded = False

    def load_env(self, env_file: str = ".env") -> bool:
        """Load environment variables from .env file"""
        if self.env_loaded:
            return True

        env_path = self.config_dir / env_file
        if not env_path.exists():
            logger.warning(f"Environment file {env_path} not found")
            return False

        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()

            self.env_loaded = True
            logger.info("Environment variables loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to load environment: {e}")
            return False

    def load_json_config(self, config_file: str) -> Dict[str, Any]:
        """Load JSON configuration file"""
        config_path = self.config_dir / config_file
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config {config_file}: {e}")
            return {}

    def get_env_var(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get environment variable with optional default"""
        return os.getenv(key, default)

    def validate_required_env_vars(self, required_vars: list[str]) -> bool:
        """Validate that required environment variables are set"""
        missing = [var for var in required_vars if not os.getenv(var)]
        if missing:
            logger.error(f"Missing required environment variables: {missing}")
            return False
        return True

# Global config manager instance
config_manager = ConfigManager()