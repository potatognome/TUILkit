"""
Test: ConfigLoader fails gracefully for missing config keys
Purpose: Ensure ValueError is raised for unknown config keys.
"""
from pathlib import Path
import sys
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from tUilKit.utils.config import ConfigLoader

def test_missing_config_key():
    config_path = PROJECT_ROOT / "config" / "tUilKit_CONFIG.json"
    loader = ConfigLoader(verbose=True, config_path=config_path)
    with pytest.raises(ValueError):
        loader.get_config_file_path("NON_EXISTENT_KEY")
