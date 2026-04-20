"""
Test: ConfigLoader fails gracefully for missing config keys
Purpose: Ensure ValueError is raised for unknown config keys.
"""
import os
import pytest
from tUilKit.utils.config import ConfigLoader

def test_missing_config_key():
    config_path = os.path.abspath(os.path.join(os.getcwd(), ".tests_config", "tUilKit_CONFIG.json"))
    loader = ConfigLoader(verbose=True, config_path=config_path)
    with pytest.raises(ValueError):
        loader.get_config_file_path("NON_EXISTENT_KEY")
