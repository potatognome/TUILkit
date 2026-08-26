# tUilKit/utils/cli_menus.py
"""
Implementation of CLIMenuInterface for building interactive command-line menus.
"""

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable

try:
    import yaml
except Exception:  # pragma: no cover - optional dependency fallback
    yaml = None

# Add the base directory of the project to the system path
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..\\..\\'))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from tUilKit.interfaces.cli_menu_interface import CLIMenuInterface
from tUilKit.interfaces.logger_interface import LoggerInterface
from tUilKit.utils.output import Logger, ColourManager
from tUilKit.utils.config import ConfigLoader
from tUilKit.factories import get_logger


class _FallbackLogger:
    def apply_border(self, text, pattern, total_length=60, border_rainbow=False, **kwargs):
        top = str(pattern.get("TOP", "="))
        bottom = str(pattern.get("BOTTOM", "="))
        print(top * total_length)
        print(text)
        print(bottom * total_length)

    def colour_log(self, *args, **kwargs):
        parts = [str(part) for part in args if not str(part).startswith("!")]
        print(" ".join(parts))


@dataclass
class MenuObject:
    key: str
    name: str
    icon: str = ""
    colourstring: str = "!info"
    position: Optional[str] = None
    order: int = 100
    parent: Optional[str] = None
    children: List[str] = field(default_factory=list)
    description: str = ""
    visibilityMode: str = "visible"
    visibilityCondition: Optional[str] = None
    visibilityDependencies: List[str] = field(default_factory=list)
    enableMode: str = "enabled"
    enableCondition: Optional[str] = None
    enableDependencies: List[str] = field(default_factory=list)
    reserved: bool = False

    @classmethod
    def from_dict(cls, raw: Dict[str, Any]) -> "MenuObject":
        return cls(
            key=str(raw.get("key", "")).strip(),
            name=str(raw.get("name", raw.get("label", ""))).strip(),
            icon=str(raw.get("icon", "")).strip(),
            colourstring=str(raw.get("colourstring", "!info")).strip() or "!info",
            position=raw.get("position"),
            order=int(raw.get("order", 100)),
            parent=raw.get("parent"),
            children=list(raw.get("children", []) or []),
            description=str(raw.get("description", "")),
            visibilityMode=str(raw.get("visibilityMode", "visible")).strip(),
            visibilityCondition=raw.get("visibilityCondition"),
            visibilityDependencies=list(raw.get("visibilityDependencies", []) or []),
            enableMode=str(raw.get("enableMode", "enabled")).strip(),
            enableCondition=raw.get("enableCondition"),
            enableDependencies=list(raw.get("enableDependencies", []) or []),
            reserved=bool(raw.get("reserved", False)),
        )


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
        if logger is not None:
            self.logger = logger
        else:
            try:
                self.logger = get_logger()
            except Exception:
                self.logger = _FallbackLogger()
        try:
            self.config_loader = ConfigLoader()
            self.config = self.config_loader.global_config
        except Exception:
            self.config_loader = None
            self.config = {}
        self.log_files = self.config.get("LOG_FILES", {})
        roots = self.config.get("ROOTS", {}) if isinstance(self.config.get("ROOTS", {}), dict) else {}
        self.workspace_root = Path(str(roots.get("WORKSPACE", Path.cwd()))).resolve()
        canonical_menu_root = self.workspace_root / "config" / "project.menus"
        legacy_menu_root = self.workspace_root / "projects.menus"
        if canonical_menu_root.exists():
            self.menu_root = canonical_menu_root
        else:
            self.menu_root = legacy_menu_root
        self.menu_registry: Dict[str, Dict[str, Any]] = {
            "menu_types": {},
            "menu_items": {},
        }

    def _resolve_tenant_root(self, tenant: str) -> Path:
        """Resolve where tenant menu files live.

        Supports both:
        - `<menu_root>/<tenant>/...` (legacy tenant folder layout)
        - `<menu_root>/...` (canonical flat project.menus layout)
        """
        tenant_root = self.menu_root / tenant
        if tenant_root.exists() and tenant_root.is_dir():
            return tenant_root
        return self.menu_root

    def _load_menu_payload(self, root: Path, name: str) -> Dict[str, Any]:
        """Load a menu payload supporting dash/underscore naming variants."""
        candidates = [
            root / f"{name}.yaml",
            root / f"{name.replace('_', '-')}.yaml",
            root / f"{name.replace('-', '_')}.yaml",
        ]
        for path in candidates:
            data = self._load_yaml_file(path)
            if data:
                return data
        return {}

    def _load_yaml_file(self, path: Path) -> Dict[str, Any]:
        if not path.exists():
            return {}
        text = path.read_text(encoding="utf-8-sig")
        if yaml is not None:
            loaded = yaml.safe_load(text) or {}
            return loaded if isinstance(loaded, dict) else {}
        return {}

    def _evaluate_visibility(self, item: MenuObject, context: Optional[Dict[str, Any]]) -> bool:
        if item.visibilityMode == "invisible":
            return False
        if item.visibilityMode == "always":
            return True
        context = context or {}
        if item.visibilityCondition and not bool(context.get(item.visibilityCondition, False)):
            return False
        for dep in item.visibilityDependencies:
            if not bool(context.get(dep, False)):
                return False
        return True

    def _evaluate_enablement(self, item: MenuObject, context: Optional[Dict[str, Any]]) -> bool:
        if item.enableMode in {"disabled", "off"}:
            return False
        if item.enableMode == "always":
            return True
        context = context or {}
        if item.enableCondition and not bool(context.get(item.enableCondition, False)):
            return False
        for dep in item.enableDependencies:
            if not bool(context.get(dep, False)):
                return False
        return True

    def _inject_reserved_entries(self, items: List[MenuObject], is_main_menu: bool) -> List[MenuObject]:
        reserved: List[MenuObject] = []
        if is_main_menu:
            reserved.append(
                MenuObject(
                    key="quit",
                    name="Quit Application",
                    icon="🚪",
                    colourstring="!warn",
                    order=0,
                    reserved=True,
                )
            )
            # q/Q remains reserved but invisible from visual index.
            reserved.append(
                MenuObject(
                    key="__reserved_q__",
                    name="Quit alias",
                    icon="",
                    colourstring="!warn",
                    order=0,
                    reserved=True,
                    visibilityMode="invisible",
                )
            )
        else:
            reserved.extend([
                MenuObject(
                    key="back",
                    name="Back",
                    icon="↩️",
                    colourstring="!warn",
                    order=0,
                    reserved=True,
                ),
            ])

        non_reserved = [item for item in items if not item.reserved]
        return [*reserved, *non_reserved]

    def _sort_items(self, items: List[MenuObject]) -> List[MenuObject]:
        return sorted(
            items,
            key=lambda item: (0 if item.reserved else 1, int(item.order), item.name.lower()),
        )

    def load_menu_tree(self, tenant: str) -> Dict[str, Any]:
        tenant_root = self._resolve_tenant_root(tenant)
        menu_tree = self._load_menu_payload(tenant_root, "menu_tree")
        menu_items = self._load_menu_payload(tenant_root, "menu_items")
        overrides = self._load_menu_payload(tenant_root, "registry-overrides")
        conditions = self._load_menu_payload(tenant_root, "conditions")

        self.menu_registry["menu_types"][tenant] = overrides.get("menu_types", {})
        self.menu_registry["menu_items"][tenant] = menu_items.get("items", {})

        return {
            "tenant": tenant,
            "menu_tree": menu_tree,
            "menu_items": menu_items,
            "overrides": overrides,
            "conditions": conditions,
        }

    def render_tenant_menu_tree(
        self,
        tenant: str,
        *,
        menu_key: str = "main",
        auto_mode: bool = False,
    ) -> Optional[str]:
        """Load a tenant DSL tree from .workspace/projects.menus and render it."""
        payload = self.load_menu_tree(tenant)
        tree = payload.get("menu_tree", {})
        item_map = payload.get("menu_items", {}).get("items", {})
        conditions = payload.get("conditions", {}).get("conditions", {})

        menus = tree.get("menus", []) if isinstance(tree.get("menus", []), list) else []
        menu = next((m for m in menus if str(m.get("key", "")) == menu_key), None)
        if not menu:
            # Compatibility aliases across older tenant DSL variants.
            aliases = {
                "selection": "project_selection",
                "project_selection": "selection",
            }
            alt_key = aliases.get(menu_key)
            if alt_key:
                menu = next((m for m in menus if str(m.get("key", "")) == alt_key), None)
        if not menu:
            # Fallback: try direct flat menu file (e.g. selection.yaml) from the
            # resolved menu root when menu-tree lacks the requested key.
            tenant_root = self._resolve_tenant_root(tenant)
            flat = self._load_menu_payload(tenant_root, menu_key)
            flat_items = flat.get("items", []) if isinstance(flat.get("items", []), list) else []
            if not flat_items:
                # Silent miss: callers can provide their own fallback UI.
                return None
            return self.render_menu_object_model(
                title=str(flat.get("title", menu_key)).strip() or "Menu",
                items=flat_items,
                context=conditions,
                is_main_menu=bool(flat.get("is_main_menu", False)),
                auto_mode=auto_mode or bool(conditions.get("auto_mode", False)),
            )

        items = []
        for key in menu.get("items", []):
            if key in item_map:
                items.append(item_map[key])

        return self.render_menu_object_model(
            title=str(menu.get("name", menu_key)).strip() or "Menu",
            items=items,
            context=conditions,
            is_main_menu=bool(menu.get("is_main_menu", False)),
            auto_mode=auto_mode or bool(conditions.get("auto_mode", False)),
        )

    def render_menu_object_model(
        self,
        title: str,
        items: List[Dict[str, Any]],
        *,
        context: Optional[Dict[str, Any]] = None,
        is_main_menu: bool = True,
        auto_mode: bool = False,
    ) -> Optional[str]:
        typed = [MenuObject.from_dict(item) for item in items]
        typed = self._inject_reserved_entries(typed, is_main_menu=is_main_menu)
        typed = self._sort_items(typed)

        visible_items = [item for item in typed if self._evaluate_visibility(item, context)]
        enabled_items = [item for item in visible_items if self._evaluate_enablement(item, context)]

        if auto_mode:
            non_reserved = [item for item in enabled_items if not item.reserved]
            if len(non_reserved) == 1:
                return non_reserved[0].key

        print()
        self.logger.apply_border(
            text=title,
            pattern={"TOP": "=", "BOTTOM": "=", "LEFT": " ", "RIGHT": " "},
            total_length=60,
            border_rainbow=True,
        )
        print()

        index_map: Dict[str, str] = {}
        non_reserved_idx = 0
        for item in enabled_items:
            if item.key == "__reserved_q__":
                continue

            if item.key in {"quit", "back", "cancel"}:
                display_index = "0"
            else:
                non_reserved_idx += 1
                display_index = str(non_reserved_idx)
            index_map[display_index] = item.key

            self.logger.colour_log(
                "!list", display_index,
                item.colourstring if item.colourstring.startswith("!") else "!info",
                f". {item.icon} {item.name}".strip(),
            )

        choice = input("\nSelect option: ").strip()
        choice_lower = choice.lower()

        # Invisible reserved quit/back aliases.
        if choice_lower in {"q", "quit"}:
            return "quit"
        if choice_lower in {"back", "cancel"}:
            return choice_lower

        return index_map.get(choice_lower) or index_map.get(choice)
    
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
        menu_objects: List[Dict[str, Any]] = []
        for index, option in enumerate(options, start=1):
            menu_objects.append(
                {
                    "key": option.get("key", f"option_{index}"),
                    "name": option.get("name", option.get("label", f"Option {index}")),
                    "icon": option.get("icon", "📋"),
                    "colourstring": option.get("colourstring", "!info"),
                    "position": option.get("position", "body"),
                    "order": option.get("order", index),
                    "parent": option.get("parent"),
                    "children": option.get("children", []),
                    "description": option.get("description", ""),
                    "visibilityMode": option.get("visibilityMode", "visible"),
                    "visibilityCondition": option.get("visibilityCondition"),
                    "visibilityDependencies": option.get("visibilityDependencies", []),
                    "enableMode": option.get("enableMode", "enabled"),
                    "enableCondition": option.get("enableCondition"),
                    "enableDependencies": option.get("enableDependencies", []),
                }
            )

        selected = self.render_menu_object_model(
            title,
            menu_objects,
            is_main_menu=allow_quit and not allow_back,
            auto_mode=bool(option.get("auto_mode", False) if options else False),
        )

        if selected in {"quit", "back", "cancel"}:
            if selected == "cancel" and allow_back:
                return "back"
            return selected

        if selected is None:
            self.logger.colour_log("!error", "❌ Invalid input")
        return selected
    
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
