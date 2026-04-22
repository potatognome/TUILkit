# Changelog

All notable changes to this project are documented in this file.

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
