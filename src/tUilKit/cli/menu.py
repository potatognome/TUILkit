#!/usr/bin/env python3
"""
Canonical minimal CLI menu loader (PCMS-2026)
- Loads YAML menus from `project.menus/`
- Renders options
- Dispatches via `ACTIONS` from `menu_actions.py`

This file is a minimal, portable template; projects may copy it to
`src/<package>/cli/menu.py` or `cli/menu.py`.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import importlib
import yaml
import sys

_THIS = Path(__file__).resolve()
# Heuristic: src/<pkg>/cli/menu.py -> project root is parents[3]
_PROJECT_ROOT = _THIS.parents[3] if len(_THIS.parents) >= 4 else _THIS.parents[2]
def _resolve_menus_dir(project_root: Path) -> Path:
    # PCMS-2026: prefer `config/project.menus` only; do not consider
    # legacy `project.menus` in project root.
    return project_root / "config" / "project.menus"


_MENUS_DIR = _resolve_menus_dir(_PROJECT_ROOT)

# Try to import local menu_actions as package-relative, fall back to top-level
try:
    from .menu_actions import ACTIONS  # type: ignore
except Exception:
    try:
        from menu_actions import ACTIONS  # type: ignore
    except Exception:
        ACTIONS = {}


def _load_menu(menu_id: str) -> Dict[str, Any]:
    path = _MENUS_DIR / f"{menu_id}.yaml"
    if not path.exists():
        print(f"[warn] Menu file not found: {path}")
        return {}
    try:
        with path.open(encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    except Exception as e:
        print(f"[error] Failed to load {path}: {e}")
        return {}


def run_menu(store: Any = None, schema: Any = None, config: Any = None) -> None:
    menu = _load_menu("main")
    title = menu.get("title", "Main Menu")
    items: List[Dict[str, Any]] = menu.get("items", [])

    key_map: Dict[str, str] = {}
    for item in items:
        key = str(item.get("key", ""))
        action = item.get("action", "")
        if key and action:
            key_map[key] = action

    if not items:
        print("[error] No menu items found in config/project.menus/main.yaml")
        return

    while True:
        print("\n" + title)
        print("=" * len(title))
        for item in items:
            key = item.get("key", "")
            label = item.get("label", "")
            print(f"{key}. {label}")

        try:
            choice = input("\nSelect option: ").strip()
        except (KeyboardInterrupt, EOFError):
            choice = "quit"

        action = key_map.get(choice, choice)

        if action in ("quit", "back"):
            print("Goodbye")
            break
        if action in ACTIONS:
            try:
                ACTIONS[action](store=store, schema=schema, config=config)
            except TypeError:
                # allow simpler call signatures
                ACTIONS[action]()
        else:
            print(f"[error] Unknown action: {action}")


if __name__ == "__main__":
    run_menu()
