# tUilKit/tools/colour_key_editor.py
"""
Interactive colour key editor for COLOURS.json
Allows visual selection of foreground/background colours for colour keys.
"""

import json
import sys
import msvcrt
from pathlib import Path
from typing import Optional, Tuple, List

from tUilKit import get_logger, get_cli_menu_handler, get_config_loader, get_colour_manager


class ColourKeyEditor:
    """Interactive editor for COLOURS.json colour keys."""
    
    def __init__(self, colours_path: Optional[Path] = None):
        """
        Initialize colour key editor.
        
        Args:
            colours_path: Path to COLOURS.json file. If None, uses default tUilKit config.
        """
        self.logger = get_logger()
        self.menu = get_cli_menu_handler()
        self.config_loader = get_config_loader()
        self.colour_manager = get_colour_manager()
        
        # Determine which COLOURS.json to edit
        if colours_path is None:
            self.colours_path = Path(__file__).parent.parent / "config" / "COLOURS.json"
        else:
            self.colours_path = Path(colours_path)
        
        # Verify file exists
        if not self.colours_path.exists():
            raise FileNotFoundError(f"COLOURS.json not found at: {self.colours_path}")
        
        # Load COLOURS.json
        with open(self.colours_path, 'r') as f:
            self.colours_data = json.load(f)
        
        self.colour_keys = self.colours_data.get("COLOUR_KEY", {})
        self.available_colours = [
            "RED", "ORANGE", "YELLOW", "GREEN", "BLUE", "INDIGO", "VIOLET",
            "CRIMSON", "CORAL", "GOLD", "CHARTREUSE", "CYAN", "PURPLE", "MAGENTA",
            "PINK", "TANGERINE", "CANARY", "LIME", "CORNFLOWER", "LAVENDER",
            "ROSE", "MANGO", "MINT", "SKY BLUE", "PEACH", "LEMON", "TURQUOISE",
            "LAVENDER BLUE", "SALMON", "HONEY", "SEAFOAM GREEN",
            "DARK RED", "DARK ORANGE", "DARK YELLOW", "DARK GREEN", "NAVY", "EGGPLANT",
            "MAROON", "BURGUNDY", "RUST", "OLIVE", "FOREST GREEN", "MIDNIGHT BLUE", "PLUM", "WINE",
            "MAHOGANY", "BROWN", "CHESTNUT", "TAN", "SAND", "ESPRESSO", "COCOA", "CINNAMON", "OCHRE", "BEIGE", "BRONZE",
            "BLACK", "CHARCOAL", "GREY", "LIGHT GREY", "ONYX", "SLATE", "DOVE GREY", "LIGHT SLATE",
            "IVORY", "SNOW", "GAINSBORO", "WHITE"
        ]
    
    def run(self):
        """Main editor loop."""
        self.logger.apply_border(
            text="🎨 Colour Key Editor",
            pattern={"TOP": "=", "BOTTOM": "=", "LEFT": " ", "RIGHT": " "},
            total_length=60,
            border_rainbow=True
        )
        
        # Show which file is being edited
        print()
        self.logger.colour_log("!info", "Editing file:", "!path", str(self.colours_path))
        print()
        
        while True:
            # Main menu
            options = [
                {'key': 'edit', 'label': 'Edit a colour key', 'icon': '🎨'},
                {'key': 'import', 'label': 'Import colour keys from file', 'icon': '📥'},
                {'key': 'export', 'label': 'Export colour keys to file', 'icon': '📤'},
                {'key': 'switch', 'label': 'Switch to different COLOURS.json', 'icon': '🔄'}
            ]
            
            action = self.menu.show_numbered_menu(
                title="Main Menu",
                options=options,
                allow_quit=True
            )
            
            if action == 'quit':
                break
            elif action == 'edit':
                self._edit_colour_key_workflow()
            elif action == 'import':
                self._import_colour_keys()
            elif action == 'export':
                self._export_colour_keys()
            elif action == 'switch':
                self._switch_file()
    
    def _edit_colour_key_workflow(self):
        """Run the edit colour key workflow."""
        # Step 1: Select colour key to edit
        colour_key = self._select_colour_key()
        if colour_key is None:
            return
        
        # Step 2: Select foreground or background
        edit_type = self._select_edit_type(colour_key)
        if edit_type is None:
            return
        
        # Step 3: Select new colour with arrow keys
        new_colour = self._select_colour_with_arrows(colour_key, edit_type)
        if new_colour is None:
            return
        
        # Step 4: Apply and save
        self._apply_colour_change(colour_key, edit_type, new_colour)
    
    def _select_colour_key(self) -> Optional[str]:
        """Show menu to select which colour key to edit."""
        print()
        self.logger.colour_log("!info", "Select a colour key to edit:")
        print()
        
        # Get list of colour keys (exclude deprecated ones)
        keys = [k for k in self.colour_keys.keys() if k.startswith('!')]
        
        options = []
        for key in sorted(keys):
            current_value = self.colour_keys[key]
            # Show preview of current colours
            options.append({
                'key': key,
                'label': f"{key:20} - {current_value}",
                'icon': '🎨'
            })
        
        result = self.menu.show_numbered_menu(
            title="Colour Keys",
            options=options,
            allow_back=True,
            allow_quit=True
        )
        
        if result in ['back', 'quit']:
            return None
        
        return result
    
    def _select_edit_type(self, colour_key: str) -> Optional[str]:
        """Select whether to edit foreground or background."""
        print()
        self.logger.colour_log("!info", f"Editing colour key: {colour_key}")
        
        current_value = self.colour_keys[colour_key]
        parts = current_value.split('|')
        fg = parts[0] if len(parts) > 0 else "WHITE"
        bg = parts[1] if len(parts) > 1 else "BLACK"
        
        self.logger.colour_log("!info", f"Current: Foreground={fg}, Background={bg}")
        print()
        
        options = [
            {'key': 'foreground', 'label': f'Foreground (currently: {fg})', 'icon': '🔤'},
            {'key': 'background', 'label': f'Background (currently: {bg})', 'icon': '🎨'}
        ]
        
        result = self.menu.show_numbered_menu(
            title="Edit Foreground or Background?",
            options=options,
            allow_back=True
        )
        
        if result == 'back':
            return None
        
        return result
    
    def _select_colour_with_arrows(self, colour_key: str, edit_type: str) -> Optional[str]:
        """Arrow-key navigable colour selector."""
        current_value = self.colour_keys[colour_key]
        parts = current_value.split('|')
        current_fg = parts[0] if len(parts) > 0 else "WHITE"
        current_bg = parts[1] if len(parts) > 1 else "BLACK"
        
        # Determine which colour to use for display background
        if edit_type == 'foreground':
            display_bg = current_bg
            editing_text = "foreground"
        else:
            display_fg = current_fg
            editing_text = "background"
        
        selected_index = 0
        
        print()
        self.logger.colour_log("!info", f"Choose new {editing_text} colour for ", colour_key, f" colour key.")
        self.logger.colour_log("!info", "Use ↑↓ arrow keys to navigate, Enter to select, Esc to cancel.")
        print()
        
        while True:
            # Clear previous display (move cursor up)
            if selected_index > 0 or True:  # First time or any navigation
                # Clear screen area
                print('\033[2J\033[H', end='')  # Clear screen and move to top
                
                print()
                self.logger.colour_log("!info", f"Choose new {editing_text} colour for {colour_key} colour key.")
                self.logger.colour_log("!info", "Use ↑↓ arrow keys to navigate, Enter to select, Esc to cancel.")
                print()
            
            # Display colour options
            for i, colour in enumerate(self.available_colours):
                marker = "(*)" if i == selected_index else f"({i+1})"
                
                # Create colour display
                if edit_type == 'foreground':
                    # Show colour as foreground with current background
                    if display_bg:
                        colour_code = self.colour_manager.colour_fstr(colour, f"BG_{display_bg}", f"{colour:20}")
                    else:
                        colour_code = self.colour_manager.colour_fstr(colour, f"{colour:20}")
                else:
                    # Show colour as background with current foreground
                    colour_code = self.colour_manager.colour_fstr(display_fg, f"BG_{colour}", f"{colour:20}")
                
                print(f"{marker:4} {colour_code}")
            
            # Get keyboard input
            key = msvcrt.getch()
            
            # Handle special keys (arrow keys send 2 bytes)
            if key == b'\xe0' or key == b'\x00':  # Special key prefix
                key = msvcrt.getch()
                
                if key == b'H':  # Up arrow
                    selected_index = max(0, selected_index - 1)
                elif key == b'P':  # Down arrow
                    selected_index = min(len(self.available_colours) - 1, selected_index + 1)
            
            elif key == b'\r':  # Enter
                return self.available_colours[selected_index]
            
            elif key == b'\x1b':  # Escape
                return None
    
    def _apply_colour_change(self, colour_key: str, edit_type: str, new_colour: str):
        """Apply the colour change and save to file."""
        current_value = self.colour_keys[colour_key]
        parts = current_value.split('|')
        fg = parts[0] if len(parts) > 0 else "WHITE"
        bg = parts[1] if len(parts) > 1 else "BLACK"
        
        if edit_type == 'foreground':
            fg = new_colour
        else:
            bg = new_colour
        
        new_value = f"{fg}|{bg}"
        
        # Confirm before saving
        print()
        self.logger.colour_log("!info", f"Saving to: {self.colours_path}")
        self.logger.colour_log("!info", f"Change: {colour_key} from {current_value} to {new_value}")
        
        if not self.menu.confirm("Save this change?", default=True):
            self.logger.colour_log("!warn", "⚠️  Change cancelled")
            return
        
        # Update in memory
        self.colours_data["COLOUR_KEY"][colour_key] = new_value
        
        # Save to file
        with open(self.colours_path, 'w') as f:
            json.dump(self.colours_data, f, indent=4)
        
        self.logger.colour_log("!done", f"✅ Updated {colour_key} to: {new_value}")
        self.logger.colour_log("!save", "Saved to:", "!path", str(self.colours_path))
        
        # Show preview
        print()
        self.logger.colour_log("!info", "Preview:")
        test_text = f"This is {colour_key} colour"
        self.logger.colour_log(colour_key, test_text)
        print()
    
    def _import_colour_keys(self):
        """Import colour keys from another COLOURS.json file."""
        print()
        self.logger.colour_log("!info", "Import colour keys from another file")
        
        # Browse for source file
        source_dir = self.menu.browse_directory(
            start_path=Path.cwd(),
            title="Navigate to directory containing source COLOURS.json"
        )
        
        if source_dir is None:
            return
        
        source_path = source_dir / "COLOURS.json"
        
        if not source_path.exists():
            self.logger.colour_log("!error", f"❌ COLOURS.json not found at: {source_path}")
            return
        
        try:
            # Load source file
            with open(source_path, 'r') as f:
                source_data = json.load(f)
            
            source_keys = source_data.get("COLOUR_KEY", {})
            
            if not source_keys:
                self.logger.colour_log("!error", "❌ No colour keys found in source file")
                return
            
            self.logger.colour_log("!info", f"Found {len(source_keys)} colour keys in source file")
            
            # Ask merge or replace
            options = [
                {'key': 'merge', 'label': f'Merge (keep existing, add new)', 'icon': '🔀'},
                {'key': 'replace', 'label': f'Replace all (overwrite existing)', 'icon': '♻️'}
            ]
            
            import_mode = self.menu.show_numbered_menu(
                title="Import Mode",
                options=options,
                allow_back=True
            )
            
            if import_mode == 'back':
                return
            
            # Confirm
            if not self.menu.confirm(f"Import from {source_path}?", default=False):
                self.logger.colour_log("!warn", "⚠️  Import cancelled")
                return
            
            # Perform import
            if import_mode == 'replace':
                self.colours_data["COLOUR_KEY"] = source_keys.copy()
                self.colour_keys = self.colours_data["COLOUR_KEY"]
            else:  # merge
                self.colours_data["COLOUR_KEY"].update(source_keys)
                self.colour_keys = self.colours_data["COLOUR_KEY"]
            
            # Save
            with open(self.colours_path, 'w') as f:
                json.dump(self.colours_data, f, indent=4)
            
            self.logger.colour_log("!done", f"✅ Imported {len(source_keys)} colour keys")
            self.logger.colour_log("!save", "Saved to:", "!path", str(self.colours_path))
            
        except Exception as e:
            self.logger.colour_log("!error", f"❌ Import failed: {e}")
    
    def _export_colour_keys(self):
        """Export colour keys to a new file."""
        print()
        self.logger.colour_log("!info", "Export colour keys to new file")
        
        # Browse for destination directory
        dest_dir = self.menu.browse_directory(
            start_path=Path.cwd(),
            title="Navigate to destination directory",
            allow_creation=True
        )
        
        if dest_dir is None:
            return
        
        dest_path = dest_dir / "COLOURS.json"
        
        # Warn if file exists
        if dest_path.exists():
            if not self.menu.confirm(f"File exists at {dest_path}. Overwrite?", default=False):
                self.logger.colour_log("!warn", "⚠️  Export cancelled")
                return
        
        try:
            # Export entire COLOURS.json
            with open(dest_path, 'w') as f:
                json.dump(self.colours_data, f, indent=4)
            
            self.logger.colour_log("!done", f"✅ Exported colour keys")
            self.logger.colour_log("!save", "Saved to:", "!path", str(dest_path))
            
        except Exception as e:
            self.logger.colour_log("!error", f"❌ Export failed: {e}")
    
    def _switch_file(self):
        """Switch to editing a different COLOURS.json file."""
        print()
        self.logger.colour_log("!info", "Switch to different COLOURS.json file")
        
        # Browse for new file
        new_dir = self.menu.browse_directory(
            start_path=Path.cwd(),
            title="Navigate to directory containing COLOURS.json"
        )
        
        if new_dir is None:
            return
        
        new_path = new_dir / "COLOURS.json"
        
        if not new_path.exists():
            self.logger.colour_log("!error", f"❌ COLOURS.json not found at: {new_path}")
            return
        
        # Confirm switch
        if not self.menu.confirm(f"Switch to {new_path}?", default=True):
            return
        
        try:
            # Load new file
            with open(new_path, 'r') as f:
                self.colours_data = json.load(f)
            
            self.colours_path = new_path
            self.colour_keys = self.colours_data.get("COLOUR_KEY", {})
            
            self.logger.colour_log("!done", f"✅ Switched to: {self.colours_path}")
            
        except Exception as e:
            self.logger.colour_log("!error", f"❌ Failed to load file: {e}")


def main():
    """Entry point for colour key editor (standalone mode)."""
    logger = get_logger()
    menu = get_cli_menu_handler()
    
    # Ask which file to edit
    logger.apply_border(
        text="🎨 Colour Key Editor - File Selection",
        pattern={"TOP": "=", "BOTTOM": "=", "LEFT": " ", "RIGHT": " "},
        total_length=60,
        border_rainbow=True
    )
    
    options = [
        {'key': 'default', 'label': 'tUilKit default (src/tUilKit/config/COLOURS.json)', 'icon': '📦'},
        {'key': 'browse', 'label': 'Browse for COLOURS.json file', 'icon': '📁'},
        {'key': 'current', 'label': 'Current directory (./config/COLOURS.json)', 'icon': '📂'}
    ]
    
    choice = menu.show_numbered_menu(
        title="Select COLOURS.json file to edit",
        options=options,
        allow_quit=True
    )
    
    if choice == 'quit':
        return
    
    colours_path = None
    
    if choice == 'default':
        colours_path = Path(__file__).parent.parent / "config" / "COLOURS.json"
    elif choice == 'browse':
        selected_path = menu.browse_directory(
            start_path=Path.cwd(),
            title="Navigate to directory containing COLOURS.json"
        )
        if selected_path:
            colours_path = selected_path / "COLOURS.json"
    elif choice == 'current':
        colours_path = Path.cwd() / "config" / "COLOURS.json"
    
    if colours_path is None or not colours_path.exists():
        logger.colour_log("!error", f"❌ COLOURS.json not found at: {colours_path}")
        return
    
    # Run editor
    try:
        editor = ColourKeyEditor(colours_path=colours_path)
        editor.run()
    except FileNotFoundError as e:
        logger.colour_log("!error", f"❌ {e}")
    except Exception as e:
        logger.colour_log("!error", f"❌ Error: {e}")


if __name__ == "__main__":
    main()
