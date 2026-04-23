# Changelog

All notable changes to this project are documented in this file.

## 0.5.1 - 2026-04-22

### Added
- `examples/test_config.py` — path-bootstrap script that resolves all test paths from `tUilKit_CONFIG.json` and writes `test_paths.json`.
- `examples/test_output.py` — 8 supplementary test functions covering `ColourManager` and `Logger` (`colour_fstr`, `colour_path`, `strip_ansi`, `interpret_codes`, `colour_log`, `print_rainbow_row`, `apply_border`, `log_exception`).
- `examples/test_cli_menus.py` — 8 supplementary test functions covering `CLIMenuHandler` (`show_numbered_menu`, `confirm`, `prompt_with_default`, `get_numeric_choice`, `show_info_screen`, `edit_key_value_pairs`, `browse_directory`, `show_menu_with_preview`).
- `CLIMenuHandler` interface section in `docs/tUilKit_Comprehensive_Usage_Guide.md`.
- `examples/` usage and `PYTHONIOENCODING` note in the Testing section of the Comprehensive Usage Guide.

### Fixed
- `get_cli_menu_handler()` in `factories.py` now correctly imports `CLIMenuHandler` inside the function before instantiation (was a `NameError`).

### Changed
- Rewrote `building_examples_policy.md` — full `tUilKit_CONFIG` path-resolution standard, per-function log requirements, UI menu break-test scenarios, and test runner structure.
- Added §6 (verbose function call log format, per-function log files) to `logging_policy.md`.
- Both policy files propagated to all 12 project `.github/copilot-instructions.d/` folders.
- `building_tests_policy.md` removed from all project folders (superseded by `building_examples_policy.md`).

## 0.5.0 - 2026-04-21

### Added
- Added root-mode and shared-config tests:
  - `tests/test_config_path_resolver_root_modes.py`
  - `tests/test_config_loader_root_mode_shared_config.py`

### Changed
- Updated test bootstrap logic so direct test script execution resolves `tUilKit` imports from local `src`.
- Updated existing config tests to use deterministic project-root config paths.
- Aligned shared config test expectations with current `config/GLOBAL_SHARED.d` inventory.
- Standardized package version references across release files.

### Fixed
- Fixed direct execution failure (`ModuleNotFoundError: No module named 'tUilKit'`) for test scripts run from `tests/`.
