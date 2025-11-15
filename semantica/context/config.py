"""
Configuration Management Module for Context Engineering

This module provides centralized configuration management for context engineering operations,
supporting multiple configuration sources including environment variables, config files,
and programmatic configuration.

Supported Configuration Sources:
    - Environment variables: CONTEXT_RETENTION_POLICY, CONTEXT_MAX_MEMORY_SIZE, etc.
    - Config files: YAML, JSON, TOML formats
    - Programmatic: Python API for setting context configurations

Algorithms Used:
    - Environment Variable Parsing: OS-level environment variable access
    - YAML Parsing: YAML parser for configuration file loading
    - JSON Parsing: JSON parser for configuration file loading
    - TOML Parsing: TOML parser for configuration file loading
    - Fallback Chain: Priority-based configuration resolution
    - Dictionary Merging: Deep merge algorithms for configuration updates

Key Features:
    - Environment variable support for context parameters
    - Config file support (YAML, JSON, TOML formats)
    - Programmatic configuration via Python API
    - Method-specific configuration management
    - Automatic fallback chain (config file -> environment -> defaults)
    - Global config instance for easy access

Main Classes:
    - ContextConfig: Main configuration manager class for context module

Example Usage:
    >>> from semantica.context.config import context_config
    >>> retention = context_config.get("retention_policy", default="unlimited")
    >>> context_config.set("retention_policy", "30_days")
    >>> method_config = context_config.get_method_config("graph")

Author: Semantica Contributors
License: MIT
"""

import os
from typing import Optional, Dict, Any
from pathlib import Path

from ..utils.logging import get_logger


class ContextConfig:
    """Configuration manager for context module - supports .env files, environment variables, and programmatic config."""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration manager."""
        self.logger = get_logger("context_config")
        self._configs: Dict[str, Any] = {}
        self._method_configs: Dict[str, Dict] = {}
        self._load_config_file(config_file)
        self._load_env_vars()
    
    def _load_config_file(self, config_file: Optional[str]):
        """Load configuration from file."""
        if config_file and Path(config_file).exists():
            try:
                # Support YAML, JSON, TOML
                if config_file.endswith('.yaml') or config_file.endswith('.yml'):
                    import yaml
                    with open(config_file, 'r') as f:
                        data = yaml.safe_load(f) or {}
                        self._configs.update(data.get("context", {}))
                        self._method_configs.update(data.get("context_methods", {}))
                elif config_file.endswith('.json'):
                    import json
                    with open(config_file, 'r') as f:
                        data = json.load(f) or {}
                        self._configs.update(data.get("context", {}))
                        self._method_configs.update(data.get("context_methods", {}))
                elif config_file.endswith('.toml'):
                    import toml
                    with open(config_file, 'r') as f:
                        data = toml.load(f) or {}
                        self._configs.update(data.get("context", {}))
                        self._method_configs.update(data.get("context_methods", {}))
                self.logger.info(f"Loaded context config from {config_file}")
            except Exception as e:
                self.logger.warning(f"Failed to load config file {config_file}: {e}")
    
    def _load_env_vars(self):
        """Load configuration from environment variables."""
        # Context-specific environment variables with CONTEXT_ prefix
        env_prefix = "CONTEXT_"
        
        for key, value in os.environ.items():
            if key.startswith(env_prefix):
                config_key = key[len(env_prefix):].lower()
                # Try to convert to appropriate type
                if value.lower() in ('true', 'false'):
                    self._configs[config_key] = value.lower() == 'true'
                elif value.isdigit():
                    self._configs[config_key] = int(value)
                else:
                    try:
                        self._configs[config_key] = float(value)
                    except ValueError:
                        self._configs[config_key] = value
    
    def set(self, key: str, value: Any):
        """Set a configuration value."""
        self._configs[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self._configs.get(key, default)
    
    def set_method_config(self, method_name: str, config: Dict[str, Any]):
        """Set method-specific configuration."""
        self._method_configs[method_name] = config
    
    def get_method_config(self, method_name: str) -> Dict[str, Any]:
        """Get method-specific configuration."""
        return self._method_configs.get(method_name, {})
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configurations."""
        return {
            "configs": self._configs.copy(),
            "method_configs": self._method_configs.copy()
        }


context_config = ContextConfig()

