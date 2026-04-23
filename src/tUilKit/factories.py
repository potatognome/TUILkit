
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
        from tUilKit.utils.output import Logger
        colour_manager = get_colour_manager()
        config_loader = get_config_loader()
        root_modes = config_loader.global_config.get("ROOT_MODES", {})
        log_root_mode = root_modes.get("LOGS", "project")
        log_files_dict = config_loader.global_config.get("LOG_FILES", {})
        resolved_log_files = {}
        if log_root_mode == "workspace":
            workspace_root = os.path.abspath(os.path.join(os.getcwd(), "../../"))
            for key in log_files_dict:
                if not os.path.isabs(log_files_dict[key]):
                    resolved_log_files[key] = os.path.join(workspace_root, log_files_dict[key])
                else:
                    resolved_log_files[key] = log_files_dict[key]
        elif log_root_mode == "auto":
            workspace_root = os.path.abspath(os.path.join(os.getcwd(), "../../"))
            for key in log_files_dict:
                if not os.path.isabs(log_files_dict[key]):
                    resolved_log_files[key] = os.path.join(workspace_root, log_files_dict[key])
                else:
                    resolved_log_files[key] = log_files_dict[key]
        elif log_root_mode == "project":
            project_root = os.path.abspath(os.path.join(os.getcwd(), "Dev", "tUilKit"))
            for key in log_files_dict:
                if not os.path.isabs(log_files_dict[key]):
                    resolved_log_files[key] = os.path.join(project_root, log_files_dict[key])
                else:
                    resolved_log_files[key] = log_files_dict[key]
        else:
            resolved_log_files = log_files_dict
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
