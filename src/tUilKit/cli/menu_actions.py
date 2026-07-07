#!/usr/bin/env python3
"""
Canonical minimal `menu_actions.py` template.
Projects should extend action implementations here; every `action:` id used
in YAML under `project.menus/` must have an entry in `ACTIONS`.
"""
from __future__ import annotations

from typing import Any, Dict


def _stub(name: str):
    def fn(store=None, schema=None, config=None, **_):
        print(f"[warn] Action '{name}' not implemented.")
    fn.__name__ = name
    return fn


def action_quit(store=None, schema=None, config=None, **_):
    print("Exiting...")


# Example concrete actions (projects must replace / extend)
ACTIONS: Dict[str, Any] = {
    "noop": _stub("noop"),
    "quit": action_quit,
}


# --- generated action stubs (safe, appended) ---
def _generated_stub(name):
    def _fn(store=None, schema=None, config=None, **_):
        print(f"[warn] Action '{name}' not implemented.")
    return _fn

try:
    ACTIONS
except NameError:
    ACTIONS = {}

ACTIONS.setdefault("noop", _generated_stub("noop"))
ACTIONS.setdefault("quit", _generated_stub("quit"))


# --- generated action stubs (safe, appended) ---
def _generated_stub(name):
    def _fn(store=None, schema=None, config=None, **_):
        print(f"[warn] Action '{name}' not implemented.")
    return _fn

try:
    ACTIONS
except NameError:
    ACTIONS = {}

ACTIONS.setdefault("noop", _generated_stub("noop"))
ACTIONS.setdefault("quit", _generated_stub("quit"))


# --- generated action stubs (safe, appended) ---
def _generated_stub(name):
    def _fn(store=None, schema=None, config=None, **_):
        print(f"[warn] Action '{name}' not implemented.")
    return _fn

try:
    ACTIONS
except NameError:
    ACTIONS = {}

ACTIONS.setdefault("noop", _generated_stub("noop"))
ACTIONS.setdefault("open_menu:menu_main", _generated_stub("open_menu:menu_main"))
ACTIONS.setdefault("quit", _generated_stub("quit"))
