"""Boot sequence renderer for Prismata CLI applications.

Implements the BE/WHEN/WHOM/WHAT/AT/USING/WHY model and provides a
standardized pre-menu pause flow.
"""

from __future__ import annotations

import getpass
import os
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

from tUilKit import get_config_loader, get_logger


@dataclass
class BootSequenceContext:
    app_name: str
    command: str
    process_name: str
    invocation_epoch: float
    cwd: Path
    project_root: Path
    config_path: Optional[Path]
    workspace_root: Optional[Path]
    cli_args: list[str] = field(default_factory=list)
    normalized_args: Dict[str, Any] = field(default_factory=dict)
    mode_flags: Dict[str, Any] = field(default_factory=dict)
    reason: Optional[str] = None


def _str_map(items: Dict[str, Any]) -> str:
    if not items:
        return "(none)"
    return ", ".join(f"{k}={v}" for k, v in items.items())


def build_boot_context(
    app_name: str,
    command: Optional[str] = None,
    *,
    args: Optional[Dict[str, Any]] = None,
    mode_flags: Optional[Dict[str, Any]] = None,
    reason: Optional[str] = None,
) -> BootSequenceContext:
    """Build a boot context from process/runtime state and ConfigLoader."""
    loader = get_config_loader()
    config = loader.global_config if isinstance(loader.global_config, dict) else {}
    roots = config.get("ROOTS", {}) if isinstance(config.get("ROOTS", {}), dict) else {}

    project_root = Path(str(roots.get("PROJECT", Path.cwd()))).resolve()
    workspace_root_raw = roots.get("WORKSPACE")
    workspace_root = Path(str(workspace_root_raw)).resolve() if workspace_root_raw else None

    return BootSequenceContext(
        app_name=app_name,
        command=command or " ".join(sys.argv),
        process_name=Path(sys.argv[0]).name if sys.argv else app_name,
        invocation_epoch=time.time(),
        cwd=Path.cwd(),
        project_root=project_root,
        config_path=Path(loader.config_path).resolve() if getattr(loader, "config_path", None) else None,
        workspace_root=workspace_root,
        cli_args=list(sys.argv[1:]),
        normalized_args=args or {},
        mode_flags=mode_flags or {},
        reason=reason,
    )


def run_boot_sequence(
    app_name: str,
    command: Optional[str] = None,
    *,
    args: Optional[Dict[str, Any]] = None,
    mode_flags: Optional[Dict[str, Any]] = None,
    reason: Optional[str] = None,
    pause: bool = True,
) -> bool:
    """Render standardized boot output and return False when user quits at pause."""
    logger = get_logger()
    loader = get_config_loader()
    cfg = loader.global_config if isinstance(loader.global_config, dict) else {}
    root_modes = cfg.get("ROOT_MODES", {}) if isinstance(cfg.get("ROOT_MODES", {}), dict) else {}

    ctx = build_boot_context(
        app_name,
        command,
        args=args,
        mode_flags=mode_flags,
        reason=reason,
    )

    start_stamp = datetime.fromtimestamp(ctx.invocation_epoch)
    now_stamp = datetime.now()
    elapsed = max(0.0, (now_stamp - start_stamp).total_seconds())

    logger.apply_border(
        text=f"{app_name} Boot Sequence",
        pattern={"TOP": "=", "BOTTOM": "=", "LEFT": " ", "RIGHT": " "},
        total_length=78,
        border_rainbow=True,
    )

    logger.colour_log("!proc", "🧭 BE:", "!info", "Boot execution model")
    logger.colour_log("!date", "⏱️ WHEN:", "!info", start_stamp.strftime("%Y-%m-%d %H:%M:%S"), "!data", f"elapsed={elapsed:.3f}s")
    logger.colour_log(
        "!info", "👤 WHOM:",
        "!data", f"user={getpass.getuser()}",
        "!data", f"root={ctx.workspace_root or '(none)'}",
        "!data", f"tenant={ctx.app_name}",
        "!data", f"process={ctx.process_name}",
    )
    logger.colour_log("!info", "🚀 WHAT:", "!data", ctx.command)
    logger.colour_log(
        "!info", "📍 AT:",
        "!path", f"cwd={ctx.cwd}",
        "!path", f"project={ctx.project_root}",
        "!path", f"config={ctx.config_path or '(none)'}",
    )
    logger.colour_log(
        "!info", "🧰 USING:",
        "!data", f"args={ctx.cli_args or '(none)'}",
        "!data", f"normalized={_str_map(ctx.normalized_args)}",
        "!data", f"modes={_str_map(ctx.mode_flags)}",
    )
    if ctx.reason:
        logger.colour_log("!info", "🧠 WHY:", "!data", ctx.reason)

    logger.colour_log("!proc", "🗂️ Bootstrap Config:", "!path", str(ctx.config_path or "(none)"))
    if root_modes:
        logger.colour_log("!proc", "🧱 ROOT_MODES:")
        for key, value in root_modes.items():
            logger.colour_log("!list", f"  {key}", "!info", "=", "!data", str(value))

    if pause:
        raw = input("Press Enter/Space to continue or Q to quit: ")
        if raw.strip().lower().startswith("q"):
            logger.colour_log("!warn", "Boot sequence terminated by user.")
            return False

    return True
