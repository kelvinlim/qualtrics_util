"""
Configuration management for qualtrics_util.

This module handles loading and validation of configuration files,
environment variables, and API credentials.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import yaml
from dotenv import dotenv_values


class ConfigLoader:
    """Load and manage configuration for Qualtrics operations."""
    
    def __init__(self):
        self.config: Dict[str, Any] = {}
        self.api_token: Optional[str] = None
        self._base_dir = self._find_base_directory()
    
    def _find_base_directory(self) -> Path:
        """
        Find the base directory of the project.
        
        Returns:
            Path: Base directory path
            
        Note:
            Works both in development and in packaged executables.
        """
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            return Path(sys.executable).parent
        else:
            # Running from source
            return Path(__file__).parent.parent.parent
    
    def load_environment(self, env_file: str = 'qualtrics_token') -> bool:
        """
        Load API token from environment file.
        
        Args:
            env_file: Name of the environment file containing the API token
            
        Returns:
            bool: True if token was loaded successfully, False otherwise
            
        Raises:
            FileNotFoundError: If the environment file doesn't exist
            ValueError: If QUALTRICS_APITOKEN is not found in the file
        """
        env_path = self._base_dir / env_file
        
        if not env_path.exists():
            # Try current working directory as fallback
            env_path = Path(env_file)
            if not env_path.exists():
                print(f"Error: {env_file} not found in {self._base_dir} or current directory")
                return False
        
        env_config = dotenv_values(str(env_path))
        self.api_token = env_config.get('QUALTRICS_APITOKEN')
        
        if not self.api_token:
            print(f"Error: QUALTRICS_APITOKEN not found in {env_file}")
            return False
        
        return True
    
    def load_config(self, config_file: Optional[str] = None) -> bool:
        """
        Load configuration from YAML file.
        
        Args:
            config_file: Path to configuration file. If None, uses default.
            
        Returns:
            bool: True if config was loaded successfully, False otherwise
            
        Raises:
            FileNotFoundError: If the config file doesn't exist
            yaml.YAMLError: If the config file is invalid YAML
        """
        if config_file is None:
            config_file = 'config_qualtrics.yaml'
        
        # Try to find config file
        config_path = self._find_config_file(config_file)
        
        if not config_path:
            print(f"Error: Configuration file '{config_file}' not found")
            return False
        
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            
            if not self.config:
                print("Error: Configuration file is empty")
                return False
                
            return True
            
        except yaml.YAMLError as e:
            print(f"Error loading configuration: {e}")
            return False
    
    def _find_config_file(self, config_file: str) -> Optional[Path]:
        """
        Find configuration file in various locations.
        
        Args:
            config_file: Name or path of config file
            
        Returns:
            Optional[Path]: Path to config file if found, None otherwise
        """
        # If it's an absolute path or explicit relative path, use it directly
        config_path = Path(config_file)
        if config_path.is_absolute() or '/' in config_file:
            if config_path.exists():
                return config_path
        else:
            # Try to find in config directory
            config_dir = self._base_dir / 'config'
            config_file_path = config_dir / config_file
            if config_file_path.exists():
                return config_file_path
            
            # Try in base directory
            config_file_path = self._base_dir / config_file
            if config_file_path.exists():
                return config_file_path
            
            # Try current working directory
            config_file_path = Path(config_file)
            if config_file_path.exists():
                return config_file_path
        
        return None
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key (supports nested keys with dots).
        
        Args:
            key: Configuration key (supports dot notation, e.g., 'account.DATA_CENTER')
            default: Default value if key not found
            
        Returns:
            Any: Configuration value or default
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def validate(self) -> bool:
        """
        Validate that required configuration is present.
        
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        required_sections = ['account', 'project', 'embedded_data']
        
        for section in required_sections:
            if section not in self.config:
                print(f"Error: Missing required section '{section}' in configuration")
                return False
        
        # Validate account section
        account = self.config['account']
        required_account = ['DATA_CENTER', 'DEFAULT_DIRECTORY']
        for key in required_account:
            if key not in account:
                print(f"Error: Missing required key 'account.{key}' in configuration")
                return False
        
        # Validate project section
        project = self.config['project']
        required_project = ['MAILING_LIST_ID', 'SURVEY_ID', 'MESSAGE_ID']
        for key in required_project:
            if key not in project:
                print(f"Error: Missing required key 'project.{key}' in configuration")
                return False
        
        return True


def load_configuration(config_file: Optional[str] = None, 
                      env_file: str = 'qualtrics_token') -> tuple[ConfigLoader, bool]:
    """
    Load configuration and environment in one step.
    
    Args:
        config_file: Path to configuration file
        env_file: Path to environment file with API token
        
    Returns:
        tuple: (ConfigLoader instance, success boolean)
    """
    loader = ConfigLoader()
    
    # Load environment token
    if not loader.load_environment(env_file):
        return loader, False
    
    # Load configuration
    if not loader.load_config(config_file):
        return loader, False
    
    # Validate configuration
    if not loader.validate():
        return loader, False
    
    return loader, True
