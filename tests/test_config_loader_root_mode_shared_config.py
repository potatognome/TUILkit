from pathlib import Path
import json
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from tUilKit.utils.config import ConfigLoader


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _base_config(workspace: Path, project: Path, config_mode: str) -> dict:
    return {
        "ROOTS": {
            "WORKSPACE": str(workspace),
            "PROJECT": str(project),
        },
        "ROOT_MODES": {
            "CONFIG": config_mode,
        },
        "PATHS": {
            "CONFIG": "config",
        },
        "SHARED_CONFIG": {
            "ENABLED": True,
            "PATH": "GLOBAL_SHARED.d",
            "FILES": {
                "COLOURS": "COLOURS.json",
            },
        },
        "CONFIG_FILES": {
            "LOCAL_ONLY": "local.json",
        },
        "LOG_FILES": {
            "MASTER": "master.log",
        },
    }


def test_loader_shared_config_uses_workspace_when_root_mode_workspace(tmp_path):
    workspace = tmp_path / "workspace"
    project = workspace / "Core" / "tUilKit"

    workspace_colours = workspace / "config" / "GLOBAL_SHARED.d" / "COLOURS.json"
    project_colours = project / "config" / "GLOBAL_SHARED.d" / "COLOURS.json"
    _write_json(workspace_colours, {"palette": "workspace"})
    _write_json(project_colours, {"palette": "project"})

    config_path = project / "config" / "tUilKit_CONFIG.json"
    _write_json(config_path, _base_config(workspace, project, "workspace"))

    loader = ConfigLoader(config_path=str(config_path))
    resolved = loader.get_config_file_path("COLOURS")

    assert resolved == str(workspace_colours)


def test_loader_shared_config_uses_project_when_root_mode_project(tmp_path):
    workspace = tmp_path / "workspace"
    project = workspace / "Core" / "tUilKit"

    workspace_colours = workspace / "config" / "GLOBAL_SHARED.d" / "COLOURS.json"
    project_colours = project / "config" / "GLOBAL_SHARED.d" / "COLOURS.json"
    _write_json(workspace_colours, {"palette": "workspace"})
    _write_json(project_colours, {"palette": "project"})

    config_path = project / "config" / "tUilKit_CONFIG.json"
    _write_json(config_path, _base_config(workspace, project, "project"))

    loader = ConfigLoader(config_path=str(config_path))
    resolved = loader.get_config_file_path("COLOURS")

    assert resolved == str(project_colours)
