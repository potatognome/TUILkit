# tUilKit/interfaces/cli_menu_interface.py
"""
This module defines the CLIMenuInterface, which provides an abstract interface for
building interactive command-line menus with consistent navigation and input handling.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Callable
from pathlib import Path


class CLIMenuInterface(ABC):
    """
    Interface for CLI menu handlers providing standardized menu patterns,
    navigation, input validation, and interactive selection.
    """
    
    @abstractmethod
    def show_numbered_menu(
        self, 
        title: str, 
        options: List[Dict[str, Any]], 
        allow_back: bool = True,
        allow_quit: bool = True
    ) -> Optional[str]:
        """
        Display a numbered menu and get user selection.
        
        Args:
            title: Menu title/header text
            options: List of option dicts with keys: 'key', 'label', 'icon' (optional)
            allow_back: Add a 'back' option
            allow_quit: Add a 'quit' option
            
        Returns:
            Selected option key, 'back', 'quit', or None if invalid
        """
        pass
    
    @abstractmethod
    def browse_directory(
        self, 
        start_path: Optional[Path] = None,
        title: str = "Browse Directory",
        allow_creation: bool = False
    ) -> Optional[Path]:
        """
        Interactive directory browser with navigation.
        
        Args:
            start_path: Starting directory (default: current directory)
            title: Browser window title
            allow_creation: Allow creating new directories
            
        Returns:
            Selected directory path or None if cancelled
        """
        pass
    
    @abstractmethod
    def select_from_list(
        self, 
        title: str, 
        items: List[str],
        multi_select: bool = False,
        allow_all: bool = True,
        icons: Optional[List[str]] = None
    ) -> Optional[List[str]]:
        """
        Select one or more items from a list.
        
        Args:
            title: Selection prompt title
            items: List of items to choose from
            multi_select: Allow multiple selections
            allow_all: Add 'all' option for multi-select
            icons: Optional list of icons (one per item)
            
        Returns:
            List of selected items or None if cancelled
        """
        pass
    
    @abstractmethod
    def confirm(
        self, 
        message: str, 
        default: bool = False
    ) -> bool:
        """
        Yes/no confirmation prompt.
        
        Args:
            message: Confirmation question
            default: Default value if user presses Enter
            
        Returns:
            True for yes, False for no
        """
        pass
    
    @abstractmethod
    def prompt_with_default(
        self,
        prompt: str,
        default: Optional[str] = None,
        validator: Optional[Callable[[str], bool]] = None,
        allow_empty: bool = False
    ) -> Optional[str]:
        """
        Prompt for input with optional default value and validation.
        
        Args:
            prompt: Input prompt text
            default: Default value shown in brackets
            validator: Optional validation function (returns True if valid)
            allow_empty: Allow empty input
            
        Returns:
            User input or default value, None if cancelled
        """
        pass
    
    @abstractmethod
    def show_info_screen(
        self,
        title: str,
        info: Dict[str, Any],
        wait_for_input: bool = True
    ) -> None:
        """
        Display formatted information screen.
        
        Args:
            title: Screen title
            info: Dictionary of label: value pairs to display
            wait_for_input: Wait for user to press Enter before returning
        """
        pass
    
    @abstractmethod
    def get_numeric_choice(
        self,
        min_val: int,
        max_val: int,
        prompt: str = "Select option",
        allow_cancel: bool = True
    ) -> Optional[int]:
        """
        Get validated numeric input within a range.
        
        Args:
            min_val: Minimum valid value
            max_val: Maximum valid value
            prompt: Input prompt text
            allow_cancel: Allow 'back' or 'cancel' input
            
        Returns:
            Selected number or None if cancelled
        """
        pass
    
    @abstractmethod
    def show_menu_with_preview(
        self,
        title: str,
        items: List[Dict[str, Any]],
        preview_func: Callable[[Any], str]
    ) -> Optional[Any]:
        """
        Show menu where selecting an item displays a preview.
        
        Args:
            title: Menu title
            items: List of items with 'label' and 'data' keys
            preview_func: Function to generate preview text from item data
            
        Returns:
            Selected item data or None if cancelled
        """
        pass
    
    @abstractmethod
    def edit_key_value_pairs(
        self,
        title: str,
        data: Dict[str, Any],
        prompts: Dict[str, str],
        validators: Optional[Dict[str, Callable]] = None
    ) -> Dict[str, Any]:
        """
        Interactive editor for key-value pairs.
        
        Args:
            title: Editor title
            data: Current data dictionary
            prompts: Display prompts for each key
            validators: Optional validation functions per key
            
        Returns:
            Updated data dictionary
        """
        pass
