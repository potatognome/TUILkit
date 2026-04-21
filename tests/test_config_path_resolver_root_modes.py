from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from tUilKit.utils.config_path_resolver import ConfigPathResolver


def test_resolve_config_path_uses_workspace_mode_first(tmp_path):
    workspace = tmp_path / "workspace"
    project = workspace / "Core" / "tUilKit"

    workspace_config = workspace / "config" / "sample.json"
    project_config = project / "config" / "sample.json"
    workspace_config.parent.mkdir(parents=True)
    project_config.parent.mkdir(parents=True)
    workspace_config.write_text("{}", encoding="utf-8")
    project_config.write_text("{}", encoding="utf-8")

    resolver = ConfigPathResolver(
        config_root_mode="workspace",
        workspace_root_path=str(workspace),
        project_root_path=str(project),
    )

    resolved = resolver.resolve_config_path("sample.json")

    assert resolved == str(workspace_config)


def test_resolve_config_path_uses_project_mode_first(tmp_path):
    workspace = tmp_path / "workspace"
    project = workspace / "Core" / "tUilKit"

    project_config = project / "config" / "sample.json"
    project_config.parent.mkdir(parents=True)
    project_config.write_text("{}", encoding="utf-8")

    resolver = ConfigPathResolver(
        config_root_mode="project",
        workspace_root_path=str(workspace),
        project_root_path=str(project),
    )

    resolved = resolver.resolve_config_path("sample.json")

    assert resolved == str(project_config)
