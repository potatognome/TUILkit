# Lib/site-packages/tUilKit/interfaces/config_loader_interface.py
"""
    This module defines the ConfigLoaderInterface, which provides an abstract interface for
    loading JSON configuration files and ensuring the existence of specified folders.
"""
 
from abc import ABC, abstractmethod

class ConfigLoaderInterface(ABC):
    @abstractmethod
    def load_config(self, json_file_path: str) -> dict:
        pass

    @abstractmethod
    def get_json_path(self, file: str, cwd: bool = False) -> str:
        pass

    @abstractmethod
    def ensure_folders_exist(self, file_system) -> None:
        """Create all folders specified in the configuration using the provided file system."""

    @abstractmethod
    def get_config_file_path(self, config_key: str) -> str:
        """Get the path to a config file from the CONFIG_FILES section."""

    @abstractmethod
    def get_log_file_path(self, log_key: str) -> str:
        """Get the path to a log file from the LOG_FILES section."""

    @abstractmethod
    def load_colour_config(self) -> dict:
        """Load the colour configuration from the COLOURS config file."""

    @abstractmethod
    def load_border_patterns_config(self) -> dict:
        """Load the border patterns configuration from the BORDER_PATTERNS config file."""
        pass
