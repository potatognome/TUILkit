"""
Test: ConfigLoader resolves all SHARED_CONFIG files in canonical pattern
Purpose: Ensure all shared config files are found and loaded from .tests_config/GLOBAL_SHARED.d/.
"""
import os
import pytest
from tUilKit.utils.config import ConfigLoader

@pytest.mark.parametrize("config_key", [
    "COLOURS",
    "BORDER_PATTERNS",
    "TESTS_OPTIONS",
    "TIME_STAMP_OPTIONS"
])
def test_shared_config_resolution(config_key):
    config_path = os.path.abspath(os.path.join(os.getcwd(), ".tests_config", "tUilKit_CONFIG.json"))
    loader = ConfigLoader(verbose=True, config_path=config_path)
    path = loader.get_config_file_path(config_key)
    print(f"{config_key} resolved to: {path}")
    assert os.path.exists(path), f"{config_key} config not found at: {path}"
    data = loader.load_config(path)
    assert isinstance(data, dict)
