# FileSystem Usage Guide

Use `FileSystem` for safe, colour-aware filesystem operations. It is a thin wrapper around `os`/`shutil` with logging hooks and log-category routing from `GLOBAL_CONFIG.json` (`LOG_CATEGORIES`).

## Quick start
```python
from tUilKit import get_logger, get_file_system

logger = get_logger()  # factory builds ConfigLoader, ColourManager, FileSystem
fs = get_file_system(logger)

fs.validate_and_create_folder("logs/run1")
safe_path = fs.no_overwrite("logs/run1/output.txt")
with open(safe_path, "w") as f:
    f.write("hello")
```

## Logging categories
- `category` controls which log files receive entries; default is `"fs"` → keys from `LOG_CATEGORIES` (usually `MASTER`, `SESSION`, `FS`).
- `log_to` controls destination: `"both"` (console + file), `"file"`, or `"console"`.
- Colour keys used: `!try`, `!create`, `!pass`, `!warn`, `!done`, `!path`, `!file`, `!error`.

## Operations
- `validate_and_create_folder(path, log=True, log_to="both", category="fs")` → ensure a folder exists; logs attempt and success; returns `True`/`False`.
- `remove_empty_folders(path, log=True, category="fs")` → recursively remove empty dirs under `path`; logs removals; ignores failures silently unless logging is enabled.
- `get_all_files(folder)` → list file names (non-recursive) in a folder.
- `validate_extension(fullfilepath, extension)` → append `extension` if missing; returns adjusted path.
- `no_overwrite(fullfilepath, max_count=None, log=True, category="fs")` → generate a non-clobbering path by appending `(n)`; if `max_count` hit, returns the oldest existing file and logs `!warn`.
- `backup_and_replace(full_pathname, backup_full_pathname, log=True, category="fs")` → copy `full_pathname` to backup, then truncate the original; logs both steps.
- `sanitize_filename(filename)` → strip/replace invalid characters (`: \ / ? * < > |`) for safe filenames.

## Patterns
- **Safe writes:** call `validate_and_create_folder` → `no_overwrite` → write file.
- **Backups before overwrite:** `backup_and_replace(existing, backup)` prior to writing new content.
- **Cleanup:** `remove_empty_folders(base_path)` after bulk deletes to tidy empty directories.

## Notes
- `FileSystem` auto-loads `LOG_CATEGORIES` via the global `config_loader`; ensure your config defines `LOG_FILES` paths so logs land in real files.
- Keep `.zip` archives out of version control (already ignored by default).