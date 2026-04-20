# Lib/site-packages/tUilKit/utils/fs.py
"""
Contains functions for managing files, folders and path names.
Provides implementation of FileSystemInterface with logging support using colour keys.
"""

import shutil
import os
import sys
from pathlib import Path

from tUilKit.interfaces.file_system_interface import FileSystemInterface
from tUilKit.utils.config import ConfigLoader

class FileSystem(FileSystemInterface):
    def __init__(self, logger=None, log_files=None):
        """
        Initializes the FileSystem with a logger and optional log_files dict.
        """
        from tUilKit.utils.output import Logger
        config_loader = ConfigLoader()
        self.logger = logger or Logger()
        root_modes = config_loader.global_config.get("ROOT_MODES", {})
        log_root_mode = root_modes.get("LOGS", "project")
        log_files_dict = log_files or config_loader.global_config.get("LOG_FILES", {})
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
        super().__init__(self.logger, resolved_log_files)
        self.LOG_KEYS = config_loader.global_config.get("LOG_CATEGORIES", {
            "default": ["MASTER", "SESSION"],
            "error": ["ERROR", "SESSION", "MASTER"],
            "fs": ["MASTER", "SESSION", "FS"]
        })


    def __init__(self, logger=None, log_files=None):
        """
        Initializes the FileSystem with a logger and optional log_files dict.
        """
        from tUilKit.utils.output import Logger, ColourManager
        config_loader = ConfigLoader()
        if logger is not None:
            self.logger = logger
        else:
            colour_config = config_loader.load_colour_config() if hasattr(config_loader, 'load_colour_config') else {}
            colour_manager = ColourManager(colour_config)
            self.logger = Logger(colour_manager)
        log_files = log_files or config_loader.global_config.get("LOG_FILES", {})
        super().__init__(self.logger, log_files)
        self.LOG_KEYS = config_loader.global_config.get("LOG_CATEGORIES", {
            "default": ["MASTER", "SESSION"],
            "error": ["ERROR", "SESSION", "MASTER"],
            "fs": ["MASTER", "SESSION", "FS"]
        })

    def _get_log_files(self, category="default"):
        """
        Returns a list of log file paths for the given category or categories.
        category can be str or list of str.
        """
        if isinstance(category, str):
            categories = [category]
        elif isinstance(category, list):
            categories = category
        else:
            categories = ["default"]
        all_files = []
        for cat in categories:
            keys = self.LOG_KEYS.get(cat, self.LOG_KEYS["default"])
            all_files.extend([self.log_files.get(key) for key in keys if self.log_files.get(key)])
        return list(set(all_files))  # unique

    def validate_and_create_folder(self, folder_path: str, log: bool = True, log_to: str = "both", category="fs") -> bool:
        """
        Validates and creates a folder if it does not exist.
        Logs the action using colour keys: !try for attempt, !create for action, !path for the path, !pass for success.
        """
        log_files = self._get_log_files(category)
        coloured_path = colourize_path(folder_path, self.logger.Colour_Mgr) if (self.logger and folder_path) else folder_path
        if not os.path.exists(folder_path):
            if self.logger and log:
                self.logger.colour_log("!try", "Attempting to", "!create", "create folder:", "!path", coloured_path, log_files=log_files, log_to=log_to, end="..... ")
            try:
                os.makedirs(folder_path, exist_ok=True)
                if self.logger and log:
                    self.logger.colour_log("!pass", "DONE!", log_files=log_files, log_to=log_to, time_stamp=False)
            except Exception as e:
                if self.logger and log:
                    self.logger.log_exception("!error", "Could not create folder: ", e, log_files=self._get_log_files("error"), log_to=log_to)
                return False
        return True

    def remove_empty_folders(self, path: str, log: bool = True, category="fs") -> None:
        """
        Recursively removes empty folders under the given path.
        Logs each removal using !pass and !path colour keys.
        """
        log_files = self._get_log_files(category)
        for root, dirs, files in os.walk(path, topdown=False):
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                coloured_path = colourize_path(dir_path, self.logger.Colour_Mgr) if (self.logger and dir_path) else dir_path
                if not os.listdir(dir_path):
                    try:
                        os.rmdir(dir_path)  
                    except Exception as e:
                        if self.logger and log:
                            self.logger.log_exception("!error", "Could not remove folder: ", e, log_files=self._get_log_files("error"))
                    if self.logger and log:
                        self.logger.colour_log("!pass", "Removed empty folder:", "!path", coloured_path, log_files=log_files)

    def get_all_files(self, folder: str) -> list[str]:
        """
        Returns a list of all files (not directories) in the specified folder.
        """
        return [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]

    def validate_extension(self, fullfilepath: str, extension: str) -> str:
        """
        Ensures the filepath has the specified extension.
        If not, appends it.
        """
        base, ext = os.path.splitext(fullfilepath)
        if ext.lower() != extension.lower():
            fullfilepath += extension
        return fullfilepath

    def no_overwrite(self, fullfilepath: str, max_count=None, log: bool = True, category="fs") -> str:
        """
        Guarantees that a newly generated file will not overwrite an existing file.
        Generates a non-overwriting filename by appending a counter in parentheses.
        If max_count is reached, returns the oldest file.
        Logs using !warn for max count, !done for success, with !path and !file keys.
        Use if you are not using version control and want to avoid overwriting files.
        """
        log_files = self._get_log_files(category)
        base, ext = os.path.splitext(fullfilepath)
        counter = 1
        new_fullfilepath = fullfilepath
        oldest_file = fullfilepath
        oldest_timestamp = os.path.getmtime(fullfilepath) if os.path.exists(fullfilepath) else float('inf')
        
        while os.path.exists(new_fullfilepath):
            new_fullfilepath = f"{base}({counter}){ext}"
            if os.path.exists(new_fullfilepath):
                file_timestamp = os.path.getmtime(new_fullfilepath)
                if file_timestamp < oldest_timestamp:
                    oldest_timestamp = file_timestamp
                    oldest_file = new_fullfilepath
            counter += 1
            if max_count and counter > max_count:
                if self.logger and log:
                    coloured_oldest_dir = colourize_path(os.path.dirname(oldest_file), self.logger.Colour_Mgr) if self.logger else os.path.dirname(oldest_file)
                    self.logger.colour_log(
                        "!warn",
                        "Max count reached, returning oldest file:",
                        "!path", coloured_oldest_dir,
                        "!file", os.path.basename(oldest_file),
                        log_files=log_files
                    )
                return oldest_file
        if self.logger and log:
            coloured_new_dir = colourize_path(os.path.dirname(new_fullfilepath), self.logger.Colour_Mgr) if self.logger else os.path.dirname(new_fullfilepath)
            self.logger.colour_log(
                "!done",
                "No-overwrite filename generated:",
                "!path", coloured_new_dir,
                "!file", os.path.basename(new_fullfilepath),
                log_files=log_files
            )
        return new_fullfilepath

    def backup_and_replace(self, full_pathname: str, backup_full_pathname: str, log: bool = True, category="fs") -> str:
        """
        Backs up the file and replaces it with an empty file.
        Logs using !done for success, !path and !file for paths.
        """
        log_files = self._get_log_files(category)
        if full_pathname and backup_full_pathname:
            if os.path.exists(full_pathname):
                shutil.copy2(full_pathname, backup_full_pathname)
                if self.logger and log:
                    coloured_backup_dir = colourize_path(os.path.dirname(backup_full_pathname), self.logger.Colour_Mgr) if self.logger else os.path.dirname(backup_full_pathname)
                    self.logger.colour_log("!done", "Backup created:", "!path", coloured_backup_dir, "!file", os.path.basename(backup_full_pathname), log_files=log_files)
                try:
                    with open(full_pathname, 'w') as file:
                        file.write('')
                    if self.logger and log:
                        coloured_full_dir = colourize_path(os.path.dirname(full_pathname), self.logger.Colour_Mgr) if self.logger else os.path.dirname(full_pathname)
                        self.logger.colour_log("!done", "File replaced:", "!path", coloured_full_dir, "!file", os.path.basename(full_pathname), log_files=log_files)
                except Exception as e:
                    if self.logger and log:
                        self.logger.log_exception("!error", "Generated Exception ", e, log_files=self._get_log_files("error"))
        return full_pathname

    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitizes a filename by replacing invalid characters with safe alternatives.
        """
        invalid_chars = {
            ':' : '-',
            '\\' : '',
            '/' : '',
            '?' : '',
            '*' : '',
            '<' : '',
            '>' : '',
            '|' : '',
        }
        new_filename = filename
        for char, replacement in invalid_chars.items():
            new_filename = new_filename.replace(char, replacement)
        return new_filename


def normalize_path(path: str, style: str = "auto") -> str:
    """Normalize a filesystem path for cross-platform display/use.

    Args:
        path: Input path (any separator mix).
        style: "auto" (platform default), "posix" (forward slashes), or "windows" (backslashes).

    Returns:
        Normalized path string.
    """
    if not path:
        return ""

    p = Path(path)
    if style == "posix":
        return p.as_posix()
    if style == "windows":
        return str(p).replace("/", "\\")

    # auto: honor current platform default separator
    return str(p)


def detect_os() -> str:
    """Return normalized OS name: "Windows", "Linux", or "Darwin" (macOS).

    Uses os.name/sys.platform to avoid platform module import. Intended for light
    branching in path display or logging.
    """
    # Fast path based on os.name
    if os.name == "nt":
        return "Windows"
    # sys.platform covers linux/darwin explicitly
    plat = sys.platform
    if plat.startswith("linux"):
        return "Linux"
    if plat == "darwin":
        return "Darwin"
    # Fallback to raw value
    return plat


def colourize_path(path: str, colour_manager, style: str = "auto") -> str:
    """Normalize a path and render it with colour manager's colour_path.

    Args:
        path: input filesystem path
        colour_manager: instance providing colour_path()
        style: normalization style passed to normalize_path

    Returns:
        Colour-formatted path string (or empty string if path is falsy).
    """
    if not path:
        return ""
    normalized = normalize_path(path, style=style)
    return colour_manager.colour_path(normalized)
