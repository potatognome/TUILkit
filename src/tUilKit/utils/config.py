
"""
Minimal ConfigLoader for tUilKit: delegates all path logic to ConfigPathResolver, essential methods only.
"""
import os
import json
from tUilKit.interfaces.config_loader_interface import ConfigLoaderInterface
from tUilKit.interfaces.file_system_interface import FileSystemInterface
from tUilKit.utils.config_path_resolver import ConfigPathResolver

class ConfigLoader(ConfigLoaderInterface):
    def __init__(self, verbose=False, config_path=None):
        self.verbose = verbose
        # Step 1: If explicit config_path is provided, use it directly
        if config_path:
            if self.verbose:
                print(f"[ConfigLoader] Using explicit config_path: {config_path}")
            resolved_config_path = os.path.abspath(config_path) if not os.path.isabs(config_path) else config_path
            if not os.path.exists(resolved_config_path):
                raise FileNotFoundError(f"Config file not found: {resolved_config_path}")
            self.config_path = resolved_config_path
            self.bootstrap_path = resolved_config_path
            self.bootstrap_data = {"root_mode": "project", "config_path": resolved_config_path}
        else:
            # Fallback to bootstrap logic
            bootstrap_result = self._find_bootstrap_file()
            if bootstrap_result is not None:
                bootstrap_path, bootstrap_data = bootstrap_result
                self.bootstrap_path = bootstrap_path
                self.bootstrap_data = bootstrap_data
                self.root_mode = bootstrap_data.get("root_mode", "project")
                self.config_path = self._resolve_config_path()
            else:
                # No bootstrap file found, search for *CONFIG.json in project-level config folder
                import glob
                project_config_dir = os.path.abspath(os.path.join(os.getcwd(), "config"))
                config_candidates = glob.glob(os.path.join(project_config_dir, "*CONFIG.json"))
                if config_candidates:
                    self.config_path = config_candidates[0]
                else:
                    raise FileNotFoundError(f"No bootstrap file and no *CONFIG.json found in {project_config_dir}")
                self.bootstrap_path = self.config_path
                self.bootstrap_data = {"root_mode": "project", "config_path": self.config_path}
                self.root_mode = self.bootstrap_data.get("root_mode", "project")
        if self.verbose:
            print(f"[ConfigLoader VERBOSE] Final config_path: {self.config_path}")
        config_data = self._load_json(self.config_path)
        self.global_config = config_data
        roots_cfg = config_data.get("ROOTS", {})
        paths_cfg = config_data.get("PATHS", {})
        root_modes = config_data.get("ROOT_MODES", {})
        self.path_resolver = ConfigPathResolver(
            config_root_mode=root_modes.get("CONFIG", getattr(self, 'root_mode', 'project')),
            workspace_root_path=roots_cfg.get("WORKSPACE", os.getcwd()),
            project_root_path=roots_cfg.get("PROJECT", os.getcwd()),
            relative_folder_paths=paths_cfg
        )


    def _find_bootstrap_file(self):
        """
        Find and load the bootstrap file (test_paths.json) for test override.
        Returns (bootstrap_path, bootstrap_data)
        """
        cwd = os.getcwd()
        # Check for test_paths.json (test override)
        test_paths_path = os.path.join(cwd, "test_paths.json")
        if os.path.exists(test_paths_path):
            with open(test_paths_path, "r", encoding="utf-8") as f:
                test_paths = json.load(f)
            # Allow test_paths.json to specify a bootstrap_path or config_path
            bootstrap_path = test_paths.get("bootstrap_path")
            if bootstrap_path and os.path.exists(bootstrap_path):
                if self.verbose:
                    print(f"[ConfigLoader] Using bootstrap_path from test_paths.json: {bootstrap_path}")
                with open(bootstrap_path, "r", encoding="utf-8") as f:
                    bootstrap_data = json.load(f)
                return bootstrap_path, bootstrap_data
            # Fallback: synthesize bootstrap_data from test_paths.json
            config_path = test_paths.get("config_path") or os.path.join(test_paths.get("tests_config_folder", cwd), "tUilKit_CONFIG.json")
            bootstrap_data = {
                "root_mode": "project",
                "config_path": config_path
            }
            if self.verbose:
                print(f"[ConfigLoader] Using test_paths.json for bootstrap: {bootstrap_data}")
            return test_paths_path, bootstrap_data

    def _resolve_config_path(self):
        config_path = self.bootstrap_data.get("config_path")
        if self.verbose:
            print(f"[ConfigLoader VERBOSE] Bootstrap config_path: {config_path}")
            print(f"[ConfigLoader VERBOSE] root_mode: {self.root_mode}")
        if not config_path:
            raise ValueError("No config_path in bootstrap file.")
        # If not absolute, resolve relative to bootstrap file
        if not os.path.isabs(config_path):
            resolved_path = os.path.join(os.path.dirname(self.bootstrap_path), config_path)
            if self.verbose:
                print(f"[ConfigLoader VERBOSE] Resolved relative config_path: {resolved_path}")
            config_path = resolved_path
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")
        if self.verbose:
            print(f"[ConfigLoader VERBOSE] Final config_path: {config_path}")
        return config_path

    def _load_json(self, path):
        if self.verbose:
            print(f"[ConfigLoader] Loading JSON: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_config(self, json_file_path: str) -> dict:
        if getattr(self, 'verbose', False):
            print(f"[ConfigLoader VERBOSE] Opening config file: {json_file_path}")
        with open(json_file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def ensure_folders_exist(self, file_system: FileSystemInterface):
        log_files = self.global_config.get("LOG_FILES", {})
        for log_path in log_files.values():
            folder = os.path.dirname(log_path)
            if folder:
                file_system.validate_and_create_folder(folder, category="fs")

    def get_config_file_path(self, config_key: str) -> str:
        shared_config = self.global_config.get("SHARED_CONFIG", {})
        shared_enabled = shared_config.get("ENABLED", False)
        shared_path = shared_config.get("PATH", "GLOBAL_SHARED.d/")
        shared_files = shared_config.get("FILES", {})
        roots_cfg = self.global_config.get("ROOTS", {})
        paths_cfg = self.global_config.get("PATHS", {})
        root_modes = self.global_config.get("ROOT_MODES", {})
        root_mode = root_modes.get("CONFIG", "project")
        # Determine root folder
        if root_mode == "workspace":
            root_folder = roots_cfg.get("WORKSPACE", os.getcwd())
        else:
            root_folder = roots_cfg.get("PROJECT", os.getcwd())
        # Construct full path for shared config
        if shared_enabled and config_key in shared_files:
            shared_file = shared_files[config_key]
            shared_folder = os.path.join(root_folder, paths_cfg.get("CONFIG", ""), shared_path)
            full_path = os.path.join(shared_folder, shared_file)
            if getattr(self, 'verbose', False):
                print(f"[ConfigLoader VERBOSE] Constructed shared config path for '{config_key}': {full_path}")
            if os.path.exists(full_path):
                return full_path
            else:
                if getattr(self, 'verbose', False):
                    print(f"[ConfigLoader VERBOSE] Shared config file '{config_key}' not found at: {full_path}")
                raise FileNotFoundError(f"Shared config file '{config_key}' not found at: {full_path}")
        # Fallback for non-shared configs
        config_files = self.global_config.get("CONFIG_FILES", {})
        relative_path = config_files.get(config_key)
        if not relative_path:
            raise ValueError(f"Config file key '{config_key}' not found.")
        path = self.path_resolver.resolve_config_path(relative_path)
        if getattr(self, 'verbose', False):
            print(f"[ConfigLoader VERBOSE] Resolved config path for '{config_key}': {path}")
        if path:
            return path
        raise FileNotFoundError(f"Config file '{config_key}' not found.")

    def get_json_path(self, file: str, cwd: bool = False) -> str:
        path = self.path_resolver.resolve_config_path(file)
        if path:
            return path
        raise FileNotFoundError(f"Config file '{file}' not found.")

    def get_log_file_path(self, log_key: str) -> str:
        log_files = self.global_config.get("LOG_FILES", {})
        return log_files.get(log_key)

    def get_test_log_file_path(self, test_log_key: str) -> str:
        test_log_files = self.global_config.get("TEST_LOG_FILES", {})
        return test_log_files.get(test_log_key)

    def load_colour_config(self) -> dict:
        colour_config_path = self.get_config_file_path("COLOURS")
        if getattr(self, 'verbose', False):
            print(f"[ConfigLoader VERBOSE] Loading COLOURS config from: {colour_config_path}")
        return self.load_config(colour_config_path)

    def load_border_patterns_config(self) -> dict:
        try:
            border_patterns_path = self.get_config_file_path("BORDER_PATTERNS")
            if getattr(self, 'verbose', False):
                print(f"[ConfigLoader VERBOSE] Loading BORDER_PATTERNS config from: {border_patterns_path}")
            return self.load_config(border_patterns_path)
        except FileNotFoundError:
            if getattr(self, 'verbose', False):
                print(f"[ConfigLoader VERBOSE] BORDER_PATTERNS config not found.")
            return {}

    def _bootstrap_config_path(self, file: str) -> str:
        # Minimal bootstrap logic for initial config load
        import os
        from pathlib import Path
        current_dir = Path(os.getcwd())
        root_path = current_dir / file
        if getattr(self, 'verbose', False):
            print(f"[ConfigLoader VERBOSE] Checking bootstrap path: {root_path} ...", end=" ")
        if root_path.exists():
            if getattr(self, 'verbose', False):
                print("SUCCESS")
            return str(root_path)
        else:
            if getattr(self, 'verbose', False):
                print("NOT FOUND.. SKIPPING")
        config_path = current_dir / "config" / file
        if getattr(self, 'verbose', False):
            print(f"[ConfigLoader VERBOSE] Checking bootstrap config path: {config_path} ...", end=" ")
        if config_path.exists():
            if getattr(self, 'verbose', False):
                print("SUCCESS")
            return str(config_path)
        else:
            if getattr(self, 'verbose', False):
                print("NOT FOUND.. SKIPPING")
        for parent in current_dir.parents:
            parent_config = parent / "config" / file
            if getattr(self, 'verbose', False):
                print(f"[ConfigLoader VERBOSE] Checking parent bootstrap config path: {parent_config} ...", end=" ")
            if parent_config.exists():
                if getattr(self, 'verbose', False):
                    print("SUCCESS")
                return str(parent_config)
            else:
                if getattr(self, 'verbose', False):
                    print("NOT FOUND.. SKIPPING")
        fallback_abs = os.path.abspath(os.path.join(os.getcwd(), "Dev", "tUilKit", "config", file))
        if getattr(self, 'verbose', False):
            print(f"[ConfigLoader VERBOSE] Checking fallback bootstrap config path: {fallback_abs} ...", end=" ")
        if os.path.exists(fallback_abs):
            if getattr(self, 'verbose', False):
                print("SUCCESS")
            return fallback_abs
        else:
            if getattr(self, 'verbose', False):
                print("NOT FOUND.. SKIPPING")
        raise FileNotFoundError(f"Config file '{file}' not found in expected locations.")