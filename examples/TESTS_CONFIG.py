#!/usr/bin/env python3
"""
examples/TESTS_CONFIG.py
Policy-aligned bootstrap for tUilKit examples.

This keeps compatibility with existing examples/test_config.py while emitting
the same test_paths.json contract used by newer exemplars.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict


HERE = Path(__file__).resolve()
PROJECT_ROOT = next((p for p in HERE.parents if (p / "pyproject.toml").exists()), HERE.parents[1])
WORKSPACE_ROOT = PROJECT_ROOT.parents[1]

SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


def _load_config() -> Dict:
    from tUilKit.utils.config import ConfigLoader

    cfg_path = PROJECT_ROOT / "config" / "tUilKit_CONFIG.json"
    loader = ConfigLoader(config_path=str(cfg_path))
    cfg = getattr(loader, "global_config", None)
    if isinstance(cfg, dict) and cfg:
        return cfg

    return loader.load_config(str(cfg_path))


def _resolve(cfg: Dict, mode_key: str, path_key: str, fallback: str) -> Path:
    mode = str(cfg.get("ROOT_MODES", {}).get(mode_key, "project")).lower()
    base = WORKSPACE_ROOT if mode == "workspace" else PROJECT_ROOT
    rel = str(cfg.get("PATHS", {}).get(path_key, fallback))
    return (base / rel).resolve()


def main() -> int:
    cfg = _load_config()

    # Calculate tUilKit config path (tUilKit's own config)
    tuilkit_config_path = PROJECT_ROOT / "config" / "tUilKit_CONFIG.json"

    payload = {
        "project_name": cfg.get("INFO", {}).get("PROJECT_NAME", "tUilKit"),
        "config_file": str((PROJECT_ROOT / "config" / "tUilKit_CONFIG.json").resolve()),
        "tuilkit_config_file": str(tuilkit_config_path.resolve()),
        "examples_folder": str(HERE.parent.resolve()),
        "project_root": str(PROJECT_ROOT.resolve()),
        "workspace_root": str(WORKSPACE_ROOT.resolve()),
        "test_logs_folder": str(_resolve(cfg, "TESTS_LOGS", "TESTS_LOGS", ".tests_logs/tUilKit/")),
        "tests_config_folder": str(_resolve(cfg, "TESTS_CONFIG", "TESTS_CONFIG", ".tests_config/")),
        "config_folder": str(_resolve(cfg, "CONFIG", "CONFIG", "config/")),
        "logs_folder": str(_resolve(cfg, "LOG_PATHS", "LOG_PATHS", ".logs/tUilKit/")),
        "tests_inputs_folder": str(_resolve(cfg, "TESTS_INPUTS", "TESTS_INPUTS", ".tests_data/inputs/")),
        "tests_outputs_folder": str(_resolve(cfg, "TESTS_OUTPUTS", "TESTS_OUTPUTS", ".tests_data/outputs/")),
    }

    for key in ("test_logs_folder", "tests_inputs_folder", "tests_outputs_folder"):
        Path(payload[key]).mkdir(parents=True, exist_ok=True)

    out_path = HERE.parent / "test_paths.json"
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"[TESTS_CONFIG] Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
