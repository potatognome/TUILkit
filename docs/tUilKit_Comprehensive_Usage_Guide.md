# tUilKit Comprehensive Usage Guide

## Overview

tUilKit is a modular Python toolkit providing utility functions for logging, colour management, file system operations, configuration loading, and dataframe manipulation. The package is structured around clear interfaces for easy extension and testing.

---

## Key Principles & Best Practices

- **Interface-first, factory-driven:** Always use provided interfaces and factory functions for initialization and extension.
- **Config-driven:** All log/config paths, colour keys, and border patterns are externalized in JSON configs. Avoid hardcoding paths or colour codes.
- **Colour-aware logging:** Use COLOUR_KEY consistently for semantic, visually distinct logs.
- **Docstring coverage:** All public methods should have clear docstrings describing purpose, parameters, and output.
- **Testing:** Ensure robust test coverage, including error handling, config overrides, and edge cases. Use per-test logs and verify log outputs.
- **Refactoring:** Regularly review for legacy code and consolidate repeated logic into shared utilities.

---

## Quick Start: Initializing tUilKit

### Factory Initialization (Recommended)

```python
from tUilKit import get_logger, get_file_system, get_config_loader

logger = get_logger()          # builds ConfigLoader + ColourManager under the hood
file_system = get_file_system()  # shares logger + config
config_loader = get_config_loader()
```

### Direct Initialization (Advanced)

```python
from tUilKit.utils.output import Logger, ColourManager
from tUilKit.utils.fs import FileSystem
from tUilKit.utils.config import ConfigLoader

config_loader = ConfigLoader()
colour_config = config_loader.load_colour_config()
colour_manager = ColourManager(colour_config)
log_files = config_loader.global_config.get("LOG_FILES", {})
logger = Logger(colour_manager, log_files=log_files)
file_system = FileSystem(logger, log_files=log_files)
```

See also: [ColourKey Usage Guide](ColourKey_Usage_Guide.md) and [FileSystem Usage Guide](FileSystem_Usage_Guide.md) for focused references.

---

## Config Standard (Current)

tUilKit path and config resolution is driven by these sections in `config/tUilKit_CONFIG.json`:

- `ROOTS`: base roots such as `PROJECT` and `WORKSPACE`
- `ROOT_MODES`: mode switches such as `CONFIG`, `LOGS`, and test roots
- `PATHS`: relative folders under the selected roots
- `SHARED_CONFIG`: shared config folder and file mappings (for example `GLOBAL_SHARED.d/COLOURS.json`)

When `ROOT_MODES.CONFIG` is set to `workspace`, config lookups resolve from the workspace root first; when set to `project`, lookups resolve from the project root first.

---

## The 4 Primary Interfaces

### 1. LoggerInterface (Logger Class)

**Purpose**: Coloured logging, terminal output, and border printing with selective file routing.

**Most Used Methods**:
- `colour_log(*args, category="default", log_files=None, log_to="both")` - Main logging method with colour codes
- `log_exception(description, exception, category="error")` - Log exceptions with formatting
- `log_done(log_files=None)` - Log completion messages
- `apply_border(text, pattern, total_length=None)` - Create bordered text sections

**Docstring Example:**
```python
def colour_log(self, *args, category="default", log_files=None, log_to="both"):
  """
  Log messages with colour formatting and category-based routing.
  Args:
    *args: Message parts, can include COLOUR_KEY codes.
    category: Log category or list of categories.
    log_files: Optional override for log file dict.
    log_to: 'console', 'file', or 'both'.
  Returns:
    None
  """
```

**Example**:
```python
# Basic coloured logging
logger.colour_log("!info", "Processing", "!int", 42, "!file", "items")

# Exception logging
try:
    risky_operation()
except Exception as e:
    logger.log_exception("Operation failed", e)

# Multi-category logging (new feature)
logger.colour_log("!info", "File system error occurred", category=["fs", "error"])

# Advanced: Selective and Multi-Category Logging
logger.colour_log("!warn", "Security alert", category="security")
logger.colour_log("!error", "Disk space low", category=["fs", "error"])
```

### 2. ColourInterface (ColourManager Class)

**Purpose**: Colour formatting and ANSI code management for terminal output.

**Most Used Methods**:
- `colour_fstr(*args, bg=None, separator=" ")` - Format strings with colours
- `colour_path(path)` - Format file paths with appropriate colours
- `interpret_codes(text)` - Replace colour codes in text strings
- `strip_ansi(fstring)` - Remove ANSI codes from strings

**Example**:
```python
# Format text with colours
coloured_text = colour_manager.colour_fstr("!info", "File", "!file", "data.txt", "!done", "loaded")

# Format file paths
path_display = colour_manager.colour_path("/home/user/documents/file.txt")

# Use in logging
logger.colour_log("!load", "Loaded configuration from", "!path", config_path)
```

### 3. FileSystemInterface (FileSystem Class)

**Purpose**: File and folder operations with integrated logging.

**Most Used Methods**:
- `validate_and_create_folder(folder_path, category="fs")` - Create folders safely
- `no_overwrite(filepath, max_count=None, category="fs")` - Generate non-conflicting filenames
- `backup_and_replace(full_path, backup_path, category="fs")` - Backup and clear files
- `sanitize_filename(filename)` - Clean filenames of invalid characters
- `get_all_files(folder)` - List files in directory

**Example**:
```python
# Create folder with logging
file_system.validate_and_create_folder("output/data", category="fs")

# Generate unique filename
safe_filename = file_system.no_overwrite("results.csv")

# Backup existing file
file_system.backup_and_replace("data.txt", "data_backup.txt")
```

### 4. ConfigLoaderInterface (ConfigLoader Class)

**Purpose**: Configuration loading and path resolution.

**Most Used Methods**:
- `get_json_path(filename, cwd=False)` - Get full path to config files
- `load_config(json_file_path)` - Load JSON configuration
- `ensure_folders_exist(file_system)` - Create necessary folders for logging

**Example**:
```python
# Load configuration
config_path = config_loader.get_json_path("MY_CONFIG.json")
config = config_loader.load_config(config_path)

# Ensure log folders exist
config_loader.ensure_folders_exist(file_system)
```

## DataFrameInterface (SmartDataFrameHandler Class)

**Purpose**: DataFrame operations with intelligent column handling.

**Most Used Methods**:
- `merge(df_list, merge_type="outer", config_loader=None, logger=None)` - Smart DataFrame merging
- `compare(df1, df2)` - Compare DataFrames ignoring row order

**Docstring Example:**
```python
def merge(self, df_list, merge_type="outer", config_loader=None, logger=None):
  """
  Merge multiple DataFrames with intelligent column handling.
  Args:
    df_list: List of pandas DataFrames.
    merge_type: Merge strategy ('outer', 'inner', etc.).
    config_loader: Optional ConfigLoader for column mapping.
    logger: Optional Logger for operation logging.
  Returns:
    Merged DataFrame
  """
```

**Example**:
```python
from tUilKit.utils.sheets import SmartDataFrameHandler

df_handler = SmartDataFrameHandler()

# Merge DataFrames with logging
result = df_handler.merge([df1, df2, df3], logger=logger)

# Compare DataFrames
differences = df_handler.compare(df1, df2)
```

## Configuration Files and Dictionaries

### JSON Configuration Files

tUilKit uses several JSON configuration files located in `src/tUilKit/config/`:

1. **`COLOURS.json`** - Colour definitions and COLOUR_KEY mappings
2. **`GLOBAL_CONFIG.json`** - Global settings and log file paths
3. **`BORDER_PATTERNS.json`** - Border patterns for terminal formatting
4. **`COLUMN_MAPPING.json`** - DataFrame column mapping for merging

### Using COLOUR_KEY

The `COLOUR_KEY` in `COLOURS.json` defines colour mappings for different types of output. Each key maps to a colour definition in the format `"FOREGROUND|BACKGROUND"` or just `"FOREGROUND"`.

**Common COLOUR_KEY Usage**:

```json
{
  "COLOUR_KEY": {
    "!info": "LIGHT GREY|BLACK",
    "!error": "RED|BLACK",
    "!file": "ROSE|BLACK",
    "!path": "LAVENDER|BLACK",
    "!done": "GREEN|BLACK"
  }
}
```

**In Code**:
```python
# Use colour keys in logging
logger.colour_log("!info", "Processing", "!file", filename, "!done", "complete")

# Troubleshooting: If colour codes do not appear, check COLOURS.json and ensure your terminal supports ANSI codes.

# Direct colour formatting
coloured = colour_manager.colour_fstr("!error", "Error:", "!text", message)
```

### Dictionary Modules

Located in `src/tUilKit/dict/`:

1. **`DICT_COLOURS.py`** - RGB ANSI escape code definitions
2. **`DICT_CODES.py`** - ANSI escape code components

These provide the foundation for colour management and are used internally by ColourManager.

---

## Advanced Features

### Multi-Category Logging

Log to multiple categories simultaneously for complex operations:

```python
# Log filesystem errors to both FS and ERROR logs
logger.colour_log("!error", "Disk space low", category=["fs", "error"])

# File operations can log to multiple categories
file_system.validate_and_create_folder(path, category=["fs", "init"])
```

### Customizing Logging Categories

tUilKit supports easy customization of logging categories through configuration:

#### Method 1: Modify GLOBAL_CONFIG.json (Recommended)

Add custom categories and log files to `src/tUilKit/config/GLOBAL_CONFIG.json`:

```json
{
  "LOG_FILES": {
    "SESSION": "logs/RUNTIME.log",
    "MASTER": "logs/MASTER.log",
    "ERROR": "logs/ERROR.log",
    "FS": "logs/FS.log",
    "INIT": "logs/INIT.log",
    "DEBUG": "logs/DEBUG.log",
    "API": "logs/API.log"
  },
  "LOG_CATEGORIES": {
    "default": ["MASTER", "SESSION"],
    "error": ["ERROR", "SESSION", "MASTER"],
    "fs": ["MASTER", "SESSION", "FS"],
    "init": ["INIT", "SESSION", "MASTER"],
    "debug": ["DEBUG", "SESSION"],
    "api": ["API", "SESSION", "MASTER"],
    "all": ["MASTER", "SESSION", "ERROR", "FS", "INIT", "DEBUG", "API"]
  }
}
```

#### Method 2: Runtime Customization

Modify categories programmatically:

```python
# Custom categories at runtime
custom_categories = {
    "security": ["ERROR", "MASTER", "DEBUG"],
    "performance": ["MASTER", "DEBUG"],
    "audit": ["MASTER", "SESSION", "ERROR"]
}

logger = Logger(colour_manager)
logger.LOG_KEYS = custom_categories

# Use custom categories
logger.colour_log("!warn", "Security alert", category="security")
```

#### Method 3: Dynamic Category Creation

Create categories based on runtime conditions:

```python
# Start with base categories
dynamic_categories = {
    "default": ["MASTER", "SESSION"],
    "error": ["ERROR", "SESSION", "MASTER"]
}

# Add categories for available modules
modules = ["auth", "payment", "inventory"]
for module in modules:
    log_key = module.upper()
    logger.log_files[log_key] = f"logs/{module}.log"
    dynamic_categories[module] = ["MASTER", "SESSION", log_key]

logger.LOG_KEYS = dynamic_categories
```

### Selective Logging

Control where logs are written using categories:
- `"default"` → MASTER, SESSION logs
- `"error"` → ERROR, SESSION, MASTER logs
- `"fs"` → FS, SESSION, MASTER logs
- `"init"` → INIT, SESSION, MASTER logs
- **Custom categories** → Any combination you define

### Custom Log Files

Override default log locations:

```python
custom_logs = {
    "SESSION": "/var/log/myapp/session.log",
    "ERROR": "/var/log/myapp/errors.log"
}
logger = Logger(colour_manager, log_files=custom_logs)

---
```

## Best Practices

1. **Always initialize ColourManager first** - Required for Logger
2. **Use appropriate categories** - Helps with log organization
3. **Include logger in DataFrame operations** - Enables operation tracking
4. **Use COLOUR_KEY consistently** - Maintains visual consistency
5. **Handle exceptions with log_exception()** - Proper error formatting

6. **Add/expand docstrings for all public methods** - Improves maintainability and onboarding.
7. **Test error handling and config overrides** - Ensure robust, predictable behavior.
8. **Refactor legacy code and consolidate logic** - Reduce duplication and technical debt.

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
python -m pytest tests/ -v

# Run with log cleanup
python -m pytest tests/test_multi_category.py --clean -v

# Run specific test
python -m pytest tests/test_fs_ops.py::test_validate_and_create_folder -v

# Edge Case Testing
python -m pytest tests/ --tb=short --disable-warnings

# Tips:
- Check log outputs for correct colour and category routing.
- Test with missing/invalid config files to verify error handling.
```

## Integration Example

Complete example showing all components working together:

```python
import os
import json
import pandas as pd
from tUilKit.utils.output import Logger, ColourManager
from tUilKit.utils.fs import FileSystem
from tUilKit.config.config import ConfigLoader
from tUilKit.utils.sheets import SmartDataFrameHandler

# Initialize tUilKit
with open("src/tUilKit/config/COLOURS.json", "r") as f:
    colour_config = json.load(f)

colour_manager = ColourManager(colour_config)
logger = Logger(colour_manager)
config_loader = ConfigLoader()
file_system = FileSystem(logger)
df_handler = SmartDataFrameHandler()

# Use all components
logger.colour_log("!info", "tUilKit initialized", "!done", "ready")

# File operations
output_dir = "output/data"
file_system.validate_and_create_folder(output_dir, category="init")

# DataFrame operations
df1 = pd.DataFrame({"name": ["Alice", "Bob"], "age": [25, 30]})
df2 = pd.DataFrame({"name": ["Charlie", "Diana"], "age": [35, 40]})

merged = df_handler.merge([df1, df2], logger=logger)
logger.colour_log("!info", "Merged", "!int", len(merged), "!data", "rows")

# Troubleshooting & Advanced Usage

# - If logs do not appear in expected files, check LOG_FILES and LOG_CATEGORIES in GLOBAL_CONFIG.json.
# - For custom log routing, update logger.LOG_KEYS or pass custom log_files.
# - For advanced DataFrame merging, provide a COLUMN_MAPPING.json config.

# Refactoring Guidance
# - Regularly review utils for legacy code.
# - Move repeated logic (e.g., log file path resolution) into shared utilities.

# Documentation
# - Expand/maintain docstrings and usage guides as new features are added.
```