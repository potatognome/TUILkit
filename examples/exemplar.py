#!/usr/bin/env python3
"""
examples/exemplar.py - tUilKit exemplar mock entry point.

Exercises factory imports, config loading, root-mode path reporting,
and basic logger/colour-manager behavior outside pytest.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve()
TEST_PATHS_FILE = HERE.parent / "test_paths.json"
TESTS_CONFIG_FILE = HERE.parent / "TESTS_CONFIG.py"

if not TEST_PATHS_FILE.exists():
    subprocess.run([sys.executable, str(TESTS_CONFIG_FILE)], check=True)

PATHS = json.loads(TEST_PATHS_FILE.read_text(encoding="utf-8-sig"))
PROJECT_ROOT = Path(PATHS["project_root"]).resolve()
WORKSPACE_ROOT = Path(PATHS["workspace_root"]).resolve()


def _resolve_config_file(p: dict) -> Path:
    """Derive the primary tUilKit config path from whatever keys test_paths.json provides."""
    for key in ("config_file", "tuilkit_config_file"):
        raw = p.get(key)
        if raw:
            c = Path(raw)
            if c.exists():
                return c.resolve()
    for folder_key in ("config_folder", "tests_config_folder", "test_config_folder"):
        folder = p.get(folder_key)
        if folder:
            c = Path(folder) / "tUilKit_CONFIG.json"
            if c.exists():
                return c.resolve()
    # Hard fallback: project-local config/
    return (PROJECT_ROOT / "config" / "tUilKit_CONFIG.json").resolve()


CONFIG_FILE = _resolve_config_file(PATHS)

SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from tUilKit.utils.config import ConfigLoader  # noqa: E402
from tUilKit.utils.output import ColourManager, Logger  # noqa: E402


# Initialize ConfigLoader with explicit tUilKit config path
config_loader = ConfigLoader(config_path=str(CONFIG_FILE))
colour_manager = ColourManager(config_loader.load_colour_config())
logger = Logger(colour_manager)
CONFIG = config_loader.load_config(str(CONFIG_FILE))


def _resolve(mode_key: str, path_key: str, fallback: str) -> Path:
    mode = str(CONFIG.get("ROOT_MODES", {}).get(mode_key, "project")).lower()
    root = WORKSPACE_ROOT if mode == "workspace" else PROJECT_ROOT
    rel = str(CONFIG.get("PATHS", {}).get(path_key, fallback))
    return (root / rel).resolve()


def _log_targets() -> list[str]:
    logs_root = _resolve("LOGS", "LOGS", ".workspace/.logs/tUilKit/")
    logs_root.mkdir(parents=True, exist_ok=True)

    targets: list[str] = []
    for key in CONFIG.get("LOG_CATEGORIES", {}).get("default", ["MASTER", "SESSION"]):
        name = CONFIG.get("LOG_FILES", {}).get(key)
        if isinstance(name, str) and name:
            targets.append(str(logs_root / name))

    if not targets:
        targets = [str(logs_root / "tUilKit_SESSION.log"), str(logs_root / "tUilKit_MASTER.log")]
    return targets


LOG_TARGETS = _log_targets()


def log_line(msg: str, key: str = "!info") -> None:
    try:
        logger.colour_log(key, msg, log_files=LOG_TARGETS, time_stamp=True)
    except Exception:
        print(msg)


def draw_header() -> None:
    title = f"{CONFIG.get('INFO', {}).get('PROJECT_NAME', 'tUilKit')} Exemplar"
    try:
        logger.apply_border(
            text=title,
            pattern={"TOP": "=", "BOTTOM": "=", "LEFT": " ", "RIGHT": " "},
            total_length=72,
            border_rainbow=True,
            log_files=LOG_TARGETS,
            include_timestamp=True,
        )
    except Exception:
        print("=" * 72)
        print(title)
        print("=" * 72)


def show_config_and_paths() -> None:
    log_line("Config and Paths", key="!proc")
    log_line(f"Primary config: {CONFIG_FILE}", key="!data")

    for k, v in CONFIG.get("ROOT_MODES", {}).items():
        if "ROOT_MODES:" in str(k):
            continue
        log_line(f"ROOT_MODE[{k}] = {v}", key="!data")

    for mk, pk, fb in (
        ("LOGS", "LOGS", ".workspace/.logs/tUilKit/"),
        ("CONFIG", "CONFIG", "config/"),
        ("INPUTS", "INPUTS", ".projects_data/inputData/tUilKit/"),
    ):
        log_line(f"Resolved {pk}: {_resolve(mk, pk, fb)}", key="!info")

    logs_root = _resolve("LOGS", "LOGS", ".workspace/.logs/tUilKit/")
    for log_key, log_file in CONFIG.get("LOG_FILES", {}).items():
        log_line(f"LOG_FILE[{log_key}] -> {logs_root / log_file}", key="!info")


def run_factory_demo() -> None:
    log_line("Factory demo", key="!proc")

    try:
        rendered = colour_manager.colour_str("!done", "Colour manager rendering OK")
        print(rendered)
    except Exception as exc:
        log_line(f"Colour manager fallback used: {exc}", key="!warning")

    log_line("Logger factory operational", key="!done")

    try:
        loaded = config_loader.load_config(str(CONFIG_FILE))
        version = loaded.get("INFO", {}).get("VERSION", "unknown")
        log_line(f"Config loader operational: version={version}", key="!done")
    except Exception as exc:
        log_line(f"Config load failed: {exc}", key="!error")


def run_edge_cases() -> None:
    log_line("Edge-case checks", key="!proc")

    bad_json = HERE.parent / "_bad_config.json"
    bad_json.write_text("{", encoding="utf-8")
    try:
        config_loader.load_config(str(bad_json))
        log_line("Malformed JSON unexpectedly parsed.", key="!error")
    except Exception as exc:
        log_line(f"Malformed JSON rejected as expected: {exc}", key="!done")
    finally:
        bad_json.unlink(missing_ok=True)


def run_compositor_demo() -> None:
    log_line("Launching compositor capture demo (headless)...", key="!proc")
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, str(HERE.parent / "compositor_examples.py"),
             "--demo", "capture", "--no-clear"],
            capture_output=True, text=True,
        )
        for line in result.stdout.splitlines():
            log_line(line, key="!info")
        if result.returncode != 0:
            log_line(f"Compositor demo exited {result.returncode}", key="!error")
            for line in result.stderr.splitlines():
                log_line(line, key="!error")
        else:
            log_line("Compositor demo completed.", key="!done")
    except Exception as exc:
        log_line(f"Could not run compositor demo: {exc}", key="!error")


def menu_loop() -> None:
    while True:
        print()
        log_line("1. Config and path report", key="!list")
        log_line("2. tUilKit factory demo", key="!list")
        log_line("3. Edge-case checks", key="!list")
        log_line("4. Compositor capture demo", key="!list")
        log_line("5. Exit", key="!list")

        choice = input("Select option (1-5): ").strip()
        if choice == "1":
            show_config_and_paths()
        elif choice == "2":
            run_factory_demo()
        elif choice == "3":
            run_edge_cases()
        elif choice == "4":
            run_compositor_demo()
        elif choice == "5":
            log_line("Exiting exemplar.", key="!done")
            return
        else:
            log_line("Invalid choice.", key="!error")


def main() -> int:
    draw_header()
    log_line("Loaded tUilKit factories in exemplar mode.", key="!done")
    menu_loop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
