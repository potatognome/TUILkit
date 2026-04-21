# CLI Menu Patterns for tUilKit Applications

Purpose
- Standardized patterns for building interactive command-line menus.
- Ensures consistent user experience across all tUilKit-enabled applications.
- Provides reusable templates for common menu scenarios.

## Basic Menu Structure

### Simple Main Menu Template

```python
from tUilKit import get_logger

logger = get_logger()

def main():
    logger = get_logger()
    
    while True:
        print()  # Blank line for spacing
        logger.apply_border(
            text="🔄 Application Name - Description",
            pattern={"TOP": "=", "BOTTOM": "=", "LEFT": " ", "RIGHT": " "},
            total_length=60,
            border_rainbow=True,
            log_files=list(LOG_FILES.values())
        )
        
        print()  # Blank line before menu
        logger.colour_log("!info", "📋 Main Menu:")
        logger.colour_log("!list", "1", "!info", ". 📂 Option One")
        logger.colour_log("!list", "2", "!info", ". 💾 Option Two")
        logger.colour_log("!list", "3", "!info", ". 🔍 Option Three")
        logger.colour_log("!list", "4", "!info", ". ❓ Help")
        logger.colour_log("!list", "5", "!info", ". 🚪 Exit")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == '1':
            print()
            logger.colour_log("!info", "📂 Launching Option One...")
            option_one()
        elif choice == '2':
            print()
            logger.colour_log("!info", "💾 Launching Option Two...")
            option_two()
        elif choice == '3':
            print()
            logger.colour_log("!info", "🔍 Launching Option Three...")
            option_three()
        elif choice == '4':
            print()
            logger.colour_log("!info", "❓ Showing Help...")
            show_help()
        elif choice == '5':
            print()
            logger.colour_log("!done", "👋 Goodbye!")
            break
        else:
            logger.colour_log("!error", "❌ Invalid choice. Please select 1-5.")

if __name__ == "__main__":
    main()
```

## Menu Patterns

### Pattern 1: Numbered List Menu (Recommended)

**Best for:** 5-10 options, clear hierarchy

```python
def show_configuration_menu():
    """Display configuration options"""
    print()
    logger.apply_border(
        text="⚙️ Configuration Menu",
        pattern={"TOP": "=", "BOTTOM": "=", "LEFT": " ", "RIGHT": " "},
        total_length=60,
        border_rainbow=True,
        log_files=list(LOG_FILES.values())
    )
    print()
    logger.colour_log("!list", "1", "!info", ". 🖥️  Edit device profiles")
    logger.colour_log("!list", "2", "!info", ". 📦 Edit repositories")
    logger.colour_log("!list", "3", "!info", ". ⚙️  Edit sync options")
    logger.colour_log("!list", "4", "!info", ". 💾 Save and exit")
    logger.colour_log("!list", "5", "!info", ". 🚪 Exit without saving")
    
    choice = input("\nSelect option (1-5): ").strip()
    return choice
```

### Pattern 2: Lettered Menu

**Best for:** Few options, quick selection

```python
def show_quick_menu():
    """Quick action menu"""
    logger.colour_log("!info", "\n⚡ Quick Actions:")
    logger.colour_log("!info", "  [B] 💾 Backup")
    logger.colour_log("!info", "  [R] 🔄 Restore")
    logger.colour_log("!info", "  [V] 🔍 View")
    logger.colour_log("!info", "  [Q] 🚪 Quit")
    
    choice = input("\nSelect action (B/R/V/Q): ").strip().upper()
    return choice
```

### Pattern 3: Multi-Select Menu

**Best for:** Selecting multiple items from a list

```python
def select_projects(projects):
    """Allow user to select multiple projects"""
    logger.colour_log("!info", "\n📦 Available Projects:")
    
    for i, project in enumerate(projects, 1):
        logger.colour_log("!list", str(i), "!info", ". 📂 ", "!thisfolder", project)
    
    logger.colour_log("!info", "\nSelect projects (e.g., '1,3,5' or 'all'): ")
    choice = input("Selection: ").strip().lower()
    
    if choice == 'all':
        return projects
    
    try:
        indices = [int(x.strip()) for x in choice.split(',')]
        return [projects[i-1] for i in indices if 1 <= i <= len(projects)]
    except (ValueError, IndexError):
        logger.colour_log("!error", "❌ Invalid selection")
        return []
```

### Pattern 4: Hierarchical/Nested Menus

**Best for:** Complex applications with sub-menus

```python
def main_menu():
    """Main menu with sub-menus"""
    while True:
        print()
        loggtext="📋 Main Menu",
            pattern={"TOP": "=", "BOTTOM": "=", "LEFT": " ", "RIGHT": " "},
            total_length=60,
            border_rainbow=Trueenu",
            total_length=60,
            log_files=list(LOG_FILES.values())
        )
        print()
        logger.colour_log("!list", "1", "!info", ". ⚙️  Configuration ➡️")
        logger.colour_log("!list", "2", "!info", ". 🔧 Tools ➡️")
        logger.colour_log("!list", "3", "!info", ". ❓ Help ➡️")
        logger.colour_log("!list", "4", "!info", ". 🚪 Exit")
        
        choice = input("\nSelect: ").strip()
        
        if choice == '1':
            configuration_submenu()  # Calls another menu function
        elif choice == '2':
            tools_submenu()
        elif choice == '3':
            help_submenu()
        elif choice == '4':
            break

def configuration_submenu():
    """Configuration sub-menu"""
    while True:
        print()
        loggtext="⚙️ Configuration",
            pattern={"TOP": "=", "BOTTOM": "=", "LEFT": " ", "RIGHT": " "},
            total_length=60,
            border_rainbow=Trueuration",
            total_length=60,
            log_files=list(LOG_FILES.values())
        )
        print()
        logger.colour_log("!list", "1", "!info", ". 🖥️  Devices")
        logger.colour_log("!list", "2", "!info", ". 📦 Repositories")
        logger.colour_log("!list", "3", "!info", ". 🔙 Back")
        
        choice = input("\nSelect: ").strip()
        
        if choice == '1':
            edit_devices()
        elif choice == '2':
            edit_repositories()
        elif choice == '3':
            break  # Return to main menu
```

## Icon Usage Guidelines

### Common Menu Icons

**Navigation & Actions**
- 📋 Main menu / List
- ⚙️ Settings / Configuration
- 🔧 Tools / Utilities
- 🔍 Search / Browse / View
- ❓ Help / Information
- 🚪 Exit / Quit
- 🔙 Back / Return
- ➡️ Submenu indicator

**Data & Files**
- 📂 Folder / Directory
- 📁 File / Document
- 📦 Package / Archive / Backup
- 💾 Save / Backup operation
- 🔄 Sync / Refresh / Restore
- 📊 Data / Reports / Analysis

**Status Indicators**
- ✅ Enabled / Success / Available
- ❌ Disabled / Failed / Error
- ⚠️ Warning / Attention needed
- 🔴 Critical / Important
- 🟢 Active / Running
- 🟡 Pending / In progress

**Devices & Systems**
- 🖥️ Desktop / Computer / Device
- 💻 Laptop
- 🖨️ Server
- 📱 Mobile / Portable
- 👑 Primary / Master
- 🔧 Secondary / Backup

**Special Actions**
- ➕ Add / Create new
- ➖ Remove / Delete
- ✏️ Edit / Modify
- 🗑️ Delete / Trash
- 📝 Note / Description
- 🏷️ Tag / Label

### Icon Consistency Example (Syncbot)

```python
# Main menu
logger.colour_log("!list", "1", "!info", ". 📂 Edit Configuration")
logger.colour_log("!list", "2", "!info", ". 💾 Run Backup Utility")
logger.colour_log("!list", "3", "!info", ". 🔄 Run Restore Utility")
logger.colour_log("!list", "4", "!info", ". 🔍 Browse Project Versions")
logger.colour_log("!list", "5", "!info", ". ❓ Help - Configuration & Options")
logger.colour_log("!list", "6", "!info", ". 🚪 Exit")

# Configuration submenu
logger.colour_log("!list", "1", "!info", ". 🖥️  Edit device profiles")
logger.colour_log("!list", "2", "!info", ". 📦 Edit repository profiles")
logger.colour_log("!list", "3", "!info", ". ⚙️  Edit sync options")
logger.colour_log("!list", "4", "!info", ". 💾 Save and exit")
logger.colour_log("!list", "5", "!info", ". 🚪 Exit without saving")

# Device list with status
for i, (device_id, device_data) in enumerate(devices.items(), 1):
    status = "✅" if device_data.get("enabled") else "❌"
    role_icon = "👑" if role == "primary" else "🔧"
    logger.colour_log("!info", f"  {i}. {role_icon} {device_id} {status}")
```

## Border Patterns for Headers

### Rainbow Border (Recommended Default)

Use rainbow borders for main headers to create visual appeal and separation:

```python
loggtext="🔄 Application Name",
    pattern={"TOP": "=", "BOTTOM": "=", "LEFT": " ", "RIGHT": " "},
    total_length=60,
    border_rainbow=True,
    log_files=list(LOG_FILES.values())
)
```

### Custom Color Borders

For specific contexts, you can use colored borders:

```python
# Success/completion header
logger.apply_border(
    text="✅ Operation Complete",
    pattern={"TOP": "=", "BOTTOM": "=", "LEFT": " ", "RIGHT": " "},
    total_length=60,
    border_colour="!done",
    text_colour="!done",
    log_files=list(LOG_FILES.values())
)

# Error/warning header
logger.apply_border(
    text="⚠️ Warning",
    pattern={"TOP": "=", "BOTTOM": "=", "LEFT": " ", "RIGHT": " "},
    total_length=60,
    border_colour="!warn",
    text_colour="!warn",
    log_files=list(LOG_FILES.values())
)

# Processing/active header
logger.apply_border(
    text="🔄 Processing",
    pattern={"TOP": "=", "BOTTOM": "=", "LEFT": " ", "RIGHT": " "},
    total_length=60,
    border_colour="!proc",
    text_colour="!info",
    log_files=list(LOG_FILES.values())
)
```

### Border Pattern Dictionary

The `pattern` parameter defines the border characters:

```python
pattern = {
    "TOP": "=",      # Top border character(s)
    "BOTTOM": "=",   # Bottom border character(s)
    "LEFT": " ",     # Left side character(s)
    "RIGHT": " "     # Right side character(s)
}
```

Common pattern examples:
```python
# Simple equals
{"TOP": "=", "BOTTOM": "=", "LEFT": " ", "RIGHT": " "}

# Hash/pound
{"TOP": "#", "BOTTOM": "#", "LEFT": " ", "RIGHT": " "}

# Asterisks
{"TOP": "*", "BOTTOM": "*", "LEFT": " ", "RIGHT": " "}

# Decorative
{"TOP": "═", "BOTTOM": "═", "LEFT": "║", "RIGHT": "║"}
```

### Apply Border Parameters

```python
logger.apply_border(
    text="Header Text",                    # Required: Text to display
    pattern={...},                          # Required: Border pattern dict
    total_length=60,                        # Optional: Total width (default: fits text)
    border_colour="!proc",                  # Optional: Single color for borders
    text_colour="!info",                    # Optional: Single color for text
    border_rainbow=True,                    # Optional: Rainbow gradient on borders
    text_rainbow=False,                     # Optional: Rainbow gradient on text
    border_fg_gradient=["RED", "YELLOW"],   # Optional: Custom border gradient
    text_fg_gradient=["BLUE", "CYAN"],      # Optional: Custom text gradient
    justify="center",                       # Optional: left/center/right (default: left)
    log_files=list(LOG_FILES.values())      # Optional: Files to log to
)
```
- Custom pattern - Any character or pattern

## Input Validation Patterns

### Numeric Range Validation

```python
def get_numeric_choice(min_val, max_val, prompt="Select option"):
    """Get validated numeric input within range"""
    while True:
        try:
            choice = input(f"\n{prompt} ({min_val}-{max_val}): ").strip()
            
            if choice.lower() in ['q', 'quit', 'exit', 'back']:
                return None
            
            choice_num = int(choice)
            if min_val <= choice_num <= max_val:
                return choice_num
            else:
                logger.colour_log("!error", f"❌ Please enter {min_val}-{max_val}")
        except ValueError:
            logger.colour_log("!error", "❌ Please enter a valid number")
```

### Yes/No Confirmation

```python
def confirm_action(message, default=False):
    """Get yes/no confirmation from user"""
    default_str = "Y/n" if default else "y/N"
    choice = input(f"\n{message} ({default_str}): ").strip().lower()
    
    if not choice:
        return default
    
    return choice in ['y', 'yes']
```

### List Selection with 'all' Option

```python
def select_from_list(items, item_type="item"):
    """Select one, multiple, or all items from a list"""
    logger.colour_log("!info", f"\n📋 Available {item_type}s:")
    
    for i, item in enumerate(items, 1):
        logger.colour_log("!list", str(i), "!info", f". {item}")
    
    while True:
        choice = input(f"\nSelect {item_type} (1-{len(items)}) or 'all': ").strip().lower()
        
        if choice == 'all':
            return items
        
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(items):
                return [items[choice_num - 1]]
            else:
                logger.colour_log("!error", f"❌ Please enter 1-{len(items)} or 'all'")
        except ValueError:
            logger.colour_log("!error", "❌ Invalid input")
```

## Display Patterns

### Table/List Display

```python
def display_items_with_status(items):
    """Display items with version and status"""
    logger.colour_log("!info", "\n📦 Items:")
    logger.colour_log("!info", "=" * 70)
    
    for i, item in enumerate(items, 1):
        version = item.get('version', 'unknown')
        status = "✅" if item.get('active') else "❌"
        
        logger.colour_log(
            "!list", str(i), "!info", ". ",
            "!thisfolder", item['name'], "!info", " (v", "!data", version, "!info", ") ",
            "!done" if item.get('active') else "!warn", status
        )
```

### Progress Indicator

```python
def show_progress(current, total, message="Processing"):
    """Display progress in menu"""
    percentage = (current / total) * 100
    logger.colour_log(
        "!info", f"{message}: ",
        "!int", f"{current}", "!info", "/", "!int", f"{total}",
        "!info", f" ({percentage:.1f}%)"
    )
```

### Section Headers

```python
def display_section_header(title, width=60):
    """Display visually separated section header"""
    loggtext=title,
        pattern={"TOP": "=", "BOTTOM": "=", "LEFT": " ", "RIGHT": " "},
        total_length=width,
        border_rainbow=True
        total_length=width,
        log_files=list(LOG_FILES.values())
    )
    print()
```

## Advanced Patterns

### Menu with Preview/Details

```python
def browse_with_preview(items):
    """Show list, allow selection to view details"""
    while True:
        logger.colour_log("!info", "\n📦 Items:")
        for i, item in enumerate(items, 1):
            logger.colour_log("!list", str(i), "!info", f". {item['name']}")
        
        logger.colour_log("!info", f"\nSelect item (1-{len(items)}) to view details or 'q' to quit:")
        choice = input("Selection: ").strip().lower()
        
        if choice == 'q':
            break
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(items):
                show_item_details(items[idx])  # Show detailed view
            else:
                logger.colour_log("!error", "❌ Invalid selection")
        except ValueError:
            logger.colour_log("!error", "❌ Invalid input")
```

### Menu State Management

```python
class MenuState:
    """Track menu state for complex workflows"""
    def __init__(self):
        self.current_menu = 'main'
        self.previous_menu = []
        self.context = {}
    
    def navigate_to(self, menu_name, **context):
        """Navigate to a menu, saving previous"""
        self.previous_menu.append(self.current_menu)
        self.current_menu = menu_name
        self.context.update(context)
    
    def go_back(self):
        """Return to previous menu"""
        if self.previous_menu:
            self.current_menu = self.previous_menu.pop()
            return True
        return False
```

## Best Practices

1. **Rainbow Borders**: Use `apply_border` with `"rainbow"` pattern for all main headers.
2. **Consistent Spacing**: Use `print()` for blank lines before/after menus and borders.
3. **Clear Prompts**: Always indicate expected input format and range.
4. **Error Handling**: Validate input and provide clear error messages.
5. **Escape Options**: Always provide 'q', 'quit', or 'back' options.
6. **Visual Hierarchy**: Use icons and colour codes consistently.
7. **Confirmation**: Ask for confirmation before destructive actions.
8. **Status Feedback**: Show what's happening ("Launching...", "Processing...").
9. **Exit Gracefully**: Always provide a clear exit path.

## Complete Example: Multi-Level Menu

See `Applications/Syncbot/src/Syncbot/main.py` for a complete implementation including:
- Main menu with submenu calls
- Configuration editor with nested options
- Help system with topic selection
- Project browser with detail views

## References

- Colour key usage: `.github/copilot-instructions.d/colour_key_usage.md`
- tUilKit logger functions: `Projects/tUilKit/src/tUilKit/utils/output.py`
- Example implementations: `Applications/Syncbot/`, `SuiteTools/H3l3n/`

---
Last updated: 2026-01-21
