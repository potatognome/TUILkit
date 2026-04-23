#!/usr/bin/env python3
"""
examples/test_config.py
Bootstrap: resolves all paths for tUilKit's examples suite from project config.
Run this file directly to (re)generate test_paths.json.
"""
import sys
import json
from pathlib import Path

HERE = Path(__file__).resolve()
PROJECT_ROOT   = next(p for p in HERE.parents if (p / "pyproject.toml").exists())
WORKSPACE_ROOT = next(p for p in PROJECT_ROOT.parents if (p / "dev_local.code-workspace").exists())
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from tUilKit.factories import get_config_loader

config_loader = get_config_loader()
config        = config_loader.global_config


def _resolve(mode_key: str, path_key: str) -> Path:
    mode = config.get("ROOT_MODES", {}).get(mode_key, "project")
    base = WORKSPACE_ROOT if mode == "workspace" else PROJECT_ROOT
    return base / config.get("PATHS", {}).get(path_key, "")


TEST_LOGS_FOLDER   = _resolve("TEST_LOGS",   "TEST_LOGS")
TEST_CONFIG_FOLDER = _resolve("TEST_CONFIG", "TEST_CONFIG")
CONFIG_FOLDER      = _resolve("CONFIG",      "CONFIG")

paths = {
    "examples_folder":    str(HERE.parent),
    "project_root":       str(PROJECT_ROOT),
    "workspace_root":     str(WORKSPACE_ROOT),
    "test_logs_folder":   str(TEST_LOGS_FOLDER),
    "test_config_folder": str(TEST_CONFIG_FOLDER),
    "config_folder":      str(CONFIG_FOLDER),
}

with open(HERE.parent / "test_paths.json", "w") as f:
    json.dump(paths, f, indent=4)

if __name__ == "__main__":
    print(f"test_paths.json written to {HERE.parent}")
    for k, v in paths.items():
        print(f"  {k}: {v}")
