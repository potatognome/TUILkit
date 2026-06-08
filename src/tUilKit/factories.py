
# src/tUilKit/factories.py

"""
Factory functions for creating and initializing tUilKit components.
Encapsulates setup logic and provides convenient one-liner instantiation.
"""

import os


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
    global _colour_manager
    if _colour_manager is None:
        from tUilKit.utils.output import ColourManager
        _colour_manager = ColourManager(get_config_loader().load_colour_config())
    return _colour_manager


def get_logger():
    global _logger
    if _logger is None:
        from tUilKit.utils.output import Logger
        _logger = Logger(get_colour_manager())
    return _logger


def get_file_system():
    global _file_system
    if _file_system is None:
        from tUilKit.utils.fs import FileSystem
        _file_system = FileSystem(logger=get_logger())
    return _file_system


def get_cli_menu_handler():
    global _cli_menu_handler
    if _cli_menu_handler is None:
        from tUilKit.utils.cli_menus import CLIMenuHandler
        _cli_menu_handler = CLIMenuHandler(logger=get_logger())
    return _cli_menu_handler


def reset_factories():
    global _config_loader, _colour_manager, _logger, _file_system, _cli_menu_handler
    _config_loader = None
    _colour_manager = None
    _logger = None
    _file_system = None
    _cli_menu_handler = None


def get_colour_manager():
    """
    Get or create the singleton ColourManager instance.
    Initializes colour mappings from the loaded colour configuration.
    """
    global _colour_manager
    if _colour_manager is None:
        from tUilKit.utils.output import ColourManager
        _colour_manager = ColourManager(get_config_loader().load_colour_config())
    return _colour_manager


def get_logger():
    """
    Get or create the singleton Logger instance.
    Fully initialized with ColourManager and log file paths from config.
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
