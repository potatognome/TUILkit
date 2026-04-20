# Lib/site-packages/tUilKit/interfaces/file_system_interface.py
"""
    This module defines the FileSystemInterface, which provides an abstract interface for
    file system operations such as folder creation, removal of empty folders, and file listing.
    Implementations should handle logging via the provided log_files parameter and use colour keys
    for consistent output formatting (e.g., !path for paths, !file for filenames, !create for creation actions).
"""

from abc import ABC, abstractmethod

class FileSystemInterface(ABC):
    def __init__(self, logger, log_files=None):
        self.logger = logger
        self.log_files = log_files or {}

    @abstractmethod
    def validate_and_create_folder(self, folder_path: str, log: bool = True, log_to: str = "both", category="fs") -> bool:
        """
        Validates and creates a folder if it does not exist.
        Logs the action using colour keys like !try, !create, !path, !pass.
        Returns True if successful.
        """
        pass

    @abstractmethod
    def remove_empty_folders(self, path: str, log: bool = True, category="fs") -> None:
        """
        Recursively removes empty folders under the given path.
        Logs each removal using !pass and !path colour keys.
        """
        pass

    @abstractmethod
    def get_all_files(self, folder: str) -> list[str]:
        """
        Returns a list of all files (not directories) in the specified folder.
        """
        pass
