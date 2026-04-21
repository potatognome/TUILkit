"""
Test: ConfigLoader resolves all SHARED_CONFIG files in canonical pattern
Purpose: Ensure all shared config files are found and loaded from .tests_config/GLOBAL_SHARED.d/.
"""
from pathlib import Path
import sys
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from tUilKit.utils.config import ConfigLoader

@pytest.mark.parametrize("config_key", [
    "COLOURS",
    "TESTS_OPTIONS",
    "TIME_STAMP_OPTIONS"
])
def test_shared_config_resolution(config_key):
    config_path = PROJECT_ROOT / "config" / "tUilKit_CONFIG.json"
    loader = ConfigLoader(verbose=True, config_path=config_path)
    path = loader.get_config_file_path(config_key)
    print(f"{config_key} resolved to: {path}")
    assert Path(path).exists(), f"{config_key} config not found at: {path}"
    data = loader.load_config(path)
    assert isinstance(data, dict)
