# Workspace vs Project Root Modes (Config, Logs, Data)

Purpose: define a single agent policy for using alternate workspace-level and
project-level folders for config, logs, and output data.

## Scope

- Applies to all active development areas under `Core/` and
  `Applications/`.
- Applies to runtime code, scripts, tests, docs, and generated files.

## Root Mode Contract

Agents must respect `ROOT_MODES` in app config and never hardcode output roots.

Supported mode values:

- `project`
- `workspace`

Common keys used by projects:

- `ROOT_MODES.LOG_PATHS` (or legacy `ROOT_MODES.LOGS`)
- `ROOT_MODES.TESTS_LOGS`
- `ROOT_MODES.CONFIG`
- `ROOT_MODES.TESTS_CONFIG`
- `ROOT_MODES.OUTPUT_DATA`
- `ROOT_MODES.INPUT_DATA`
- `ROOT_MODES.TESTS_INPUTS`
- `ROOT_MODES.TESTS_OUTPUTS`

If a key is missing, default to `project` behavior.

## Canonical Folders

When mode is `project`, use project-local folders from `PATHS`.

Examples:

- `config/`
- `logFiles/` or `logs/`
- `output/`

When mode is `workspace`, use workspace-level alternate roots.

Examples:

- `.projects_config/`
- `.projects_data/`
- `.logs/`
- `.tests_config/`
- `.tests_logs/`

For workspace-level placement, namespace by application where appropriate.

Examples:

- `.logs/Chromaspace/`
- `.projects_data/Chromaschemes/`

## Required Agent Behavior

- Read app config first; do not assume folder mode.
- Resolve file destinations from config + mode, then create directories if
  needed.
- Use loader/factory utilities where available (for example tUilKit
  `ConfigLoader` and file system utilities) instead of ad hoc path logic.
- Keep logging paths config-driven:
  - Prefer `config_loader.global_config.get("LOG_FILES", {})`.
  - Avoid literal `LOG_FILES` path dictionaries unless there is no configured
    alternative.
- In terminal output for root-mode reports, use semantic root-mode colour keys:
  - `!root_mode` for root-mode labels/headings
  - `!workspace_root_mode` for value `workspace`
  - `!project_root_mode` for value `project`
  - `!workspace` and `!project` for scope labels/values where applicable
- Support `.d` override directories for config loads.
- Preserve deterministic file naming in tests and generated artifacts.

## Path Resolution Guidance

Recommended order for locating config files:

1. Explicit config path provided by the app/tool.
2. Project-level config root.
3. Workspace-level alternate config root.
4. Fail with a clear error if unresolved.

Recommended order for writing logs/data:

1. Mode-directed root (`workspace` or `project`).
2. Project/app namespace under that root.
3. Configured file names from `PATHS` / `LOG_FILES`.

## Tests and Docs Requirements

- If root behavior is changed, update tests to cover both `project` and
  `workspace` modes.
- Update README/changelog notes when root mode behavior changes.
- Ensure test logs and test config follow their dedicated root-mode toggles.

## Anti-Patterns (Do Not Do)

- Do not hardcode absolute machine-specific paths in source.
- Do not write logs directly to project folders when `ROOT_MODES.LOGS` is
  `workspace`.
- Do not bypass config resolution by writing outputs to ad hoc locations.
- Do not ignore alternate workspace folders when they are enabled.

---
Last updated: 2026-05-01
