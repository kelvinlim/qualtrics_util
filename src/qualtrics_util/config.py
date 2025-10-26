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
from zoneinfo import ZoneInfo


class ConfigLoader:
    """Load and manage configuration for Qualtrics operations."""
    
    def __init__(self):
        self.config: Dict[str, Any] = {}
        self.api_token: Optional[str] = None
        self._base_dir = self._find_base_directory()
        self._config_file_path: Optional[str] = None
        self._config_file_lines: list = []
    
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
                # Store file content for line number lookup
                self._config_file_lines = f.readlines()
                f.seek(0)  # Reset file pointer
                self._config_file_path = str(config_path)
                self.config = yaml.safe_load(f)
            
            if not self.config:
                print("Error: Configuration file is empty")
                return False
            
            # Validate timezones
            self._validate_timezones()
                
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
    
    def _validate_timezones(self):
        """
        Validate IANA timezones in configuration.
        
        Raises:
            ValueError: If timezone is invalid
        """
        # Validate project timezone
        timezone_str = self.config.get('project', {}).get('TIMEZONE')
        if timezone_str:
            self._validate_timezone(timezone_str, 'project:TIMEZONE', 'TIMEZONE')
        
        # Validate embedded_data timezone
        timezone_str = self.config.get('embedded_data', {}).get('TimeZone')
        if timezone_str:
            self._validate_timezone(timezone_str, 'embedded_data:TimeZone', 'TimeZone')
    
    def _validate_timezone(self, timezone_str: str, field_name: str, key_name: str):
        """
        Validate that a timezone string is a valid IANA timezone.
        
        Args:
            timezone_str: The timezone string to validate
            field_name: The field name for error reporting
            key_name: The key name to search for in the config file
        
        Raises:
            ValueError: If timezone is invalid
        """
        try:
            # Try to create a ZoneInfo object with the timezone string
            ZoneInfo(timezone_str)
        except (ValueError, Exception) as e:
            # Find the line number in the config file
            line_num = self._find_line_number(key_name)
            file_info = f" in {self._config_file_path}" if self._config_file_path else ""
            line_info = f" on line {line_num}" if line_num > 0 else ""
            
            # Catch both ValueError and ZoneInfoNotFoundError
            raise ValueError(
                f"Invalid timezone '{timezone_str}' in {field_name}{line_info}{file_info}. "
                f"It must be a valid IANA timezone name (e.g., 'America/New_York', 'Europe/London'). "
                f"Error: {e}"
            )
    
    def _find_line_number(self, key_name: str) -> int:
        """Find the line number of a key in the config file."""
        if not self._config_file_lines:
            return 0
        
        for i, line in enumerate(self._config_file_lines, start=1):
            if key_name in line:
                return i
        return 0


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
