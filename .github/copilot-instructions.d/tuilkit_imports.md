# tUilKit Import Guidelines

Purpose
- Standardized import patterns for using tUilKit across all projects.
- Ensures consistency and prevents common import errors.
- Covers both production and test scenarios.

## Factory Functions (Recommended)

**Primary Import Pattern**
```python
from tUilKit import (
    get_logger,
    get_config_loader,
    get_colour_manager,
    get_file_system,
    get_dataframe_manager
)

# Initialize utilities
logger = get_logger()
config_loader = get_config_loader()
colour_manager = get_colour_manager()
file_system = get_file_system()
df_manager = get_dataframe_manager()
```

**Why Use Factories?**
- Singleton pattern ensures consistent instances across modules.
- Easier to mock and test.
- Future-proof: implementation can change without breaking imports.
- Explicit dependency injection pattern.

## Production Code Imports

**Assumption: tUilKit Installed in Environment**
```python
# Main module imports
from tUilKit import get_logger, get_config_loader, get_file_system

# If you need specific utilities directly (rare)
from tUilKit.utils.output import ColourManager
from tUilKit.utils.file_system import FileSystemManager
```

**When NOT to Import Directly**
- Avoid: `from tUilKit.utils.output import Logger` - use `get_logger()` instead.
- Avoid: Instantiating classes directly like `Logger()` or `ColourManager()`.
- Exception: When you need a second independent instance (very rare).

## Test Code Imports

**Local Source Imports for Tests**
When working in `tests/` folders, use local src imports:

```python
#!/usr/bin/env python3
"""
test_module.py
Test suite for module
"""

import sys
from pathlib import Path

# Add src to path for local development
test_dir = Path(__file__).parent
project_root = test_dir.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Now import from local source
from tUilKit.utils.output import Logger, ColourManager
from tUilKit.utils.file_system import FileSystemManager
from tUilKit.utils.config_loader import ConfigLoader

# Initialize for testing
logger = Logger()
colour_manager = ColourManager()
file_system = FileSystemManager()
config_loader = ConfigLoader()
```

**Why Direct Imports in Tests?**
- Tests should verify the actual implementation classes.
- Allows testing without installed package.
- Easier debugging of source code during development.

## Common Import Patterns by Use Case

### Basic CLI Application

```python
from tUilKit import get_logger, get_config_loader

logger = get_logger()
config_loader = get_config_loader()

LOG_FILES = {
    "SESSION": "logFiles/SESSION.log",
    "MASTER": "logFiles/MASTER.log"
}

def main():
    logger.colour_log("!info", "Application started", log_files=list(LOG_FILES.values()))
    config = config_loader.load_config("APP_CONFIG")
    # ... rest of application
```

### File Processing Application

```python
from tUilKit import get_logger, get_file_system, get_config_loader

logger = get_logger()
file_system = get_file_system()
config_loader = get_config_loader()

LOG_FILES = {"SESSION": "logFiles/SESSION.log", "MASTER": "logFiles/MASTER.log"}

def process_files(input_dir, output_dir):
    # Validate paths
    if not file_system.validate_path(input_dir):
        logger.colour_log("!error", "Input directory not found", log_files=list(LOG_FILES.values()))
        return False
    
    # Create output directory
    file_system.validate_and_create_folder(output_dir)
    # ... process files
```

### DataFrame Application

```python
from tUilKit import get_logger, get_dataframe_manager, get_config_loader
import pandas as pd

logger = get_logger()
df_manager = get_dataframe_manager()
config_loader = get_config_loader()

LOG_FILES = {"SESSION": "logFiles/SESSION.log", "MASTER": "logFiles/MASTER.log"}

def analyze_data(csv_file):
    df = pd.read_csv(csv_file)
    
    # Use dataframe utilities
    logger.colour_log("!info", "Processing dataframe...", log_files=list(LOG_FILES.values()))
    result = df_manager.filter_dataframe(df, conditions)
    # ... analyze data
```

### Colour-Rich Output Application

```python
from tUilKit import get_logger, get_colour_manager

logger = get_logger()
colour_manager = get_colour_manager()

LOG_FILES = {"SESSION": "logFiles/SESSION.log", "MASTER": "logFiles/MASTER.log"}

def display_status():
    # Use colour codes
    logger.colour_log("!info", "Status:", "!done", "Active", 
                     log_files=list(LOG_FILES.values()))
    
    # Use rainbow row for visual separation
    logger.print_rainbow_row(pattern="X-O-", spacer=2, log_files=list(LOG_FILES.values()))
    
    # Use borders for headers
    logger.apply_border("=", "System Report", total_length=60, 
                       border_colour="!proc", text_colour="!info",
                       log_files=list(LOG_FILES.values()))
```

## Advanced Import Patterns

### Submodule-Specific Imports

If you need specific functionality not exposed by factories:

```python
# Colour dictionary utilities
from tUilKit.dict.colour_definitions import COLOUR_KEY_HELP, COLOUR_KEY

# Specific interface imports (for type hints)
from tUilKit.interfaces.logger_interface import LoggerInterface
from tUilKit.interfaces.config_loader_interface import ConfigLoaderInterface

# Use in type hints
def process_with_logger(logger: LoggerInterface, data: dict) -> bool:
    logger.colour_log("!info", "Processing...")
    # ...
```

### Conditional Imports

For optional features or fallbacks:

```python
try:
    from tUilKit import get_dataframe_manager
    df_manager = get_dataframe_manager()
    DATAFRAME_SUPPORT = True
except ImportError:
    DATAFRAME_SUPPORT = False
    logger.colour_log("!warn", "DataFrame support not available")
```

## Package vs Editable Install

**Installed Package** (Production)
```bash
# Install from PyPI (when published)
pip install tUilKit

# Or install local package
pip install /path/to/tUilKit
```

```python
# Imports work from site-packages
from tUilKit import get_logger
```

**Editable Install** (Development)
```bash
# Install in editable mode
cd /path/to/tUilKit
pip install -e .
```

```python
# Imports work, but point to source directory
from tUilKit import get_logger  # Uses src/tUilKit
```

**Local Source** (Testing)
```python
# Manually add to path
import sys
sys.path.insert(0, "/path/to/tUilKit/src")

# Now imports work
from tUilKit import get_logger
```

## Common Import Errors and Solutions

### Error: `ModuleNotFoundError: No module named 'tUilKit'`

**Solutions:**
1. Check tUilKit is installed: `pip list | grep tUilKit`
2. Install if missing: `pip install -e /path/to/tUilKit`
3. Verify virtual environment is activated
4. Check `sys.path` includes tUilKit location

### Error: `ImportError: cannot import name 'get_logger'`

**Solutions:**
1. Verify tUilKit version: `pip show tUilKit`
2. Check `__init__.py` exports the function
3. Try: `from tUilKit.factories import get_logger`

### Error: `AttributeError: module 'tUilKit' has no attribute 'get_logger'`

**Cause:** Circular import or incomplete package initialization

**Solutions:**
1. Check for circular imports in your module
2. Restart Python interpreter
3. Reinstall tUilKit: `pip install -e . --force-reinstall --no-deps`

## Import Checklist for New Modules

- [ ] Use factory functions (`get_logger()`, etc.)
- [ ] Define `LOG_FILES` dictionary after imports
- [ ] Initialize utilities at module level (not in functions)
- [ ] Use local src imports only in `tests/` folder
- [ ] Import from `tUilKit` package in production code
- [ ] Add type hints using interface imports if needed
- [ ] Avoid direct class instantiation

## Examples from Real Projects

### Syncbot (Device-Centric Backup)
```python
from tUilKit import get_logger, get_config_loader
from Syncbot.utils.device_detection import detect_current_device

logger = get_logger()
config_loader = get_config_loader()

LOG_FILES = {
    "SESSION": "logFiles/SESSION.log",
    "MASTER": "logFiles/MASTER.log"
}
```

### H3l3n (Project Scaffolding)
```python
from tUilKit import get_logger, get_file_system, get_config_loader

logger = get_logger()
file_system = get_file_system()
config_loader = get_config_loader()

LOG_FILES = {
    "SESSION": "logFiles/SESSION.log",
    "MASTER": "logFiles/MASTER.log",
    "INIT": "logFiles/INIT.log"
}
```

### tUilKit Tests
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tUilKit.utils.output import Logger, ColourManager
from tUilKit.utils.file_system import FileSystemManager

logger = Logger()
colour_manager = ColourManager()
file_system = FileSystemManager()
```

## References

- tUilKit source: `Projects/tUilKit/src/tUilKit/`
- Factory functions: `Projects/tUilKit/src/tUilKit/factories.py`
- Interfaces: `Projects/tUilKit/src/tUilKit/interfaces/`
- Building tUilKit apps: `.github/copilot-instructions.d/tuilkit_enabled_apps_guidelines.md`

---
Last updated: 2026-01-21
