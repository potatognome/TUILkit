# tUilKit Colour Key Usage Guide

Purpose
- Comprehensive reference for using tUilKit's colour logging system.
- Semantic colour codes ensure consistent, meaningful output across all applications.
- Covers both terminal display and log file formatting.

## Core Concept

tUilKit uses **semantic colour codes** (e.g., `!data`, `!error`) instead of literal colours (e.g., `RED`, `BLUE`). This provides:
- **Consistency**: Same meaning = same colour across all apps
- **Readability**: Codes describe intent, not appearance
- **Flexibility**: Can change colour schemes without changing code
- **Accessibility**: Can adapt for colour-blind users or high-contrast themes

## Primary Colour Codes (COLOUR_KEY)

### Informational

**`!reset`** - Neutral/default text
- **Use**: Neutral separators, blank lines, punctuation glue between semantic segments

**`!info`** - Deprecated alias of `!reset`
- **Status**: Deprecated
- **Use**: Avoid in new code

**`!data`** - Data values, variables, content
- **Colour**: Cyan
- **Use**: Displaying variable values, user data, configuration values
```python
logger.colour_log("!text", "Version:", "!data", version)
logger.colour_log("!text", "Count:", "!int", str(count))
```

**`!int`** - Integer/numeric values
- **Colour**: Light Blue
- **Use**: Numbers, counts, indices
```python
logger.colour_log("!proc", "Processing item", "!int", str(i), "!reset", "of", "!int", str(total))
```

### Status & Outcomes

**`!done`** - Success, completion, positive state
- **Colour**: Green
- **Use**: Successful operations, enabled status, completion messages
```python
logger.colour_log("!done", "✅ Operation completed successfully")
logger.colour_log("!text", "Status:", "!done", "Active")
```

**`!error`** - Errors, failures, critical issues
- **Colour**: Red
- **Use**: Error messages, failed operations, critical problems
```python
logger.colour_log("!error", "❌ File not found:", "!path", filepath)
logger.colour_log("!error", "Operation failed with code:", "!int", str(error_code))
```

**`!warn`** - Warnings, cautions, attention needed
- **Colour**: Yellow
- **Use**: Non-critical warnings, deprecation notices, user attention
```python
logger.colour_log("!warn", "⚠️  Configuration not found, using defaults")
logger.colour_log("!warn", "This feature is deprecated")
```

### Process & Operations

**`!proc`** - Processing, operations in progress
- **Colour**: Magenta
- **Use**: Operations in progress, processing steps, active tasks
```python
logger.colour_log("!proc", "🔄 Processing files...")
logger.colour_log("!proc", "Initializing system components")
```

**`!test`** - Testing, validation, checks
- **Colour**: Light Magenta
- **Use**: Test execution, validation steps, checks
```python
logger.colour_log("!test", "Running test:", "!int", str(test_num))
logger.colour_log("!test", "Validating configuration...")
```

### Paths & Files

**`!path`** - File paths, directory paths
- **Colour**: Light Cyan
- **Use**: Path labels and prefix text. **Always wrap the path value itself with `colourize_path`** (see below) — never pass a raw path string directly to a `!path` slot.
```python
from tUilKit.utils.fs import colourize_path

# Build colourized path first, then embed in the label string
coloured = colourize_path(str(source_path), logger.Colour_Mgr)
logger.colour_log("!path", f"  Source : {coloured}")
logger.colour_log("!error", "Path not found:", "!path", colourize_path(missing_path, logger.Colour_Mgr))
```

**`!thisfolder`** - Current folder/project name
- **Colour**: Blue
- **Use**: Relative paths, current folder names, project names
```python
logger.colour_log("!info", "Project:", "!thisfolder", project_name)
logger.colour_log("!info", "Folder:", "!thisfolder", folder_name)
```

**`!file`** - File names (without path)
- **Colour**: Light Blue
- **Use**: Individual file names, file references
```python
logger.colour_log("!info", "Reading file:", "!file", "config.json")
```

### Special Purpose

**`!pass`** - Test passed, assertion succeeded
- **Colour**: Bright Green
- **Use**: Test success, assertion pass, validation success
```python
logger.colour_log("!test", "Test", "!int", str(num), "!pass", "PASSED")
```

**`!fail`** - Test failed, assertion failed
- **Colour**: Bright Red
- **Use**: Test failure, assertion failure
```python
logger.colour_log("!test", "Test", "!int", str(num), "!fail", "FAILED")
```

**`!expect`** - Expected values in tests
- **Colour**: Cyan (similar to !data)
- **Use**: Expected values in test comparisons
```python
logger.colour_log("!test", "Expected:", "!expect", expected_value)
logger.colour_log("!test", "Got:", "!data", actual_value)
```

**`!list`** - List item markers, indices
- **Colour**: Yellow
- **Use**: Menu item numbers, list indices
```python
logger.colour_log("!list", "1", "!info", ". First option")
logger.colour_log("!list", "2", "!info", ". Second option")
```

**`!text`** - Emphasized text, headers
- **Colour**: White (bold or emphasized)
- **Use**: Section headers, emphasized content
```python
logger.colour_log("!text", "Configuration Summary:")
```

**`!date`** - Date/time values
- **Colour**: Light Yellow
- **Use**: Timestamps, dates, time values
```python
logger.colour_log("!info", "Modified:", "!date", timestamp)
```

## Extended Colour Codes (COLOUR_KEY_HELP)

Additional codes for special scenarios:

**`!note`** - Notes, comments, asides
- **Use**: Additional information, footnotes

**`!debug`** - Debug information
- **Use**: Debug output, developer information

**`!input`** - User input prompts
- **Use**: Prompting for user input

**`!output`** - Output data, results
- **Use**: Final results, output data

## Log Category → Colour Key Mapping

Use the following keys consistently when logging each category of event.
Full details and lifecycle rules are in `.github/copilot-instructions.d/logging_policy.md`.

| Log Category                  | Primary key | Value / detail key     |
|-------------------------------|-------------|------------------------|
| ConfigLoader init / load      | `!proc`     | `!file`                |
| Config key reads              | `!text`     | `!data`                |
| File system operation (start) | `!proc`     | `!path` / `!file`      |
| File system success           | `!done`     | `!file`                |
| File system failure           | `!error`    | `!path`                |
| Caught exception (error)      | `!error`    | `!data`                |
| Caught exception (warning)    | `!warn`     | `!data`                |
| Test / assertion              | `!test`     | `!pass` / `!fail`      |
| Timestamps                    | `!date`     | —                      |
| Object / class name           | `!text`     | —                      |
| Variable / symbol             | `!data`     | —                      |
| Integer / count               | `!int`      | —                      |
| Full file path                | `!path`     | —                      |
| Path component / folder       | `!thisfolder` | —                    |
| Bare file name                | `!file`     | —                      |

### Composite Path Colouring

**Always use `colourize_path` for any file or directory path displayed to the user.** Raw `str(path)` must not appear in `colour_log` calls.

`colourize_path` normalizes the path and applies semantic colour highlighting via the colour manager:

```python
from tUilKit.utils.fs import colourize_path

# Basic usage
coloured = colourize_path(str(some_path), logger.Colour_Mgr)
logger.colour_log("!path", f"  Config : {coloured}", log_files=lf, time_stamp=True)

# Inline in f-string inside a !path label
logger.colour_log(
    "!path", f"  Source : {colourize_path(str(source), logger.Colour_Mgr)}",
    log_files=lf, time_stamp=True,
)
```

In **V4l1d8r menus** (where `AppContext` is available), use the `_cpath(ctx, path)` helper from `menus/shared.py`.
It combines path relativization (`_rel`) with `colourize_path` in one call:

```python
from .shared import _cpath

# Displays path relative to workspace root, with colour
ctx.logger.colour_log(
    "!path", f"  Config : {_cpath(ctx, project.primary_config_path)}\n",
    log_files=lf, time_stamp=True,
)
ctx.logger.colour_log(
    "!done", f"  Written: {_cpath(ctx, output_file)}",
    log_files=lf, time_stamp=True,
)
```

For lower-level multi-segment path colouring, `logger.colour_path()` can highlight the last segment:

```python
# /home/user/projects/myapp/logFiles/SESSION.log
coloured = logger.colour_path(path, highlight_last_folder=True, colour_key="!path")
logger.colour_log("!path", f"Path: {coloured}", log_files=list(LOG_FILES.values()))
```



### Basic Information Display

```python
logger.colour_log("!proc", "Processing project:", "!thisfolder", project_name)
logger.colour_log("!text", "Version:", "!data", version, "!reset", "|", "!text", "Status:", "!done", "Active")
```

### Error Reporting

```python
logger.colour_log("!error", "❌ Failed to load config file:", "!path", config_path)
logger.log_exception("Configuration load error", exception, log_files=list(LOG_FILES.values()))
```

### Progress Updates

```python
logger.colour_log("!proc", "🔄 Syncing files...")
logger.colour_log("!proc", "Progress:", "!int", str(current), "!reset", "/", "!int", str(total))
logger.colour_log("!done", "✅ Sync complete!")
```

### Menu Display

```python
logger.colour_log("!text", "📋 Main Menu:")
logger.colour_log("!list", "1", "!text", ". 📂 Edit Configuration")
logger.colour_log("!list", "2", "!text", ". 💾 Run Backup")
logger.colour_log("!list", "3", "!text", ". 🚪 Exit")
```

### Test Output

```python
logger.colour_log("!test", "Running test", "!int", "1", "!reset", ":", "!proc", "test_function")
logger.colour_log("!test", "Expected:", "!expect", "expected_value")
logger.colour_log("!test", "Actual:", "!data", "actual_value")
logger.colour_log("!test", "Result:", "!pass", "PASSED")
```

### File Operations

```python
from tUilKit.utils.fs import colourize_path

logger.colour_log("!path", f"  Source     : {colourize_path(str(source), logger.Colour_Mgr)}", log_files=lf)
logger.colour_log("!path", f"  Destination: {colourize_path(str(dest), logger.Colour_Mgr)}", log_files=lf)
logger.colour_log("!info", "Copying file:", "!file", filename, log_files=lf)
logger.colour_log("!done", "✅ File copied successfully", log_files=lf)
```

## Multi-Line Colour Logging

Combine multiple colour codes in a single call:

```python
logger.colour_log(
    "!info", "Processing ",
    "!thisfolder", project_name,
    "!info", " version ",
    "!data", version,
    "!info", " from ",
    "!path", source_path,
    log_files=list(LOG_FILES.values())
)
```

## Special Logger Functions

### Rainbow Row

Visual separator using colour pattern:

```python
logger.print_rainbow_row(pattern="X-O-", spacer=2, log_files=list(LOG_FILES.values()))
```

### Bordered Text

Create bordered headers:

```python
logger.apply_border(
    border_pattern="=",
    text="Configuration Menu",
    total_length=60,
    border_colour="!proc",
    text_colour="!info",
    log_files=list(LOG_FILES.values())
)
```

### Colour Path

**`colourize_path`** from `tUilKit.utils.fs` is the standard function for displaying any path.
It normalizes the path string and applies colour via the colour manager:

```python
from tUilKit.utils.fs import colourize_path

# Signature: colourize_path(path: str, colour_manager, style: str = "auto") -> str
coloured = colourize_path(str(my_path), logger.Colour_Mgr)
logger.colour_log("!path", f"  Output: {coloured}", log_files=list(LOG_FILES.values()))
```

For lower-level control, `logger.colour_path()` exposes the same logic with additional segment options:

```python
coloured_path = logger.colour_path(
    path="/home/user/projects/myproject",
    highlight_last_folder=True,
    colour_key="!path"
)
print(coloured_path)
```

## Logging to Files

Always specify log files when logging important information:

```python
LOG_FILES = {
    "SESSION": "logFiles/SESSION.log",
    "MASTER": "logFiles/MASTER.log"
}

# Log to all files
logger.colour_log("!info", "Message", log_files=list(LOG_FILES.values()))

# Log to specific file
logger.colour_log("!info", "Message", log_files=[LOG_FILES["SESSION"]])

# Log to file and function log
function_log = "logFiles/function_specific.log"
logger.colour_log("!info", "Message", log_files=[LOG_FILES["SESSION"], function_log])
```

## Best Practices

### DO:
- ✅ Use semantic codes (`!info`, `!error`) instead of colour names
- ✅ Be consistent: same meaning = same colour code
- ✅ Combine codes for rich, meaningful output
- ✅ Log to files for persistent records
- ✅ Use `!path` for full path labels, `!thisfolder` for folder names, `!file` for bare filenames
- ✅ **Always wrap path values with `colourize_path(str(path), logger.Colour_Mgr)`** before passing to `colour_log`
- ✅ In V4l1d8r menus, use `_cpath(ctx, path)` which combines relativization + `colourize_path`
- ✅ Use `!done` for success, `!error` for failures, `!warn` for warnings

### DON'T:
- ❌ Don't use `print()` in production code - use `logger.colour_log()`
- ❌ Don't use literal colour names like `RED` or `BLUE`
- ❌ Don't mix plain text with coloured output inconsistently
- ❌ Don't forget to specify log_files for important messages
- ❌ Don't use `!error` for warnings or `!warn` for errors
- ❌ **Don't pass raw `str(path)` or `f"{path}"` directly as a `!path` value** — always use `colourize_path`

## Common Patterns

### Status with Icon and Colour

```python
# Success
logger.colour_log("!done", "✅ Operation completed")

# Error
logger.colour_log("!error", "❌ Operation failed")

# Warning
logger.colour_log("!warn", "⚠️  Attention needed")

# Processing
logger.colour_log("!proc", "🔄 Processing...")

# Info
logger.colour_log("!info", "ℹ️  Information")
```

### Structured Data Display

```python
logger.colour_log("!info", "=" * 60)
logger.colour_log("!text", "Device Information")
logger.colour_log("!info", "=" * 60)
logger.colour_log("!info", "Name:", "!data", device_name)
logger.colour_log("!info", "Hostname:", "!data", hostname)
logger.colour_log("!info", "Path:", "!path", device_path)
logger.colour_log("!info", "Status:", "!done", "Active")
logger.colour_log("!info", "=" * 60)
```

### Comparison Display

```python
logger.colour_log("!test", "Comparing values:")
logger.colour_log("!info", "  Expected:", "!expect", str(expected))
logger.colour_log("!info", "  Actual:", "!data", str(actual))
if expected == actual:
    logger.colour_log("!test", "  Result:", "!pass", "MATCH")
else:
    logger.colour_log("!test", "  Result:", "!fail", "MISMATCH")
```

## Terminal vs File Output

- **Terminal**: ANSI colour codes render as colours
- **Log Files**: Colour codes saved as-is for later interpretation
- **Testing**: Log files can be compared for deterministic output

To strip colour codes (e.g., for plain text):
```python
plain_text = colour_manager.strip_codes(coloured_text)
```

## Accessing Colour Definitions

```python
from tUilKit.dict.colour_definitions import COLOUR_KEY, COLOUR_KEY_HELP

# View all colour codes
for code, colour_name in COLOUR_KEY.items():
    print(f"{code}: {colour_name}")
```

## Examples from Real Projects

### Syncbot Menu
```python
logger.colour_log("!info", "🔄 Syncbot - Project Backup & Sync Utility")
logger.colour_log("!list", "1", "!info", ". 📂 Edit Configuration")
logger.colour_log("!list", "2", "!info", ". 💾 Run Backup Utility")
```

### H3l3n Scaffolding
```python
logger.colour_log("!proc", "🏗️  Creating project structure...")
logger.colour_log("!info", "Creating folder:", "!thisfolder", folder_name)
logger.colour_log("!done", "✅ Project scaffolding complete!")
```

### tUilKit Tests
```python
logger.colour_log("!test", "Test", "!int", "1", "!info", ":", "!proc", "test_colour_manager")
logger.colour_log("!test", "Testing:", "!data", "colour code interpretation")
assert "{RED}" not in result
logger.colour_log("!test", "Result:", "!pass", "PASSED")
```

## References

- Colour definitions: `Projects/tUilKit/src/tUilKit/dict/colour_definitions.py`
- Logger implementation: `Projects/tUilKit/src/tUilKit/utils/output.py`
- CLI menu patterns: `.github/copilot-instructions.d/cli_menu_patterns.md`
- Logging policy (what/where/when to log): `.github/copilot-instructions.d/logging_policy.md`
- Test output: `.github/copilot-instructions.d/building_tests_policy.md`

---
Last updated: 2026-05-01
