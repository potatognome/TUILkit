# CLI Menu Patterns for tUilKit Applications

Purpose
- Define the standard CLI menu framework used by V4l1d8r.
- Keep menu behavior, layout, and interaction consistent across projects.
- Make future menus validator-first: new menu work should follow V4l1d8r patterns unless there is a clear exception.

## Canonical Baseline (Validator-First)

Use V4l1d8r menu utilities as the baseline for future CLI menus:
- Shared helpers: `src/V4l1d8r/menus/shared.py`
- Selection menu: `src/V4l1d8r/menus/selection.py`
- Validation menu: `src/V4l1d8r/menus/validation.py`
- Repair menu: `src/V4l1d8r/menus/repair.py`

If a new menu is added in another project, copy these interaction rules and naming patterns first, then adapt content.

## Required Interaction Patterns

### 0) Colour Key Policy (!info deprecation)

`!info` is deprecated and treated as a neutral reset-style alias.

Rules
- Do not introduce new `!info` usage in menu code.
- Use semantic keys (`!data`, `!list`, `!text`, `!path`, `!done`, `!warn`, `!error`, etc.).
- For tabular/columnated output (especially PASS/WARN/FAIL screens), every displayed column should use explicit semantic keys.
- Use `!reset` for neutral separators/blank lines when needed.

### 1) Header Pattern

Always use `_display_header(ctx, subtitle=...)` from shared helpers.

Current baseline behavior:
- Header width is dynamic (not fixed).
- Width expands to accommodate longest line, with practical min/max bounds.
- Includes user, timestamp, cwd, and selected-project summary.

Guideline
- Do not hardcode small header widths (for example 60/72) in new menus.
- Use shared header logic so all menus inherit future improvements automatically.

### 2) Option Rendering Pattern

Use `_print_options(ctx, [...])`.

Why
- Keeps number formatting and semantic color keys consistent.
- Avoids one-off menu formatting drift.

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
        _display_header(ctx, subtitle=">> My Menu")
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

## Migration Rules for Future CLI Menus

When modernizing older menus, apply this order:
1. Replace ad-hoc border/header code with shared `_display_header`.
2. Replace custom numbered output with `_print_options`.
3. Replace comma-separated multi-select input with interactive picker.
4. Switch path rendering to `_cpath` and align paths in a vertical column.
5. Keep confirmation prompts routed through `_confirm` where available.

## Non-Goals / Avoid

- Do not add per-menu header-width constants unless required by terminal constraints.
- Do not duplicate selection-list rendering in multiple places; use one helper.
- Do not mix absolute and relative path output styles within the same menu.
- Do not introduce new multi-select conventions that conflict with the interactive picker.

## Quick Checklist (Before Merging Menu Changes)

- Uses `_display_header` and `_print_options`.
- Multi-select uses arrow/space interactive picker.
- Paths use `_cpath` and line up in a fixed visual column.
- Tabular output uses semantic keys for every column; no `!info` in table rows.
- Unknown-option handling is present.
- Tests pass.

## References

- V4l1d8r shared menu helpers: `Core/V4l1d8r/src/V4l1d8r/menus/shared.py`
- V4l1d8r selection menu: `Core/V4l1d8r/src/V4l1d8r/menus/selection.py`
- Colour key usage: `Core/V4l1d8r/config/COPILOT-INSTRUCTIONS.d/colour_key_usage.md`

---
Last updated: 2026-05-01
