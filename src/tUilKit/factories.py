
# src/tUilKit/factories.py

"""
Factory functions for creating and initializing tUilKit components.
Encapsulates setup logic and provides convenient one-liner instantiation.
"""

import os
import json

_config_loader = None
_colour_manager = None
_logger = None
_file_system = None
_cli_menu_handler = None

def get_config_loader():
    global _config_loader
    if _config_loader is None:
        from tUilKit.utils.config import ConfigLoader
        _config_loader = ConfigLoader()
    return _config_loader

def get_colour_manager():
    """
    Get or create the singleton ColourManager instance.
    Initializes colour mappings from the loaded colour configuration.
    """
    global _colour_manager
    if _colour_manager is None:
        from tUilKit.utils.output import ColourManager
        # Allow optional override via merged config key 'colourKeyPath'
        config_loader = get_config_loader()
        colour_config = None
        try:
            global_cfg = getattr(config_loader, 'global_config', {}) or {}
            colour_override = global_cfg.get('colourKeyPath') if isinstance(global_cfg, dict) else None
        except Exception:
            colour_override = None

        if colour_override:
            try:
                # Absolute path
                if os.path.isabs(colour_override) and os.path.exists(colour_override):
                    with open(colour_override, 'r', encoding='utf-8') as fh:
                        colour_config = json.load(fh)
                else:
                    # Try resolving via ConfigLoader helpers
                    try:
                        resolved = config_loader.get_json_path(colour_override)
                        colour_config = config_loader.load_config(resolved)
                    except Exception:
                        # Fallback to relative path from cwd
                        rel = os.path.join(os.getcwd(), colour_override)
                        if os.path.exists(rel):
                            with open(rel, 'r', encoding='utf-8') as fh:
                                colour_config = json.load(fh)
            except Exception:
                colour_config = None

        if not colour_config:
            colour_config = config_loader.load_colour_config()

        _colour_manager = ColourManager(colour_config)
    return _colour_manager

def get_logger(*args, **kwargs):
    """
    Get or create the singleton Logger instance.
    Accepts optional positional/keyword arguments (e.g., a logger name)
    for compatibility with callers that pass `__name__`.
    """
    global _logger
    if _logger is None:
        from tUilKit.utils.output import Logger, _resolve_log_files_from_config
        colour_manager = get_colour_manager()
        config_loader = get_config_loader()
        resolved_log_files = _resolve_log_files_from_config(config_loader)
        _logger = Logger(colour_manager, log_files=resolved_log_files)
    return _logger

def get_file_system():
    """
    Get or create the singleton FileSystem instance.
    """
    global _file_system
    if _file_system is None:
        from tUilKit.utils.fs import FileSystem
        _file_system = FileSystem()
    return _file_system

def get_cli_menu_handler():
    """
    Get or create the singleton CLIMenuHandler instance.
    Fully initialized with Logger for colour-coded menu output.
    """
    global _cli_menu_handler
    if _cli_menu_handler is None:
        from tUilKit.utils.cli_menus import CLIMenuHandler
        logger = get_logger()
        _cli_menu_handler = CLIMenuHandler(logger)
    return _cli_menu_handler

def reset_factories():
    """
    Reset all singleton instances. Useful for testing.
    """
    global _config_loader, _colour_manager, _logger, _file_system, _cli_menu_handler
    _config_loader = None
    _colour_manager = None
    _logger = None
    _file_system = None
    _cli_menu_handler = None
