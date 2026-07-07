# PCMS‑2026: Prismata Compliant Menu System
# Copilot Authoring Instructions - How Copilot must generate project.menus YAML files

## Last Updated: 2026-07-06

## Purpose
Define the canonical CLI menu framework for all Prismata applications.

Ensure consistent menu behavior, layout, interaction, and colour semantics across repositories.

Enforce schema‑driven menu definitions using YAML under project.menus/.

Ensure tUilKit configuration paths (notably colour‑key config) are validated and consistent.

Prevent drift between projects, tools, and shared modules.


## 1. General Rules
- Copilot must treat each file in `config/project.menus/` as a **menu tree**, not a single menu.
- A menu tree may contain:
  - one or more menus
  - one or more menu-items
  - optional headers, subheaders, footers, subfooters
  - optional registry overrides
  - optional conditional visibility/enablement blocks
- Copilot must never generate one file per menu unless explicitly instructed.
- Copilot must group menus logically (e.g., main, project_selection, settings, edit_configuration, folder_paths).

## 2. File Structure
Every `config/project.menus/*.yaml` file must contain the following top-level keys:

menus:
  - <menu definitions>

items:
  - <menu-item definitions>

registryOverrides:   # optional
  <registry override blocks>

The file must conform to the schemas in:
`Prismata/Meta/canonical/menu.schemas/`

## 3. Menu Definitions
Each menu entry must include:
- key (unique)
- name
- position (Main, Sub, Leaf)
- order
- type (menu type key)
- colourScheme (pointer)
- borderScheme (pointer)
- optional parent
- optional children
- optional header
- optional subheaders
- optional footer
- optional subfooter
- optional visibilityMode, visibilityCondition, visibilityDependencies
- optional enableMode, enableCondition, enableDependencies

Copilot must ensure:
- parent/child relationships are valid
- order values are unique within the file
- type corresponds to a known menu type

## 4. Header/Subheader/Footer/Subfooter Blocks
Copilot must generate these blocks using the definitions in `/Prismata/Meta/canonical/menu.schemas/header.schema.yaml`.

Rules:
- header appears at the top of the menu
- subheaders appear below the header
- footer appears at the bottom of the menu
- subfooter appears above the footer
- all support conditional visibility
- all support colourScheme and borderScheme pointers
- at least one blank row in between each header, subheader and footer

## 5. Menu-Item Definitions
Each item must include:
- key
- name
- order
- type (item type key)
- selectionMethod
- action (execute, navigate, back, exit, noop)
- optional executeTarget or navigateTarget
- optional visibilityMode, visibilityCondition, visibilityDependencies
- optional enableMode, enableCondition, enableDependencies
- optional colourScheme override

Copilot must ensure:
- item types match registry defaults
- selectionMethod matches item type unless overridden
- order values are unique within the menu

## 6. Conditional Logic
reference: `/Prismata/Meta/canonical/menu.schemas/menu-condition-language.schema.yaml`
Copilot must generate conditions using the Menu Condition Language (MCL):

Examples:
visibilityCondition: "user_is_admin == true"
visibilityCondition: "feature_flag('beta_mode') == true"
enableCondition: "project_selected == true"

Copilot must include visibilityDependencies or enableDependencies whenever conditions are used.

## 7. Registry Overrides
Copilot may generate registry overrides when:
- a menu type needs custom defaults
- a menu-item type needs custom behaviour
- colourScheme or borderScheme needs tenant-specific changes

Overrides must follow the structure in:
`/Prismata/Meta/canonical/menu.schemas/menu-registry.schema.yaml`

## 8. Best Practices
- Group related menus into the same file (e.g., settings.yaml, admin.yaml).
- Use meaningful keys (menu.settings.display, settings.volume).
- Use consistent ordering (1, 2, 3…).
- Always include a footer for hotkeys or status text.
- Use subfooter for progress bars or secondary status.
- Use colourScheme and borderScheme pointers, never inline ANSI.
- Use menu types to reduce duplication.

## 9. What Copilot Must Not Do
- Must not create one file per menu unless explicitly asked.
- Must not inline colour or border definitions.
- Must not omit required fields.
- Must not invent schemas.
- Must not break parent/child relationships.
- Must not generate invalid MCL expressions.

## 10. Output Format
When asked to create or modify `config/project.menus` files:
- Copilot must output valid YAML.
- Copilot must follow the canonical schemas exactly.
- Copilot must include headers, footers, and registry overrides when appropriate.
- Copilot must generate complete menu trees, not fragments.

## 11. Canonical Baseline (Schema‑Driven Menus)
All Prismata applications must load menus from:

Code
config/project.menus/*.yaml
Menu logic must be implemented in:

Code
src/<project>/cli/menu.py          (loader + dispatcher)
src/<project>/cli/menu_actions.py  (workflow functions)

## 12. Required Interaction Patterns
2.0 Colour Key Policy (tUilKit Configuration Required)
Rules
Use semantic colour keys:
!data, !list, !text, !path, !done, !warn, !error, !reset.

Avoid new !info usage unless required for legacy compatibility.

All tabular output must use explicit semantic keys for each column.

Colour‑key configuration must load from the path defined in:

Code
config/project.menus/folder_paths.yaml → config.tuilkit_colour_keys
Verification Requirement
Every project must verify:

tUilKit colour‑key config file exists

folder_paths.yaml points to the correct colour‑key file

colour‑key loader uses the verified path

This prevents colour drift across repos.

## 12.1 Header Pattern
Always use _display_header(...) from shared helpers.

Main Menu
Code
_display_header(ctx, menu_title="Main Menu", is_main_menu=True)
Submenus
Code
_display_header(ctx, menu_title="Some Menu")
Rules
Never hardcode borders or uppercase logic.

Titles must be plain strings; helper handles formatting.

Blank line after header is mandatory.

## 12.2 Option Rendering Pattern
Use _print_options(ctx, [...]).

Icon Standard
Core stable icons:

Meaning	Icon
Project / Select	📂
Validation / Check	✅
Repair	🛠️ / 🏗️
Settings	⚙️
Save	💾
Quit	🚪
Back	◀


Extended recommended icons:

🔎 🔍 ⚖️ 🔄 🧩 🧰 🧱 📄 ➕ 🗑️ ✂️

ASCII fallback allowed.

Ordering Rules
Main menu last item: Quit Application

Submenu last item: Back

Settings + Configuration must be a single wrapper entry.

## 12.3 Selection Pattern (Interactive Multi‑Select)
Primary multi‑select UX is the interactive picker:

Up/Down: move

Space: toggle

A: select all

C: clear all

Enter: confirm

Esc: cancel

Implementation baseline uses:

msvcrt.getch()

Canvas redraw

Cursor.hide() / Cursor.show()

## 12.4 Path Display Pattern
All filesystem paths must be:

colourized via _cpath(ctx, path)

aligned in a vertical column

relative when possible

## 13. Migration Rules for Modernizing Older Menus
Apply in this order:

Replace custom headers with _display_header.

Replace custom option rendering with _print_options.

Replace comma‑separated multi‑select with interactive picker.

Replace path rendering with _cpath.

Route confirmations through _confirm or _confirm_with_mode.

Use Settings + Configuration wrapper pattern.

Ensure title rendering follows _display_header(menu_title=...).

## 14. tUilKit CLI Module Alignment
Legacy module:
`/Prismata/Projects/Core/tUilKit/src/tUilKit/utils/cli_menus.py`

Rules:

Prefer interface helpers `/Prismata/Projects/Tooling` over ad‑hoc loops.

Keep icon semantics aligned with PCMS‑2026.

Use centralized settings + safety prompts.

Verify colour‑key config path before rendering.

## 15. Non‑Goals / Avoid
No custom header width constants.

No duplicated selection‑list rendering.

No mixing absolute/relative paths in the same menu.

No new multi‑select conventions.

No hardcoded menu definitions in Python.

No colour‑key usage outside semantic keys.

## 16. Quick Checklist (Before Merging Menu Changes)
Uses _display_header and _print_options.

Uses correct main/submenu title pattern.

Multi‑select uses interactive picker.

Paths use _cpath and aligned columns.

Tabular output uses semantic colour keys.

Icons follow expanded semantic mapping.

Main menu includes Settings + Configuration wrapper.

Settings exit warning appears when AUTO‑YES is active.

Unknown‑option handling present.

Colour‑key config path validated.

Menu YAML → menu_actions linkage verified.

Tests pass.

## References
Tooling shared helpers:
`/Prismata/Projects/Tooling/utilities/interface_primitives/menu_helpers.py`
`/Prismata/Projects/Tooling/utilities/interface_primitives/vile.py`
`/Prismata/Projects/Tooling/utilities/interface_primitives/border_patterns.py`

V4l1d8r selection menu: 
`Core/V4l1d8r/src/V4l1d8r/menus/selection.py`

Colour key usage: `.github/copilot-instructions.d/colour_key_usage.md`
Prismata menu YAML directory: `/config/project.menus/`
Prismata menu loader: menu.py
Prismata action dispatcher: menu_actions.py