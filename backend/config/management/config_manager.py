import yaml
import logging
import os
from typing import Dict, Any, Optional
from pathlib import Path

from backend.config.management.config_type import ConfigType


class ConfigManager:
    """
    Centralized configuration manager for pipeline components.
    Loads and provides access to configuration data from component-specific YAML files.
    """
    
    DEFAULT_CONFIG_DIR = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "components"
    )
    
    def __init__(self, config_dir: Optional[str] = None, enable_logging: bool = True):
        self.config_dir = Path(config_dir or self.DEFAULT_CONFIG_DIR)
        self.enable_logging = enable_logging
        self._config_cache: Dict[ConfigType, Dict[str, Any]] = {}
        
        self._log(f"ConfigManager initialized with config directory: {self.config_dir}")
    
    def _log(self, message: str, level: int = logging.INFO) -> None:
        if self.enable_logging:
            logging.log(level, f"[ConfigManager] {message}")
    
    def _load_yaml_file(self, filepath: Path) -> Dict[str, Any]:
        """
        Load a YAML file and return its contents.
        
        Args:
            filepath: Path to the YAML file
            
        Returns:
            Dictionary with configuration data
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If YAML file is invalid
        """
        if not filepath.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {filepath}. "
                f"Please ensure the file exists in {self.config_dir}"
            )
        
        try:
            with open(filepath, "r") as f:
                config_data = yaml.safe_load(f)
                
                if config_data is None:
                    self._log(f"Config file is empty: {filepath}", level=logging.WARNING)
                    return {}
                
                self._log(f"Successfully loaded config from: {filepath}")
                return config_data
                
        except yaml.YAMLError as e:
            raise ValueError(f"Failed to parse YAML file {filepath}: {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error loading {filepath}: {e}")
    
    def _get_config_file_path(self, config_type: ConfigType) -> Path:
        return self.config_dir / config_type.filename
    
    def get_config(self, config_type: ConfigType) -> Dict[str, Any]:
        """
        Get configuration for a specific component.
        
        Args:
            config_type: Type of component configuration to retrieve
            
        Returns:
            Dictionary with configuration data for the component
            
        Raises:
            FileNotFoundError: If configuration file doesn't exist
            ValueError: If configuration file is invalid
        """
        if config_type in self._config_cache:
            self._log(f"Using cached config for {config_type.value}")
            return self._config_cache[config_type]
        
        config_path = self._get_config_file_path(config_type)
        config_data = self._load_yaml_file(config_path)
        
        self._config_cache[config_type] = config_data
        self._log(f"Cached config for {config_type.value}")
        
        return config_data
    
    def get_value(
        self, 
        config_type: ConfigType, 
        key_path: str, 
        default: Any = None
    ) -> Any:
        """
        Get a specific value from component configuration using dot notation.
        
        Args:
            config_type: Type of component configuration
            key_path: Path to the value using dot notation
            default: Default value to return if key not found
            
        Returns:
            The configuration value, or default if not found
        """
        config = self.get_config(config_type)
        
        keys = key_path.split(".")
        current = config
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                self._log(
                    f"Key path '{key_path}' not found in {config_type.value} config, "
                    f"returning default: {default}",
                    level=logging.DEBUG
                )
                return default
        
        return current
    
    def reload_config(self, config_type: Optional[ConfigType] = None) -> None:
        """
        Reload configuration from files.
        
        Args:
            config_type: Specific component to reload, or None to reload all
        """
        if config_type is None:
            self._config_cache.clear()
            self._log("Cleared all configuration cache")
        else:
            if config_type in self._config_cache:
                del self._config_cache[config_type]
                self._log(f"Cleared cache for {config_type.value}")
    
    def has_config(self, config_type: ConfigType) -> bool:
        """
        Check if a configuration file exists for the given type.
        
        Args:
            config_type: Type of component to check
            
        Returns:
            True if config file exists, False otherwise
        """
        config_path = self._get_config_file_path(config_type)
        return config_path.exists()
    
    def list_available_configs(self) -> list[ConfigType]:
        """
        List all available configuration types that have existing files.
        
        Returns:
            List of ConfigType enums for which config files exist
        """
        available = []
        for config_type in ConfigType:
            if self.has_config(config_type):
                available.append(config_type)
        return available
    
    def validate_all_configs_exist(self) -> bool:
        """
        Validate that all required configuration files exist.
        
        Returns:
            True if all config files exist, False otherwise
        """
        missing = []
        for config_type in ConfigType:
            if not self.has_config(config_type):
                missing.append(config_type)
        
        if missing:
            self._log(
                f"Missing configuration files for: {[ct.value for ct in missing]}",
                level=logging.ERROR
            )
            return False
        
        self._log("All required configuration files exist")
        return True
    
    def get_config_file_path(self, config_type: ConfigType) -> str:
        """
        Get the absolute path to a configuration file.
        
        Args:
            config_type: Type of component configuration
            
        Returns:
            Absolute path to the configuration file as string
        """
        return str(self._get_config_file_path(config_type).absolute())