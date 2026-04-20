# tUilKit/utils/cli_menus.py
"""
Implementation of CLIMenuInterface for building interactive command-line menus.
"""

import os
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable

# Add the base directory of the project to the system path
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..\\..\\'))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from tUilKit.interfaces.cli_menu_interface import CLIMenuInterface
from tUilKit.interfaces.logger_interface import LoggerInterface
from tUilKit.utils.output import Logger, ColourManager
from tUilKit.utils.config import ConfigLoader


class CLIMenuHandler(CLIMenuInterface):
    """
    Concrete implementation of CLIMenuInterface providing interactive
    command-line menu functionality with colour-coded output.
    """
    
    def __init__(self, logger: Optional[LoggerInterface] = None):
        """
        Initialize CLIMenuHandler.
        
        Args:
            logger: Optional LoggerInterface instance (creates default if None)
        """
        self.logger = logger or Logger()
        config_loader = ConfigLoader()
        self.log_files = config_loader.global_config.get("LOG_FILES", {})
    
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
        print()  # Blank line for spacing
        self.logger.apply_border(
            text=title,
            pattern={"TOP": "=", "BOTTOM": "=", "LEFT": " ", "RIGHT": " "},
            total_length=60,
            border_rainbow=True
        )
        print()
        
        # Display options
        for i, option in enumerate(options, 1):
            icon = option.get('icon', '📋')
            label = option.get('label', f"Option {i}")
            self.logger.colour_log("!list", str(i), "!info", f". {icon} {label}")
        
        # Add back/quit options
        extra_options = []
        if allow_back:
            extra_options.append("'back'")
        if allow_quit:
            extra_options.append("'quit'")
        
        # Build prompt
        max_num = len(options)
        prompt_parts = [f"1-{max_num}"]
        if extra_options:
            prompt_parts.append(" or " + ", ".join(extra_options))
        
        prompt = f"\nSelect option ({','.join(prompt_parts)}): "
        choice = input(prompt).strip().lower()
        
        # Log the selection
        self.logger.colour_log("!prompt", "Selected: ", "!selection", f"{choice}")
        
        # Handle back/quit
        if allow_back and choice in ['back', 'b']:
            return 'back'
        if allow_quit and choice in ['quit', 'q', 'exit']:
            return 'quit'
        
        # Handle numeric selection
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(options):
                return options[choice_num - 1].get('key')
            else:
                self.logger.colour_log("!error", f"❌ Please select 1-{len(options)}")
                return None
        except ValueError:
            self.logger.colour_log("!error", "❌ Invalid input")
            return None
    
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
        current_path = Path(start_path) if start_path else Path.cwd()
        
        if not current_path.exists():
            self.logger.colour_log("!warn", f"⚠️  Path does not exist: {current_path}")
            current_path = Path.cwd()
        
        while True:
            print()
            self.logger.apply_border(
                text=f"📂 {title}",
                pattern={"TOP": "=", "BOTTOM": "=", "LEFT": " ", "RIGHT": " "},
                total_length=60,
                border_rainbow=True
            )
            print()
            
            self.logger.colour_log("!info", "Current path:", "!path", str(current_path))
            print()
            
            # List directories
            try:
                subdirs = [d for d in current_path.iterdir() if d.is_dir()]
                subdirs.sort()
            except PermissionError:
                self.logger.colour_log("!error", "❌ Permission denied")
                subdirs = []
            
            # Show parent option
            if current_path.parent != current_path:
                self.logger.colour_log("!list", "0", "!info", ". 📁 .. (Parent directory)")
            
            # Show subdirectories
            for i, subdir in enumerate(subdirs, 1):
                self.logger.colour_log("!list", str(i), "!info", f". 📁 {subdir.name}")
            
            print()
            self.logger.colour_log("!info", "Options:")
            self.logger.colour_log("!info", "  - Enter number to navigate")
            self.logger.colour_log("!info", "  - 's' to select current directory")
            if allow_creation:
                self.logger.colour_log("!info", "  - 'n' to create new directory here")
            self.logger.colour_log("!info", "  - 'cancel' to cancel")
            
            choice = input("\nChoice: ").strip().lower()
            
            # Log the selection
            self.logger.colour_log("!prompt", "Selected: ", "!selection", f"{choice}")
            
            if choice == 'cancel':
                return None
            elif choice == 's':
                return current_path
            elif choice == 'n' and allow_creation:
                new_name = input("New directory name: ").strip()
                if new_name:
                    new_path = current_path / new_name
                    try:
                        new_path.mkdir(exist_ok=True)
                        self.logger.colour_log("!done", f"✅ Created: {new_path}")
                        current_path = new_path
                    except Exception as e:
                        self.logger.colour_log("!error", f"❌ Could not create directory: {e}")
            else:
                try:
                    choice_num = int(choice)
                    if choice_num == 0 and current_path.parent != current_path:
                        current_path = current_path.parent
                    elif 1 <= choice_num <= len(subdirs):
                        current_path = subdirs[choice_num - 1]
                    else:
                        self.logger.colour_log("!error", f"❌ Invalid choice")
                except ValueError:
                    self.logger.colour_log("!error", "❌ Invalid input")
    
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
        print()
        self.logger.colour_log("!info", f"📋 {title}")
        print()
        
        # Display items
        for i, item in enumerate(items, 1):
            icon = icons[i-1] if icons and i-1 < len(icons) else "📄"
            self.logger.colour_log("!list", str(i), "!info", f". {icon} {item}")
        
        # Build prompt
        if multi_select:
            if allow_all:
                prompt = f"\nSelect (1-{len(items)}, comma-separated, or 'all'): "
            else:
                prompt = f"\nSelect (1-{len(items)}, comma-separated): "
        else:
            prompt = f"\nSelect (1-{len(items)} or 'cancel'): "
        
        choice = input(prompt).strip().lower()
        
        # Log the selection
        self.logger.colour_log("!prompt", "Selected: ", "!selection", f"{choice}")
        
        if choice == 'cancel':
            return None
        
        if multi_select and allow_all and choice == 'all':
            return items.copy()
        
        # Parse selection(s)
        try:
            if multi_select:
                indices = [int(x.strip()) for x in choice.split(',')]
                selected = []
                for idx in indices:
                    if 1 <= idx <= len(items):
                        selected.append(items[idx - 1])
                    else:
                        self.logger.colour_log("!warn", f"⚠️  Skipping invalid index: {idx}")
                return selected if selected else None
            else:
                idx = int(choice)
                if 1 <= idx <= len(items):
                    return [items[idx - 1]]
                else:
                    self.logger.colour_log("!error", f"❌ Please select 1-{len(items)}")
                    return None
        except ValueError:
            self.logger.colour_log("!error", "❌ Invalid input")
            return None
    
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
        default_str = "Y/n" if default else "y/N"
        choice = input(f"\n{message} ({default_str}): ").strip().lower()
        
        # Log the selection
        if choice:
            self.logger.colour_log("!prompt", "Selected: ", "!selection", f"{choice}")
        else:
            self.logger.colour_log("!prompt", "Selected: ", "!selection", "(default)")
        
        if not choice:
            return default
        
        return choice in ['y', 'yes']
    
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
        if default:
            full_prompt = f"{prompt} [{default}]: "
        else:
            full_prompt = f"{prompt}: "
        
        while True:
            value = input(full_prompt).strip()
            
            # Log the selection
            if value:
                self.logger.colour_log("!prompt", "Selected: ", "!selection", f"{value}")
            else:
                self.logger.colour_log("!prompt", "Selected: ", "!selection", "(empty)")
            
            # Handle empty input
            if not value:
                if default:
                    return default
                elif allow_empty:
                    return ""
                else:
                    self.logger.colour_log("!error", "❌ Input cannot be empty")
                    continue
            
            # Handle cancel
            if value.lower() in ['cancel', 'back']:
                return None
            
            # Validate if validator provided
            if validator:
                if validator(value):
                    return value
                else:
                    self.logger.colour_log("!error", "❌ Invalid input")
                    continue
            
            return value
    
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
        print()
        self.logger.apply_border(
            text=f"ℹ️  {title}",
            pattern={"TOP": "=", "BOTTOM": "=", "LEFT": " ", "RIGHT": " "},
            total_length=60,
            border_rainbow=True
        )
        print()
        
        for label, value in info.items():
            self.logger.colour_log("!info", f"{label}:", "!data", str(value))
        
        if wait_for_input:
            input("\nPress Enter to continue...")
    
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
        while True:
            if allow_cancel:
                full_prompt = f"\n{prompt} ({min_val}-{max_val} or 'cancel'): "
            else:
                full_prompt = f"\n{prompt} ({min_val}-{max_val}): "
            
            choice = input(full_prompt).strip().lower()
            
            if allow_cancel and choice in ['cancel', 'back', 'q', 'quit']:
                return None
            
            try:
                choice_num = int(choice)
                if min_val <= choice_num <= max_val:
                    return choice_num
                else:
                    self.logger.colour_log("!error", f"❌ Please enter {min_val}-{max_val}")
            except ValueError:
                self.logger.colour_log("!error", "❌ Please enter a valid number")
    
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
        while True:
            print()
            self.logger.apply_border(
                text=title,
                pattern={"TOP": "=", "BOTTOM": "=", "LEFT": " ", "RIGHT": " "},
                total_length=60,
                border_rainbow=True
            )
            print()
            
            # Display items
            for i, item in enumerate(items, 1):
                label = item.get('label', f"Item {i}")
                self.logger.colour_log("!list", str(i), "!info", f". {label}")
            
            choice = input(f"\nSelect item (1-{len(items)}) for preview, 's' to select, or 'cancel': ").strip().lower()
            
            if choice == 'cancel':
                return None
            elif choice == 's':
                idx = input(f"Select item to return (1-{len(items)}): ").strip()
                try:
                    idx_num = int(idx)
                    if 1 <= idx_num <= len(items):
                        return items[idx_num - 1].get('data')
                except ValueError:
                    pass
            else:
                try:
                    idx_num = int(choice)
                    if 1 <= idx_num <= len(items):
                        # Show preview
                        item_data = items[idx_num - 1].get('data')
                        preview = preview_func(item_data)
                        print()
                        self.logger.colour_log("!info", "=" * 60)
                        print(preview)
                        self.logger.colour_log("!info", "=" * 60)
                        input("\nPress Enter to continue...")
                except ValueError:
                    self.logger.colour_log("!prompt", f"Selected: ", "!selection", f"{choice}")
                    self.logger.colour_log("!error", "❌ Invalid input")
    
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
        print()
        self.logger.apply_border(
            text=f"✏️  {title}",
            pattern={"TOP": "=", "BOTTOM": "=", "LEFT": " ", "RIGHT": " "},
            total_length=60,
            border_rainbow=True
        )
        print()
        self.logger.colour_log("!info", "Leave blank to keep current value")
        print()
        
        result = data.copy()
        validators = validators or {}
        
        for key, prompt_text in prompts.items():
            current_value = result.get(key, '')
            validator = validators.get(key)
            
            new_value = self.prompt_with_default(
                prompt_text,
                default=str(current_value) if current_value else None,
                validator=validator,
                allow_empty=True
            )
            
            if new_value is not None and new_value != str(current_value):
                result[key] = new_value
        
        return result
