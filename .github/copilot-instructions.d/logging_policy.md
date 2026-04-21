# Logging Policy

Purpose
- Defines what must be logged, which log files receive each entry, how log file types behave,
  and which colour keys should be used for each category of event.
- Applies to all projects in `Core/` and `Applications/`.
- Agents must follow these rules when writing or reviewing any code that produces log output.

---

## 1. Mandatory Log Targets

Every tUilKit project must define a `LOG_FILES` dictionary in its primary config JSON under an
`INIT` section (or equivalent top-level key).  At minimum, three log file paths are required:

| Key        | Filename convention     | Purpose                                      |
|------------|-------------------------|----------------------------------------------|
| `MASTER`   | contains `MASTER`       | Archival, append-only, never deleted         |
| `SESSION`  | contains `SESSION`      | Overwritten at main entry-point startup      |
| `RUNTIME`  | contains `RUNTIME`      | Same as SESSION but may also be overwritten at regular intervals or natural execution stages |

Additional log files (e.g. `TRY`, `FS`, `INIT`) are strongly recommended and described below.

### 1.1 Log File Lifecycle Rules (file-name-based)

A file's name determines its overwrite behaviour — this must be honoured by every entry point:

- **`MASTER`** — Never overwritten or deleted.  Every entry logged anywhere in the app must
  also be appended to this file.  It is the single source of truth for the full run history.

- **`SESSION`** — Overwritten (truncated) once when `main()` is entered.  All entries logged
  anywhere in that session must also be written to this file.

- **`RUNTIME`** — Same as SESSION for the initial overwrite.  An additional overwrite may
  occur at regular time intervals or at natural execution stage boundaries (e.g. between
  major pipeline steps).

- **`TRY`** — Receives all test runs, assertions, and try-block entries.  Stage-based or
  interval-based overwriting is permitted (same semantics as RUNTIME).

### 1.2 Cascading Write Rule

Every log entry must be written to **all** applicable files simultaneously, not just the most
specific one.  Minimum required cascade:

```
Any log entry  →  SESSION  +  MASTER  (and RUNTIME if active)
```

Pass `log_files=list(LOG_FILES.values())` (or at minimum `[LOG_FILES["SESSION"], LOG_FILES["MASTER"]]`)
to every `colour_log` / `log_exception` call unless deliberately scoping to a sub-log.

---

## 2. What to Log and Where

### 2.1 Configuration Init / Load (`!proc` → INIT log)

All `ConfigLoader` initialisation, instantiation, and `load_config()` calls **must** be
ColourLogged to both the terminal and the INIT log file path defined in the project config.
Use `!proc` for the action and `!file` for the config file name.

```python
logger.colour_log(
    "!proc", "Initializing config loader",
    log_files=[LOG_FILES["SESSION"], LOG_FILES["MASTER"], LOG_FILES.get("INIT", "")]
)
config_loader = get_config_loader()
config = config_loader.load_config("PROJECT_CONFIG")
logger.colour_log(
    "!done", "Config loaded:", "!file", "PROJECT_CONFIG.json",
    log_files=[LOG_FILES["SESSION"], LOG_FILES["MASTER"], LOG_FILES.get("INIT", "")]
)
```

### 2.2 Individual Config Reads (`!data` → CONFIG_READ log)

Individual `config.get()` calls should be logged using `!info` / `!data` pairs.  If a module
makes many sequential reads they may be summarised into a single log entry.  Route to the
`CONFIG_READ` log when defined, in addition to SESSION and MASTER.

```python
value = config.get("SOME_KEY", "default")
logger.colour_log(
    "!info", "Config read:", "!data", "SOME_KEY", "!info", "→", "!data", str(value),
    log_files=[LOG_FILES["SESSION"], LOG_FILES["MASTER"], LOG_FILES.get("CONFIG_READ", "")]
)
```

### 2.3 File System Operations (`!proc` / `!done` / `!error` → FS log)

Every file system operation (read, write, copy, move, delete, mkdir, validate) must be logged.
Use `!path` for full paths and `!file` for bare filenames.  Route to the `FS` log when defined.

```python
logger.colour_log(
    "!proc", "Writing file:", "!path", str(output_path),
    log_files=[LOG_FILES["SESSION"], LOG_FILES["MASTER"], LOG_FILES.get("FS", "")]
)
# … operation …
logger.colour_log(
    "!done", "✅ File written:", "!file", output_path.name,
    log_files=[LOG_FILES["SESSION"], LOG_FILES["MASTER"], LOG_FILES.get("FS", "")]
)
```

### 2.4 Caught Exceptions (`!error` / `!warn` → ERROR log)

All caught exceptions must be logged.  Use `!error` for unrecoverable or unexpected failures
and `!warn` for handled/recoverable conditions.  Always use `logger.log_exception()` so the
full traceback is preserved.  Route to an `ERROR` log when defined.

```python
try:
    risky_operation()
except FileNotFoundError as e:
    logger.log_exception(
        "File not found during operation", e,
        log_files=[LOG_FILES["SESSION"], LOG_FILES["MASTER"], LOG_FILES.get("ERROR", "")]
    )
except Exception as e:
    logger.colour_log(
        "!warn", "⚠️  Recoverable error:", "!data", str(e),
        log_files=[LOG_FILES["SESSION"], LOG_FILES["MASTER"], LOG_FILES.get("ERROR", "")]
    )
```

### 2.5 Test / Assertion / Try Blocks (`!test` / `!pass` / `!fail` → TRY log)

All test runs, assertions, and try-block entries must be logged to the `TRY` log (when defined)
in addition to SESSION and MASTER.  See `building_tests_policy.md` for full test output format.

---

## 3. Timestamps

**Every log entry must include a timestamp.**  Use `!date` for the timestamp token:

```python
from datetime import datetime

ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
logger.colour_log(
    "!date", ts, "!proc", "Starting backup...",
    log_files=list(LOG_FILES.values())
)
```

Alternatively, configure the logger to prepend timestamps automatically if the tUilKit logger
supports it, so callers do not need to inject them manually.

---

## 4. INFO_DISPLAY Modes

Projects may define an `INFO_DISPLAY` key in their primary config JSON with one of:
`VERBOSE`, `BASIC`, or `MINIMAL`.

| Mode      | Terminal output           | File output (SESSION/MASTER) |
|-----------|---------------------------|------------------------------|
| `VERBOSE` | All categories logged     | All entries to at least SESSION, MASTER, and any relevant sub-log (INIT, FS, CONFIG_READ, ERROR, TRY) |
| `BASIC`   | Key events only (INIT, errors, done) | SESSION + MASTER only |
| `MINIMAL` | Errors and completion only | SESSION + MASTER only |

- `VERBOSE` is the **default** mode and must always log to at least SESSION, MASTER, and any
  active sub-log.  Never suppress entries in VERBOSE mode.
- Agents must read `INFO_DISPLAY` from config early in `main()` and pass it to logging helpers
  so output can be gated appropriately.

---

## 5. Colour Key Quick Reference for Logging Categories

| Category                   | Primary key | Secondary / value key | Notes |
|----------------------------|-------------|------------------------|-------|
| ConfigLoader init/load     | `!proc`     | `!file`                | Target INIT log |
| Config key reads           | `!info`     | `!data`                | Target CONFIG_READ log |
| File system operations     | `!proc`     | `!path` / `!file`      | Target FS log |
| FS success                 | `!done`     | `!file`                | |
| FS failure                 | `!error`    | `!path`                | Target ERROR log |
| Caught exception (error)   | `!error`    | `!data`                | Use `log_exception()` |
| Caught exception (warn)    | `!warn`     | `!data`                | |
| Test / assertion           | `!test`     | `!pass` / `!fail`      | Target TRY log |
| Timestamps                 | `!date`     | —                      | Include in all entries |
| Objects / class names      | `!text`     | —                      | Emphasised label |
| Variable names / symbols   | `!data`     | —                      | Cyan |
| Integer / numeric values   | `!int`      | —                      | |
| Full file paths            | `!path`     | —                      | Light Cyan |
| Path components / folders  | `!thisfolder` | —                    | Blue |
| Bare file names            | `!file`     | —                      | Light Blue |

For a full list of colour keys and usage examples see
`.github/copilot-instructions.d/colour_key_usage.md`.

### 5.1 Composite Path Colouring

Full file paths contain multiple components, each with its own key.  When displaying a path
in context, break it into parts:

```python
# e.g. /home/user/projects/myapp/logFiles/SESSION.log
logger.colour_log(
    "!info",       "Log path:",
    "!path",       "/home/user/projects/myapp/",
    "!thisfolder", "logFiles/",
    "!file",       "SESSION.log",
    log_files=list(LOG_FILES.values())
)
```

Or use `logger.colour_path()` to auto-highlight the final folder/file component:

```python
coloured = logger.colour_path(path, highlight_last_folder=True, colour_key="!path")
logger.colour_log("!info", "Path:", coloured, log_files=list(LOG_FILES.values()))
```

---

## 6. Recommended LOG_FILES Config Block

Include this block (or an equivalent) in the primary `PROJECT_CONFIG.json`:

```json
{
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
  "INFO_DISPLAY": "VERBOSE"
}
```

Projects may omit sub-logs they do not need, but MASTER and SESSION are always required.

---

## References

- Colour key definitions: `.github/copilot-instructions.d/colour_key_usage.md`
- tUilKit app guidelines: `.github/copilot-instructions.d/tuilkit_enabled_apps_guidelines.md`
- Test logging: `.github/copilot-instructions.d/building_tests_policy.md`
- Root modes / log paths: `.github/copilot-instructions.d/root_modes_workspace_project_paths.md`

---
Last updated: 2026-04-18
