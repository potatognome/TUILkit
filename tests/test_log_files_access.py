"""
Test: ConfigLoader loads and prints all log file paths
Purpose: Ensure LOG_FILES section is parsed and paths are accessible.
"""
import os
from tUilKit.utils.config import ConfigLoader

def test_log_files_access():
    config_path = os.path.abspath(os.path.join(os.getcwd(), ".tests_config", "tUilKit_CONFIG.json"))
    loader = ConfigLoader(verbose=True, config_path=config_path)
    log_files = loader.global_config.get("LOG_FILES", {})
    assert log_files, "LOG_FILES section missing"
    for key, path in log_files.items():
        print(f"Log file key: {key}, path: {path}")
        assert isinstance(path, str)
