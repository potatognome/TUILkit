"""
ConfigPathResolver: Helper class for resolving config file paths based on tUilKit_CONFIG.json settings.
"""
import os
from pathlib import Path

class ConfigPathResolver:
    def __init__(self, config_root_mode="project", workspace_root_path=None, project_root_path=None, relative_folder_paths=None):
        self.config_root_mode = config_root_mode
        self.workspace_root_path = workspace_root_path
        self.project_root_path = project_root_path
        self.relative_folder_paths = relative_folder_paths or {}

    def resolve_config_path(self, file_name, verbose=False):
        if verbose:
            print(f"[ConfigPathResolver VERBOSE] config_root_mode: {self.config_root_mode}")
            print(f"[ConfigPathResolver VERBOSE] workspace_root_path: {self.workspace_root_path}")
            print(f"[ConfigPathResolver VERBOSE] project_root_path: {self.project_root_path}")
            print(f"[ConfigPathResolver VERBOSE] file_name: {file_name}")
        # Root mode is default: workspace/project root first
        if self.config_root_mode == "workspace" and self.workspace_root_path:
            fallback = Path(self.workspace_root_path) / "config" / file_name
            if verbose:
                print(f"[ConfigPathResolver VERBOSE] Checking workspace config path: {fallback}", end="...")
            if fallback.exists():
                if verbose:
                    print("Found!")
                return str(fallback)
        elif self.config_root_mode == "project" and self.project_root_path:
            fallback = Path(self.project_root_path) / "config" / file_name
            if verbose:
                print("Not found.\n")
                print(f"[ConfigPathResolver VERBOSE] Checking project config path: {fallback}", end="...")
            if fallback.exists():
                if verbose:
                    print("Found!")
                return str(fallback)
        # Fallback to cwd/config/parent if root mode fails
        current_dir = Path(os.getcwd())
        root_path = current_dir / file_name
        if verbose:
            print("Not found.\n")
            print(f"[ConfigPathResolver VERBOSE] Checking cwd root path: {root_path}", end="...")
        if root_path.exists():
            if verbose:
                print("Found!")
            return str(root_path)
        config_path = current_dir / "config" / file_name
        if verbose:
            print("Not found.\n")
            print(f"[ConfigPathResolver VERBOSE] Checking cwd config path: {config_path}", end="...")
        if config_path.exists():
            if verbose:
                print("Found!")
            return str(config_path)
        for parent in current_dir.parents:
            parent_config = parent / "config" / file_name
            if verbose:                
                print("Not found.\n")
                print(f"[ConfigPathResolver VERBOSE] Checking parent config path: {parent_config}", end="...")
            if parent_config.exists():
                if verbose:
                    print("Found!")
                return str(parent_config)
        # Absolute fallback
        fallback_abs = os.path.abspath(os.path.join(os.getcwd(), "Dev", "tUilKit", "config", file_name))
        if verbose:
            print("Not found.\n")
            print(f"[ConfigPathResolver VERBOSE] Checking absolute fallback: {fallback_abs}", end="...")
        if os.path.exists(fallback_abs):
            if verbose:
                print("Found!")
            return fallback_abs
        if verbose:
            print("Not found.\n")
            print(f"[ConfigPathResolver VERBOSE] No config path found for: {file_name}")
        return None

    def resolve_shared_config_path(self, config_key, shared_config_files, shared_folder):
        shared_path = shared_config_files.get(config_key)
        if not shared_path:
            return None
        abs_path = os.path.abspath(os.path.join(shared_folder, shared_path))
        if os.path.exists(abs_path):
            return abs_path
        cwd_path = os.path.abspath(os.path.join(os.getcwd(), shared_folder, shared_path))
        if os.path.exists(cwd_path):
            return cwd_path
        dev_shared_path = os.path.abspath(os.path.join(os.getcwd(), "Dev", "tUilKit", shared_folder, shared_path))
        if os.path.exists(dev_shared_path):
            return dev_shared_path
        return None
