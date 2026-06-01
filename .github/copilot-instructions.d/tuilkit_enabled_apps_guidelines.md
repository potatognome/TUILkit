# Building tUilKit-Enabled Apps (Guidelines & Policies)

Purpose
- Standardized guidelines for creating and maintaining applications that use tUilKit as their core utility framework.
- Aligns app behavior with current Prismata workspace policy for config, paths, shared assets, and logging.
- Applies to active projects under `Core/` and `Applications/`.

## Core Principles

**Interface-First Design**
- Always use tUilKit factory functions: `get_logger()`, `get_config_loader()`, `get_colour_manager()`, `get_file_system()`.
- Never instantiate utility classes directly (e.g., avoid `Logger()`, use `get_logger()` instead).
- Interfaces allow for easy testing, mocking, and future implementation swaps.

**Separation of Concerns**
- Configuration: External JSON/YAML files in `config/` directory.
- Logging: Centralized using tUilKit logger with `LOG_FILES` dictionary.
- Business logic: Separate from I/O and presentation layers.
- CLI menus: Modular functions that can be tested independently.

**Config-Driven Path Resolution**
- Resolve paths using `ROOTS`, `ROOT_MODES`, and `PATHS` from the app primary config.
- Do not hardcode absolute machine-specific paths in runtime code.
- Use tUilKit loaders and utilities instead of ad hoc path construction whenever available.

**Single Workspace Shared Config Source**
- The Prismata ecosystem uses one shared config directory:
  - `.workspace/.projects_config/GLOBAL_SHARED.d/`
- Every tUilKit-enabled app must expose this through:
  - `PATHS["GLOBAL_SHARED.d"] = ".workspace/.projects_config/GLOBAL_SHARED.d/"`
- Do not rely on per-project `SHARED_CONFIG` entries in primary config files.
- Per-project optional overrides remain in each app's `ALT_CONFIG.d`.

**Deterministic Outputs**
- All logging should use colour codes (`!info`, `!error`, etc.) for consistency.
- Test outputs should be reproducible and comparable.
- Avoid timestamps in test output comparisons unless explicitly testing time-based functionality.

## Project Structure Template

```
ProjectName/
├── config/
│   ├── PROJECT_CONFIG.json      # Main configuration
│   ├── ALT_CONFIG.d/            # Optional app-local overrides
│   └── devices.d/               # Optional: device-specific configs
├── docs/
│   ├── README.md                # User-facing overview and usage
│   ├── CHANGELOG.md             # Versioned release notes
│   └── ROADMAP.md               # Planning and priorities
├── logFiles/
│   ├── SESSION.log              # Runtime session log
│   └── MASTER.log               # Persistent master log
├── src/
│   └── ProjectName/
│       ├── __init__.py
│       ├── main.py              # Entry point with CLI menu
│       ├── proc/                # Processing modules
│       └── utils/               # Utility modules
├── tests/
│   ├── testInputData/           # Test input files
│   ├── testOutputLogs/          # Expected output logs
│   └── test_*.py                # Test modules
├── pyproject.toml               # Package metadata and dependencies
└── requirements.txt             # Optional, if project uses pip workflow
```

Workspace-level shared config location (outside app folders):

```
Prismata/
└── .workspace/
  └── .projects_config/
    └── GLOBAL_SHARED.d/
      ├── COLOURS.json
      ├── BORDER_PATTERNS.json
      ├── OUTPUT_PREFS.json
      └── ...
```

## Initialization Pattern

Every module should follow this initialization pattern:

```python
#!/usr/bin/env python3
"""
module_name.py
Brief description of module purpose
"""

import sys
from pathlib import Path
from tUilKit import get_logger, get_config_loader, get_file_system

# Initialize logger and utilities
logger = get_logger()
config_loader = get_config_loader()
file_system = get_file_system()

# Define log files for this module
LOG_FILES = {
    "SESSION": "logFiles/SESSION.log",
    "MASTER": "logFiles/MASTER.log"
}

# Module constants from config
try:
    config = config_loader.load_config("PROJECT_CONFIG")
    MODULE_SETTING = config.get("module_setting", "default_value")
except Exception as e:
    logger.log_exception("Failed to load config", e, log_files=list(LOG_FILES.values()))
    MODULE_SETTING = "default_value"
```

  Recommended shared bundle access pattern:

  ```python
  from pathlib import Path

  workspace_root = Path(config.get("ROOTS", {}).get("WORKSPACE", Path.cwd()))
  global_shared_rel = config.get("PATHS", {}).get("GLOBAL_SHARED.d", "")

  global_shared_dir = (workspace_root / global_shared_rel).resolve() if global_shared_rel else None
  if global_shared_dir:
    colours_path = global_shared_dir / "COLOURS.json"
  ```

## Configuration Best Practices

**Config File Structure**
- Use descriptive top-level keys (UPPERCASE for sections).
- Provide sensible defaults.
- Version your config schema if it may change.
- Keep `ROOTS`, `ROOT_MODES`, and `PATHS` explicit and complete.
- Keep `GLOBAL_SHARED.d` in `PATHS`; keep per-project optional overrides in `ALT_CONFIG.d`.
- Do not add `SHARED_CONFIG` blocks to active primary configs.

Example:
```json
{
  "PROJECT_INFO": {
    "name": "ProjectName",
    "version": "1.0.0",
    "description": "Project description"
  },
  "LOG_FILES": {
    "MASTER":      "logFiles/MASTER.log",
    "SESSION":     "logFiles/SESSION.log",
    "RUNTIME":     "logFiles/RUNTIME.log",
    "TRY":         "logFiles/TRY.log",
    "INIT":        "logFiles/INIT.log",
    "FS":          "logFiles/FS.log",
    "CONFIG_READ": "logFiles/CONFIG_READ.log",
    "ERROR":       "logFiles/ERROR.log"
  },
  "ROOTS": {
    "WORKSPACE": "C:/Repository/Daniel/dev_local/Prismata"
  },
  "ROOT_MODES": {
    "CONFIG": "project",
    "LOGS": "project",
    "OUTPUTS": "project"
  },
  "PATHS": {
    "GLOBAL_SHARED.d": ".workspace/.projects_config/GLOBAL_SHARED.d/",
    "ALT_CONFIG.d": "config/ALT_CONFIG.d/"
  },
  "INFO_DISPLAY": "VERBOSE",
  "OPTIONS": {
    "verbose": true,
    "dry_run": false
  }
}
```

**Loading Configuration**
```python
config_loader = get_config_loader()
config = config_loader.load_config("PROJECT_CONFIG")

# Extract with defaults
log_files = config.get("LOG_FILES", {
    "SESSION": "logFiles/SESSION.log",
    "MASTER": "logFiles/MASTER.log"
})

# Use throughout module
LOG_FILES = log_files
```

## Error Handling

**Always Use logger.log_exception()**
```python
try:
    risky_operation()
except Exception as e:
    logger.log_exception("Operation failed", e, log_files=list(LOG_FILES.values()))
    # Handle gracefully or re-raise
```

**Validation Pattern**
```python
# Validate inputs early
if not file_system.validate_path(input_path):
    logger.colour_log("!error", "Invalid path:", "!path", input_path, 
                     log_files=list(LOG_FILES.values()))
    return False

# Create necessary directories
file_system.validate_and_create_folder("output/results")
```

## CLI Application Structure

**Main Entry Point**
- Use a `main()` function as the entry point.
- Provide a menu-driven interface for user interaction.
- See `.github/copilot-instructions.d/cli_menu_patterns.md` for detailed menu patterns.
- For V4l1d8r-style apps, use shared menu helpers (`_display_header`, `_print_options`) and the standard icon set (`📂 ✅ 🏗️ 💾 🚪 ◀`).
- Keep snippet tools and global toggles under a Settings menu; reserve Main menu for top-level navigation.
- On startup, log resolved root-mode and effective shared-config path values.

**Argument Parsing**
```python
import argparse

def main():
    parser = argparse.ArgumentParser(description="Project description")
    parser.add_argument("--config", help="Custom config file")
    parser.add_argument("--dry-run", action="store_true", help="Preview without executing")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Use args to modify behavior
    if args.verbose:
        logger.colour_log("!info", "Verbose mode enabled")
```

## Logging Strategy

**LOG_FILES Dictionary**
- Define at module level for easy reference.
- Always include SESSION and MASTER at minimum.
- Recommended additional logs: INIT, FS, CONFIG_READ, ERROR, TRY, RUNTIME.
- See `.github/copilot-instructions.d/logging_policy.md` for the full recommended config block.

```python
LOG_FILES = config_loader.global_config.get("LOG_FILES", {
    "SESSION": "logFiles/SESSION.log",
    "MASTER":  "logFiles/MASTER.log",
})
```

**Log File Lifecycle (name-based rules)**
- `MASTER`: append-only, never deleted — receives every entry logged anywhere.
- `SESSION`: overwritten once at `main()` entry — receives every entry logged that session.
- `RUNTIME`: same as SESSION plus optional mid-run overwrites at stage boundaries.
- `TRY`: receives all test/assertion/try-block entries; stage or interval overwrites permitted.
- All other sub-logs (INIT, FS, CONFIG_READ, ERROR) are supplemental and never replace
  the SESSION + MASTER cascade.

**INFO_DISPLAY Mode**
- Projects define `INFO_DISPLAY` in their primary config JSON: `VERBOSE`, `BASIC`, or `MINIMAL`.
- `VERBOSE` (default): log all categories to terminal and all relevant log files.
- `BASIC`: key events only (INIT, errors, done) → SESSION + MASTER.
- `MINIMAL`: errors and completion only → SESSION + MASTER.
- Read `INFO_DISPLAY` early in `main()` and gate output accordingly.

**ConfigLoader Initialization — always ColourLogged**
- All `ConfigLoader` instantiation and `load_config()` calls must be logged using `!proc` /
  `!file` keys to both the terminal and the INIT log path from config.
- Individual `config.get()` reads use `!info` / `!data` pairs and route to CONFIG_READ log.

**Colour Logging**
- See `.github/copilot-instructions.d/colour_key_usage.md` for comprehensive colour key guidance.
- See `.github/copilot-instructions.d/logging_policy.md` for per-category colour key mapping.
- Use semantic colour codes (`!info`, `!error`, `!done`, etc.).
- Avoid plain `print()` statements in production code.
- Always include a `!date` timestamp token in every log entry.
- For menu/status labels with icons, keep icon semantics consistent with `cli_menu_patterns.md`.

## Import Strategy

**Standard tUilKit Imports**
- See `.github/copilot-instructions.d/tuilkit_imports.md` for detailed import guidelines.
- Use factory functions from `tUilKit` package.
- Import specific utilities only when needed.
- Prefer interface/factory entry points for config resolution so root-mode and workspace policies stay centralized.

**Package vs Local Imports**
```python
# Production code: assume tUilKit is installed
from tUilKit import get_logger, get_config_loader

# Test code: use local src imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from tUilKit.utils.output import Logger
```

## Testing Integration

- Follow `.github/copilot-instructions.d/building_examples_policy.md` for supplementary example test structure.
- Use tUilKit utilities in tests for consistency.
- Compare logged output against expected output in `tests/testOutputLogs/`.

## Deployment with H3l3n

H3l3n is the preferred scaffolding and migration workflow for tUilKit-enabled projects.

**Creating a New Project with H3l3n**
1. Run H3l3n scaffolding script.
2. H3l3n creates project structure with tUilKit integration.
3. Customize configuration files in `config/`.
4. Implement business logic in `src/` modules.
5. Write tests following the testing policy.

**Retrofitting Existing Projects**
1. Stage project in an active workspace migration/staging area (for example under `Applications/REFACTOR/` or another approved repo-local staging folder).
2. Run H3l3n retrofit workflow.
3. Update imports to use tUilKit factories.
4. Add configuration files.
5. Migrate logging to tUilKit logger.
6. Migrate config keys to current policy:
  - keep `PATHS.GLOBAL_SHARED.d`
  - keep per-project `ALT_CONFIG.d`
  - remove primary-config `SHARED_CONFIG`
7. Add tests and verify output.

## Version Control

**pyproject.toml Requirements**
```toml
[project]
name = "project-name"
version = "1.0.0"
requires-python = ">=3.11"
dependencies = [
  "tUilKit>=0.6.0",
]
```

**Git Practices**
- Commit message format: `feat: description` or `fix: description` or `docs: description`.
- Include tUilKit version in dependencies.
- Update CHANGELOG.md with each release.

## Common Patterns

**File Operations**
```python
file_system = get_file_system()

# Create directory if needed
file_system.validate_and_create_folder("output/data")

# Validate path exists
if not file_system.validate_path(input_file):
    logger.colour_log("!error", "File not found:", "!path", input_file)
    return
```

**Configuration with Fallbacks**
```python
config = config_loader.load_config("PROJECT_CONFIG")

# Multi-level fallback
setting = (
    config.get("SECTION", {}).get("setting") or 
    config.get("DEFAULTS", {}).get("setting") or 
    "hardcoded_default"
)
```

**Shared Config Resolution (GLOBAL_SHARED.d First)**
```python
from pathlib import Path

config = config_loader.load_config("PROJECT_CONFIG")
roots = config.get("ROOTS", {})
paths = config.get("PATHS", {})

workspace_root = Path(roots.get("WORKSPACE", Path.cwd()))
global_shared_rel = paths.get("GLOBAL_SHARED.d", "")
alt_config_rel = paths.get("ALT_CONFIG.d", "config/ALT_CONFIG.d/")

global_shared_dir = (workspace_root / global_shared_rel).resolve() if global_shared_rel else None
alt_config_dir = (Path.cwd() / alt_config_rel).resolve()

# Load order: workspace shared first, then app ALT overrides.
```

## References

- tUilKit import guidelines: `.github/copilot-instructions.d/tuilkit_imports.md`
- CLI menu patterns: `.github/copilot-instructions.d/cli_menu_patterns.md`
- Colour key usage: `.github/copilot-instructions.d/colour_key_usage.md`
- Logging policy: `.github/copilot-instructions.d/logging_policy.md`
- Testing policy: `.github/copilot-instructions.d/building_examples_policy.md`
- Root modes and path policy: `.github/copilot-instructions.d/root_modes_workspace_project_paths.md`

---
Last updated: 2026-05-27
