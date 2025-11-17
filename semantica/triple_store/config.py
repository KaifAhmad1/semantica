"""
Configuration Management Module for Triple Store

This module provides centralized configuration management for triple store operations,
supporting multiple configuration sources including environment variables, config files,
and programmatic configuration.

Supported Configuration Sources:
    - Environment variables: TRIPLE_STORE_DEFAULT_STORE, TRIPLE_STORE_BATCH_SIZE, TRIPLE_STORE_ENABLE_CACHING, etc.
    - Config files: YAML, JSON, TOML formats
    - Programmatic: Python API for setting triple store configurations

Algorithms Used:
    - Environment Variable Parsing: OS-level environment variable access
    - YAML Parsing: YAML parser for configuration file loading
    - JSON Parsing: JSON parser for configuration file loading
    - TOML Parsing: TOML parser for configuration file loading
    - Fallback Chain: Priority-based configuration resolution
    - Dictionary Merging: Deep merge algorithms for configuration updates

Key Features:
    - Environment variable support for triple store parameters
    - Config file support (YAML, JSON, TOML formats)
    - Programmatic configuration via Python API
    - Method-specific configuration management
    - Automatic fallback chain (config file -> environment -> defaults)
    - Global config instance for easy access

Main Classes:
    - TripleStoreConfig: Main configuration manager class for triple store module

Example Usage:
    >>> from semantica.triple_store.config import triple_store_config
    >>> default_store = triple_store_config.get("default_store", default="main")
    >>> triple_store_config.set("default_store", "main")
    >>> method_config = triple_store_config.get_method_config("add_triple")
"""

import os
from typing import Optional, Dict, Any
from pathlib import Path

from ..utils.logging import get_logger


class TripleStoreConfig:
    """Configuration manager for triple store module - supports .env files, environment variables, and programmatic config."""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Optional path to configuration file (YAML, JSON, or TOML)
        """
        self.logger = get_logger("triple_store_config")
        self.config_file = config_file
        self._config: Dict[str, Any] = {}
        self._method_configs: Dict[str, Dict[str, Any]] = {}
        
        # Load configuration
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file, environment variables, and defaults."""
        # Load from config file if provided
        if self.config_file:
            self._load_from_file(self.config_file)
        
        # Load from environment variables
        self._load_from_env()
        
        # Set defaults
        self._set_defaults()
    
    def _load_from_file(self, file_path: str) -> None:
        """Load configuration from file."""
        file_path = Path(file_path)
        if not file_path.exists():
            self.logger.warning(f"Config file not found: {file_path}")
            return
        
        try:
            if file_path.suffix in ['.yaml', '.yml']:
                import yaml
                with open(file_path, 'r') as f:
                    config_data = yaml.safe_load(f)
                    if config_data and 'triple_store' in config_data:
                        self._config.update(config_data['triple_store'])
            elif file_path.suffix == '.json':
                import json
                with open(file_path, 'r') as f:
                    config_data = json.load(f)
                    if config_data and 'triple_store' in config_data:
                        self._config.update(config_data['triple_store'])
            elif file_path.suffix == '.toml':
                import tomli
                with open(file_path, 'rb') as f:
                    config_data = tomli.load(f)
                    if config_data and 'triple_store' in config_data:
                        self._config.update(config_data['triple_store'])
        except Exception as e:
            self.logger.error(f"Failed to load config file: {e}")
    
    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        env_mappings = {
            'TRIPLE_STORE_DEFAULT_STORE': 'default_store',
            'TRIPLE_STORE_BATCH_SIZE': 'batch_size',
            'TRIPLE_STORE_ENABLE_CACHING': 'enable_caching',
            'TRIPLE_STORE_CACHE_SIZE': 'cache_size',
            'TRIPLE_STORE_ENABLE_OPTIMIZATION': 'enable_optimization',
            'TRIPLE_STORE_MAX_RETRIES': 'max_retries',
            'TRIPLE_STORE_RETRY_DELAY': 'retry_delay',
            'TRIPLE_STORE_TIMEOUT': 'timeout',
            'TRIPLE_STORE_BLAZEGRAPH_ENDPOINT': 'blazegraph_endpoint',
            'TRIPLE_STORE_JENA_ENDPOINT': 'jena_endpoint',
            'TRIPLE_STORE_RDF4J_ENDPOINT': 'rdf4j_endpoint',
            'TRIPLE_STORE_VIRTUOSO_ENDPOINT': 'virtuoso_endpoint',
        }
        
        for env_var, config_key in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                # Convert string values to appropriate types
                if config_key in ['batch_size', 'cache_size', 'max_retries', 'timeout']:
                    try:
                        self._config[config_key] = int(value)
                    except ValueError:
                        self.logger.warning(f"Invalid integer value for {env_var}: {value}")
                elif config_key in ['enable_caching', 'enable_optimization']:
                    self._config[config_key] = value.lower() in ['true', '1', 'yes', 'on']
                elif config_key == 'retry_delay':
                    try:
                        self._config[config_key] = float(value)
                    except ValueError:
                        self.logger.warning(f"Invalid float value for {env_var}: {value}")
                else:
                    self._config[config_key] = value
    
    def _set_defaults(self) -> None:
        """Set default configuration values."""
        defaults = {
            'default_store': None,
            'batch_size': 1000,
            'enable_caching': True,
            'cache_size': 1000,
            'enable_optimization': True,
            'max_retries': 3,
            'retry_delay': 1.0,
            'timeout': 30,
        }
        
        for key, default_value in defaults.items():
            if key not in self._config:
                self._config[key] = default_value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        """
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        self._config[key] = value
    
    def update(self, config: Dict[str, Any]) -> None:
        """
        Update configuration with dictionary.
        
        Args:
            config: Configuration dictionary
        """
        self._config.update(config)
    
    def get_method_config(self, method_name: str) -> Dict[str, Any]:
        """
        Get method-specific configuration.
        
        Args:
            method_name: Method name
        
        Returns:
            Method configuration dictionary
        """
        return self._method_configs.get(method_name, {}).copy()
    
    def set_method_config(self, method_name: str, config: Dict[str, Any]) -> None:
        """
        Set method-specific configuration.
        
        Args:
            method_name: Method name
            config: Method configuration dictionary
        """
        self._method_configs[method_name] = config.copy()
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration.
        
        Returns:
            Complete configuration dictionary
        """
        return self._config.copy()
    
    def reset(self) -> None:
        """Reset configuration to defaults."""
        self._config.clear()
        self._method_configs.clear()
        self._set_defaults()


# Global configuration instance
triple_store_config = TripleStoreConfig()

