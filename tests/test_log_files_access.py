"""
Test: ConfigLoader loads and prints all log file paths
Purpose: Ensure LOG_FILES section is parsed and paths are accessible.
"""
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from tUilKit.utils.config import ConfigLoader

def test_log_files_access():
    config_path = PROJECT_ROOT / "config" / "tUilKit_CONFIG.json"
    loader = ConfigLoader(verbose=True, config_path=config_path)
    log_files = loader.global_config.get("LOG_FILES", {})
    assert log_files, "LOG_FILES section missing"
    for key, path in log_files.items():
        print(f"Log file key: {key}, path: {path}")
        assert isinstance(path, str)
