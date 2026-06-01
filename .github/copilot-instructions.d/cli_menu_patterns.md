# CLI Menu Patterns for tUilKit Applications

Purpose
- Define the standard CLI menu framework used by V4l1d8r.
- Keep menu behavior, layout, and interaction consistent across projects.
- Make future menus validator-first: new menu work should follow current V4l1d8r patterns unless there is a clear exception.

## Canonical Baseline (Validator-First)

Use V4l1d8r menu utilities as the baseline for future CLI menus:
- Shared helpers: `src/V4l1d8r/menus/shared.py`
- Selection menu: `src/V4l1d8r/menus/selection.py`
- Validation menu: `src/V4l1d8r/menus/validation.py`
- Repair menu: `src/V4l1d8r/menus/repair.py`
- Configuration menu: `src/V4l1d8r/menus/configuration.py`
- Settings menu: `src/V4l1d8r/menus/settings.py`

If a new menu is added in another project, copy these interaction rules and naming patterns first, then adapt content.

## Required Interaction Patterns

### 0) Colour Key Policy

Rules
- Prefer semantic keys (`!data`, `!list`, `!text`, `!path`, `!done`, `!warn`, `!error`, etc.) for menu and table output.
- Existing `!info` usage is tolerated for compatibility while migration is in progress.
- Do not introduce new `!info` usage when an explicit semantic key is available.
- For tabular/columnated output (especially PASS/WARN/FAIL screens), every displayed column should use explicit semantic keys.
- Use `!reset` for neutral separators/blank lines when needed.

### 1) Header Pattern

Always use `_display_header(...)` from shared helpers.

Current baseline behavior:
- Main menu uses:
    - `_display_header(ctx, menu_title="Main Menu", is_main_menu=True)`
    - Two bordered sections are rendered: app header, then uppercase centered menu title.
    - If any global auto-approval state is active, `[AUTO-YES ACTIVE]` appears in header content.
- Submenus use:
    - `_display_header(ctx, menu_title="Some Menu")`
    - One bordered section: uppercase centered menu title.
- A blank line is printed after each bordered header section.

Guideline
- Do not hardcode local border builders for menu titles.
- Use shared header logic so all menus inherit future improvements automatically.
- Keep title strings plain (for example, `"Settings"`); `_display_header` handles uppercase.

### 2) Option Rendering Pattern

Use `_print_options(ctx, [...])`.

Why
- Keeps number formatting and semantic color keys consistent.
- Avoids one-off menu formatting drift.

Icon standard
- Menu options should use `_print_options` icon mapping and a broader semantic palette.
- Core defaults (must remain stable):
    - Project / Select -> `📂`
    - Validation / Check -> `✅`
    - Repair -> `🏗️` or `🛠️`
    - Settings -> `⚙️`
    - Save -> `💾`
    - Quit / Exit -> `🚪`
    - Back -> `◀`
- Extended mappings (recommended):
    - Discover / Search / Scan -> `🔎` / `🔍`
    - Compare / Diff -> `⚖️`
    - Sync -> `🔄`
    - Inject / Template -> `🧩`
    - Config -> `🧰`
    - Workspace -> `🧱`
    - Copy -> `📄`
    - Add / Create -> `➕`
    - Remove / Delete -> `🗑️`
    - Snippets -> `✂️`
- If terminal encoding cannot render emoji, fallback ASCII tokens are acceptable.

Menu ordering rules
- Last option is always `Quit Application` on the Main Menu.
- In submenus, last option is always `Back`.
- In the current baseline, the main menu uses one wrapper item: `Settings and Configuration`.

### 3) Selection Pattern (Interactive Multi-Select)

Primary multi-selection UX is the interactive picker, not comma-separated parsing.

Baseline controls:
- Up/Down arrows: move cursor
- Space: toggle item
- A: select all
- C: clear all
- Enter: confirm
- Esc: cancel and restore prior selection

Implementation baseline:
- `msvcrt.getch()` for key reads (Windows)
- `Canvas` for in-place redraws
- `Cursor.hide()` / `Cursor.show()` for clean interaction

### 4) Path Display Pattern

All displayed filesystem paths should be colorized and relative when possible.

Rules
- Use `_cpath(ctx, path)` when logging paths.
- In project lists, align path start position in a vertical column.
- Compute label width first, then left-pad/right-pad labels before adding `| path`.

Example (list alignment pattern):

```python
labels = [
    (f"[{p.scope}] " if p.scope else "") + p.name + (" *" if p in ctx.selected_projects else "")
    for p in ctx.projects
]
label_width = max((len(label) for label in labels), default=0)

for idx, p in enumerate(ctx.projects, start=1):
    label = labels[idx - 1]
    ctx.logger.colour_log(
        "!list", f"{idx:3}",
        "!text", f" . {label:<{label_width}}",
        "!path", f"  |  {_cpath(ctx, p.project_root)}",
        log_files=list(ctx.log_files.values()),
        time_stamp=True,
    )
```

### 5) Menu Flow Pattern

Recommended loop template:

```python
def _my_menu(ctx: AppContext) -> None:
    while True:
        _display_header(ctx, menu_title="My Menu")
        _print_options(ctx, [
            "1 . First action",
            "2 . Second action",
            "0 . Back",
        ])
        choice = _prompt()

        if choice == "0":
            return
        elif choice == "1":
            ...
            _pause(ctx)
        elif choice == "2":
            ...
            _pause(ctx)
        else:
            ctx.logger.colour_log(
                "!warn", "[!] Unknown option.",
                log_files=list(ctx.log_files.values()),
                time_stamp=True,
            )
            _pause(ctx)
```

### 6) Validator Main Menu Baseline

For V4l1d8r, the main menu order is canonical:

1. `Project Selection`
2. `Validation, Scanning and Comparison`
3. `Sync, Repair and Fix`
4. `Settings and Configuration`
0. `Quit Application`

`Snippet management` and destructive/automation toggles belong under `Settings`, not the main menu.

### 6.1) Settings + Configuration Wrapper Pattern

Current V4 baseline uses a dedicated wrapper submenu for these concerns:

1. `Configuration`
2. `Settings`
0. `Back`

Guideline
- Keep the wrapper submenu as the single main-menu entry point when both settings and configuration flows exist.
- Do not duplicate settings toggles on the main menu.

### 7) Global Settings Safety Pattern

Settings menu should include global toggles:
- `Toggle Recursive Folder Search: {ON, OFF}`
- `Toggle YES TO ALL QUERIES: {ON, OFF}`
- `Toggle Add Missing Config Keys: {AUTO-NO, ASK, AUTO-YES}`
- `Toggle Remove Config Keys: {AUTO-NO, ASK, AUTO-YES}`
- `Toggle Remove Section Keys (inject): {AUTO-NO, ASK, AUTO-YES}`
- `Toggle Create Backups Before Write: {ON, OFF}`
- `Snippet management`
- `Open interactive toggle table editor`

Synchronization rule
- Enabling `YES TO ALL QUERIES` must set all three tri-state policy modes to `AUTO-YES`.
- Cycling any tri-state mode should re-sync the global YES/NO state.

Safety rule:
- When leaving Settings, if any tri-state policy mode is `AUTO-YES`, show a warning and require confirmation before returning to main menu.

## Migration Rules for Future CLI Menus

When modernizing older menus, apply this order:
1. Replace ad-hoc border/header code with shared `_display_header`.
2. Replace custom numbered output with `_print_options`.
3. Replace comma-separated multi-select input with interactive picker.
4. Switch path rendering to `_cpath` and align paths in a vertical column.
5. Keep confirmation prompts routed through `_confirm` where available.
6. For policy-driven prompts, route through `_confirm_with_mode` when settings support AUTO-NO/ASK/AUTO-YES.
7. Use the `Settings and Configuration` wrapper pattern when both settings and configuration menus exist.
8. Ensure main/submenu title rendering follows `_display_header(..., menu_title=...)` rules.

## tUilKit CLI Module Alignment Note

Legacy utility module:
- `Core/tUilKit/src/tUilKit/utils/cli_menus.py`

When modernizing or creating new menus in tUilKit modules:
- Prefer V4l1d8r shared menu helpers/patterns over ad-hoc direct input loops.
- Keep icon semantics aligned to this document.
- Prefer centralized settings behavior and safety prompts over per-menu custom logic.

## Non-Goals / Avoid

- Do not add per-menu header-width constants unless required by terminal constraints.
- Do not duplicate selection-list rendering in multiple places; use one helper.
- Do not mix absolute and relative path output styles within the same menu.
- Do not introduce new multi-select conventions that conflict with the interactive picker.

## Quick Checklist (Before Merging Menu Changes)

- Uses `_display_header` and `_print_options`.
- Uses `menu_title` / `is_main_menu` pattern (no legacy `subtitle` argument).
- Multi-select uses arrow/space interactive picker.
- Paths use `_cpath` and line up in a fixed visual column.
- Tabular output uses semantic keys for every column.
- Icons follow the expanded semantic mapping in this doc with fallback support.
- Main menu includes `Settings and Configuration` as a single wrapper entry.
- Settings exit warning appears when AUTO-YES modes are active.
- Unknown-option handling is present.
- Tests pass.

## References

- V4l1d8r shared menu helpers: `Core/V4l1d8r/src/V4l1d8r/menus/shared.py`
- V4l1d8r selection menu: `Core/V4l1d8r/src/V4l1d8r/menus/selection.py`
- Colour key usage: `.github/copilot-instructions.d/colour_key_usage.md`

---
Last updated: 2026-05-27
