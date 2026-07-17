# Changelog

All notable changes to this project are documented in this file.

## 0.6.3 - 2026-07-17

### Added
- Introduced AI release-governance assets for contributors: `.github/ai-quality-checklist.md`, `.github/ai-prompt-wrapper.md`, `.github/pull_request_template.md`, and `scripts/ai_quality_gate.py`.

### Changed
- Standardized AI-assisted contribution workflow in `.github/copilot-instructions.md` and `README.md` with explicit quality-gate guidance.
- Synchronized project version references across release metadata files.

## 0.6.1 - 2026-06-08

### Added
- Expanded tenant DSL menu-tree support in active Prismata applications via `render_tenant_menu_tree()` rollouts.

### Fixed
- `CLIMenuHandler` submenu index rendering now starts user-selectable items at `1` while preserving `0` for reserved navigation actions.
- Removed duplicate reserved action collisions in submenus by standardizing submenu reserved injection to a single `Back` action.

### Changed
- Improved consistency of shared CLI menu behavior across tenant and infrastructure apps using the common menu engine.

## 0.6.2 - 2026-07-06

### Changed
- Menu loader discovery now prefers `config/project.menus` for projects migrated under PCMS-2026.

### Fixed
- Ensure plain-text renderer displays `icon` before `label` when `tUilKit` is unavailable.

## 0.6.0 - 2026-05-06

### Added
- **Terminal Windowing System** (`tUilKit.output`) — full compositor-based
  terminal UI framework with the following subpackages:
  - `output/backend/` — `Style` dataclass, `RenderBackendInterface` ABC, and
    `AnsiRenderBackend` (ANSI escape sequences, absolute cursor positioning,
    diff-only flushing).
  - `output/zorder/` — `ZOrderManager` keeping windows sorted by `z_index`;
    exposes `raise_window`, `lower_window`, `set_z_index`.
  - `output/window/` — `Window` dataclass (id, x, y, width, height, z_index,
    content, border_style, focusable, title) and `WindowManager`
    (`create_window`, `close_window`, `move_window`, `resize_window`,
    `focus_window`, `raise_window`, `lower_window`, `set_z_index`,
    `list_windows_in_z_order`).
  - `output/draw/` — `Rect`, `DrawContext` (window-local coordinates +
    clipping), `draw_border`, `draw_titled_border` supporting `"single"`,
    `"double"`, `"heavy"`, and `"rounded"` border styles with Unicode
    box-drawing characters.
  - `output/widgets/` — `Widget` abstract base class (`render`, `measure`,
    `layout`); built-in `TextWidget` and `FilledWidget`.
  - `output/compositor/` — `Compositor` with double-buffering; `render_frame`
    clears back buffer, paints all windows in z-order with clipped
    `DrawContext`, then diff-flushes only changed cells to the backend.
- **80 new pytest tests** in `tests/output/` covering every subsystem.
- **`docs/compositor_README.md`** — full usage guide, architecture overview,
  custom-widget and custom-backend examples.

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
