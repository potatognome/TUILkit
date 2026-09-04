"""
Contains functions for log files and displaying text output in the terminal using ANSI sequences to colour code output.
"""

import os
import uuid
from collections import deque
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional
from tUilKit.dict.DICT_COLOURS import RGB
from tUilKit.dict.DICT_CODES import ESCAPES, COMMANDS
from tUilKit.interfaces.logger_interface import LoggerInterface
from tUilKit.interfaces.colour_interface import ColourInterface
from tUilKit.utils.config import ConfigLoader
from pathlib import Path
import json
import copy

# ANSI ESCAPE CODE PREFIXES for colour coding f-strings
SET_FG_COLOUR = ESCAPES['OCTAL'] + COMMANDS['FGC']
SET_BG_COLOUR = ESCAPES['OCTAL'] + COMMANDS['BGC']
ANSI_RESET = ESCAPES['OCTAL'] + COMMANDS['RESET']


def _resolve_log_files_from_config(loader: ConfigLoader) -> dict:
    cfg = loader.global_config if isinstance(loader.global_config, dict) else {}
    roots_cfg = cfg.get("ROOTS", {}) if isinstance(cfg.get("ROOTS", {}), dict) else {}
    paths_cfg = cfg.get("PATHS", {}) if isinstance(cfg.get("PATHS", {}), dict) else {}
    root_modes = cfg.get("ROOT_MODES", {}) if isinstance(cfg.get("ROOT_MODES", {}), dict) else {}
    log_files = copy.deepcopy(cfg.get("LOG_FILES", {})) if isinstance(cfg.get("LOG_FILES", {}), dict) else {}

    mode = str(root_modes.get("LOG_PATHS", root_modes.get("LOGS", "project"))).strip().lower()
    logs_rel = paths_cfg.get("LOG_PATHS") or paths_cfg.get("LOGS") or ".logs/tUilKit/"

    if os.path.isabs(str(logs_rel)):
        logs_root = str(logs_rel)
    else:
        if mode == "workspace":
            root_base = roots_cfg.get("WORKSPACE", os.getcwd())
        else:
            root_base = roots_cfg.get("PROJECT", os.getcwd())
        logs_root = os.path.join(str(root_base), str(logs_rel))

    logs_root = os.path.abspath(logs_root)

    resolved = {}
    for key, value in log_files.items():
        if not isinstance(value, str) or not value.strip():
            continue
        if os.path.isabs(value):
            resolved[key] = value
        else:
            resolved[key] = os.path.abspath(os.path.join(logs_root, value))
    return resolved


def _resolve_tuilkit_session_log(loader: ConfigLoader) -> str:
    cfg = loader.global_config if isinstance(loader.global_config, dict) else {}
    roots_cfg = cfg.get("ROOTS", {}) if isinstance(cfg.get("ROOTS", {}), dict) else {}
    log_files = cfg.get("LOG_FILES", {}) if isinstance(cfg.get("LOG_FILES", {}), dict) else {}

    workspace_root = os.path.abspath(str(roots_cfg.get("WORKSPACE", os.getcwd())))
    session_name = str(log_files.get("SESSION", "tUilKit_SESSION.log"))
    session_basename = os.path.basename(session_name)
    return os.path.join(workspace_root, ".logs", "tUilKit", session_basename)


try:
    config_loader = ConfigLoader()
    LOG_FILES = _resolve_log_files_from_config(config_loader)
    TUILKIT_SESSION_LOG = _resolve_tuilkit_session_log(config_loader)
except Exception:
    config_loader = None
    LOG_FILES = {}
    TUILKIT_SESSION_LOG = None


@dataclass
class LogEntry:
    event_id: str
    timestamp_utc: str
    local_timestamp: str
    severity: str
    verbosity: str
    category: str
    subcategory: str = ""
    app_id: str = "tuilkit"
    component: str = "logger"
    module: str = ""
    session_id: str = ""
    correlation_id: str = ""
    parent_event_id: str = ""
    source_layer: str = "tuilkit"
    target: str = "terminal"
    file_path: str = ""
    message: str = ""
    raw_message: str = ""
    rendered_text: str = ""
    palette_key: str = ""
    palette_version: str = "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)
    output_targets: List[str] = field(default_factory=list)
    dedupe_key: str = ""

    @staticmethod
    def normalize_metadata(metadata: Optional[Dict[str, Any]] = None, **overrides: Any) -> Dict[str, Any]:
        """Normalize metadata keys to the canonical schema used by tUilKit."""
        raw = {} if metadata is None else dict(metadata)
        for key, value in overrides.items():
            if value is not None:
                raw[key] = value

        alias_map = {
            "session": "session_id",
            "session_id": "session_id",
            "trace_id": "correlation_id",
            "correlation_id": "correlation_id",
            "level": "severity",
            "severity": "severity",
            "log_level": "verbosity",
            "verbosity": "verbosity",
            "logger_name": "category",
            "category": "category",
            "output_target": "target",
            "target": "target",
            "origin": "source_layer",
            "source_layer": "source_layer",
            "app": "app_id",
            "app_id": "app_id",
        }

        normalized: Dict[str, Any] = {}
        for key, value in raw.items():
            if value is None:
                continue
            canonical = alias_map.get(str(key), str(key))
            if canonical == "severity" and isinstance(value, str):
                normalized[canonical] = value.upper()
            elif canonical == "verbosity" and isinstance(value, str):
                normalized[canonical] = value.upper()
            else:
                normalized[canonical] = value
        return normalized

    @classmethod
    def from_message(
        cls,
        message: Any,
        *,
        category: str = "default",
        severity: Optional[str] = None,
        verbosity: Optional[str] = None,
        app_id: Optional[str] = None,
        component: str = "logger",
        module: str = "",
        session_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        source_layer: str = "tuilkit",
        target: str = "terminal",
        file_path: str = "",
        output_targets: Optional[Iterable[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        palette_key: str = "",
        palette_version: str = "unknown",
        parent_event_id: str = "",
    ) -> "LogEntry":
        normalized_meta = cls.normalize_metadata(metadata or {})
        ts = datetime.now(timezone.utc)
        timestamp_utc = ts.strftime("%Y-%m-%dT%H:%M:%SZ")
        local_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        event_id = str(uuid.uuid4())
        entry_msg = "" if message is None else str(message)
        resolved_severity = (severity or normalized_meta.get("severity") or "INFO").upper()
        resolved_verbosity = (verbosity or normalized_meta.get("verbosity") or "STANDARD").upper()
        resolved_session = session_id or normalized_meta.get("session_id") or ""
        resolved_correlation = correlation_id or normalized_meta.get("correlation_id") or resolved_session
        resolved_app = app_id or normalized_meta.get("app_id") or "tuilkit"
        resolved_target = target or normalized_meta.get("target") or "terminal"
        resolved_source = source_layer or normalized_meta.get("source_layer") or "tuilkit"
        resolved_targets = list(output_targets) if output_targets else []
        dedupe_key = "|".join(
            filter(None, [
                resolved_app,
                resolved_session,
                resolved_correlation,
                category,
                resolved_severity,
                entry_msg,
            ])
        )
        return cls(
            event_id=event_id,
            timestamp_utc=timestamp_utc,
            local_timestamp=local_timestamp,
            severity=resolved_severity,
            verbosity=resolved_verbosity,
            category=category,
            subcategory="",
            app_id=resolved_app,
            component=component,
            module=module,
            session_id=resolved_session,
            correlation_id=resolved_correlation,
            parent_event_id=parent_event_id,
            source_layer=resolved_source,
            target=resolved_target,
            file_path=file_path,
            message=entry_msg,
            raw_message=entry_msg,
            rendered_text=entry_msg,
            palette_key=palette_key,
            palette_version=palette_version,
            metadata=normalized_meta,
            output_targets=resolved_targets,
            dedupe_key=dedupe_key,
        )


class ColourManager(ColourInterface):
    def __init__(self, colour_config: dict):
        self.ANSI_FG_COLOUR_SET = {}
        self.ANSI_BG_COLOUR_SET = {}
        # Support both modern 'COLOUR_KEY' format and legacy 'COLOURS' format.
        entries = {}
        if isinstance(colour_config, dict) and colour_config:
            if 'COLOUR_KEY' in colour_config:
                entries = colour_config.get('COLOUR_KEY') or {}
            elif 'COLOURS' in colour_config:
                # Legacy format: { "COLOURS": { key: {"fg": "white", "bg": "black"}, ... } }
                for k, v in colour_config.get('COLOURS', {}).items():
                    if isinstance(v, dict):
                        fg = v.get('fg', '') or ''
                        bg = v.get('bg', '') or ''
                        fg = fg.upper() if isinstance(fg, str) else str(fg).upper()
                        bg = bg.upper() if isinstance(bg, str) else str(bg).upper()
                        if fg and bg:
                            entries[k] = f"{fg}|{bg}"
                        elif fg:
                            entries[k] = fg
                        elif bg:
                            entries[k] = bg
                        else:
                            entries[k] = ''
                    else:
                        entries[k] = str(v).upper()

        # If no entries were provided, attempt to load the package COLOURS.json as a fallback
        if not entries:
            try:
                # tUilKit package layout: tUilKit/utils/output.py -> ../config/COLOURS.json
                pkg_root = Path(__file__).resolve().parents[2]
                colours_path = pkg_root / "config" / "COLOURS.json"
                if colours_path.is_file():
                    with colours_path.open("r", encoding="utf-8") as fh:
                        data = json.load(fh) or {}
                    if isinstance(data, dict) and 'COLOUR_KEY' in data:
                        entries = data.get('COLOUR_KEY') or {}
                    elif isinstance(data, dict) and 'COLOURS' in data:
                        for k, v in data.get('COLOURS', {}).items():
                            if isinstance(v, dict):
                                fg = v.get('fg', '') or ''
                                bg = v.get('bg', '') or ''
                                fg = fg.upper() if isinstance(fg, str) else str(fg).upper()
                                bg = bg.upper() if isinstance(bg, str) else str(bg).upper()
                                if fg and bg:
                                    entries[k] = f"{fg}|{bg}"
                                elif fg:
                                    entries[k] = fg
                                elif bg:
                                    entries[k] = bg
                                else:
                                    entries[k] = ''
                            else:
                                entries[k] = str(v).upper()
            except Exception:
                entries = {}

        for key, value in entries.items():
            if not isinstance(value, str):
                value = str(value)
            if '|' in value:
                fg, bg = value.split('|', 1)
            else:
                fg = value
                # If key is a color name (like "BLUE"), use the color for BG too
                # If key is a config key (like "!info"), default BG to BLACK
                if key.startswith('!') or key in ['ARGS', 'COMMAND', 'CMD', 'TRY', 'TEST', 'PROC', 'DONE', 'PASSED', 'WARN', 'FAIL', 'ERROR', 'OUTPUT', 'INT', 'TEXT', 'FLOAT', 'CALC', 'DATA', 'LIST', 'PATH', 'DRIVE', 'BASEFOLDER', 'MIDFOLDER', 'THISFOLDER', 'FILE', 'DATE', 'TIME', 'LOAD', 'SAVE', 'CREATE', 'DELETE', 'INFO', 'RESET']:
                    bg = 'BLACK'
                else:
                    bg = value  # Use same color for background as foreground
            if fg in RGB:
                self.ANSI_FG_COLOUR_SET[key] = f"\033[38;2;{RGB[fg]}"
            if bg in RGB:
                self.ANSI_BG_COLOUR_SET[key] = f"\033[48;2;{RGB[bg]}"
        # Ensure RESET is always available
        self.ANSI_FG_COLOUR_SET['RESET'] = ANSI_RESET

        # Provide sensible defaults for commonly used colour keys when missing
        default_keys = {
            '!date': 'YELLOW',
            '!time': 'MAGENTA',
            '!proc': 'BLUE',
            '!data': 'CYAN',
            '!path': 'PURPLE',
            '!file': 'GREEN',
            '!info': 'WHITE',
            '!warn': 'YELLOW',
            '!error': 'RED',
            '!done': 'GREEN',
            '!debug': 'MAGENTA',
            '!list': 'CYAN'
        }
        for k, vk in default_keys.items():
            if k not in self.ANSI_FG_COLOUR_SET and vk in RGB:
                self.ANSI_FG_COLOUR_SET[k] = f"\033[38;2;{RGB[vk]}"
            if k not in self.ANSI_BG_COLOUR_SET:
                # default background to BLACK for visibility
                if 'BLACK' in RGB:
                    self.ANSI_BG_COLOUR_SET[k] = f"\033[48;2;{RGB['BLACK']}"

    def get_fg_colour(self, colour_code: str) -> str:
        # Check if it's a config key first (e.g., !info, !proc)
        if colour_code in self.ANSI_FG_COLOUR_SET:
            return self.ANSI_FG_COLOUR_SET[colour_code]
        # Otherwise try to build from RGB dict directly (e.g., RED, BLUE, GREEN)
        elif colour_code in RGB:
            return f"\033[38;2;{RGB[colour_code]}"
        return "\033[38;2;190;190;190m"  # default gray

    def get_bg_colour(self, colour_code: str) -> str:
        # Check if it's a config key first (e.g., !info, !proc)
        if colour_code in self.ANSI_BG_COLOUR_SET:
            return self.ANSI_BG_COLOUR_SET[colour_code]
        # Otherwise try to build from RGB dict directly (e.g., RED, BLUE, GREEN)
        elif colour_code in RGB:
            return f"\033[48;2;{RGB[colour_code]}"
        return "\033[48;2;0;0;0m"  # default black

    def strip_ansi(self, fstring: str) -> str:
        import re
        ansi_escape = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")
        return ansi_escape.sub('', fstring)

    def colour_fstr(self, *args, bg=None, separator=" ") -> str:
        """
        Usage:
            colour_fstr("RED", "Some text", "GREEN", "Other text", bg="YELLOW")
        If bg is provided, applies the background colour to the whole string.
        Now supports per-key background: keys with fg|bg in config set both fg and bg.
        """
        result = ""
        FG_RESET = "\033[38;2;190;190;190m"
        BG_RESET = "\033[49m"
        current_fg = FG_RESET
        current_bg = ""  # Start with no background (not reset code)
        
        for i, arg in enumerate(args):
            if isinstance(arg, list):
                arg = ', '.join(map(str, arg))
            else:
                arg = str(arg)
            # Check if it's a color key from config (e.g., !info, !proc)
            if arg in self.ANSI_FG_COLOUR_SET:
                current_fg = self.ANSI_FG_COLOUR_SET[arg]
                # Check if this color key has a background defined
                if arg in self.ANSI_BG_COLOUR_SET:
                    current_bg = self.ANSI_BG_COLOUR_SET[arg]
            # Check if it's a raw color name (e.g., RED, BLUE, GREEN)
            elif arg in RGB:
                current_fg = self.get_fg_colour(arg)
            elif arg.startswith('BG_'):
                # Set background color and keep it active
                current_bg = self.get_bg_colour(arg[3:])
            else:
                # Apply current colors to text
                result += f"{current_fg}{current_bg}{arg}"
                if i != len(args) - 1:
                    result += separator
        result += FG_RESET + BG_RESET
        return result

    def colour_path(self, path: str) -> str:
        """
        Returns a colour-formatted string for a file path using COLOUR_KEYs:
        DRIVE, BASEFOLDER, MIDFOLDER, THISFOLDER, FILE.
        If only one folder, uses DRIVE and BASEFOLDER.
        If two folders, uses DRIVE, BASEFOLDER, THISFOLDER.
        If more, uses DRIVE, BASEFOLDER, MIDFOLDER(s), THISFOLDER.
        # Exposed for external use in tUilKit: Use when displaying full pathnames with color coding.
        """
        import os
        drive, tail = os.path.splitdrive(path)
        folders, filename = os.path.split(tail)
        folders = folders.strip(os.sep)
        folder_parts = folders.split(os.sep) if folders else []
        n = len(folder_parts)

        parts = []
        if drive:
            parts.append(("DRIVE", drive + os.sep))
        if n == 1 and folder_parts:
            parts.append(("BASEFOLDER", folder_parts[0] + os.sep))
        elif n == 2:
            parts.append(("BASEFOLDER", folder_parts[0] + os.sep))
            parts.append(("THISFOLDER", folder_parts[1] + os.sep))
        elif n > 2:
            parts.append(("BASEFOLDER", folder_parts[0] + os.sep))
            for mid in folder_parts[1:-1]:
                parts.append(("MIDFOLDER", mid + os.sep))
            parts.append(("THISFOLDER", folder_parts[-1] + os.sep))
        if filename:
            parts.append(("FILE", filename))

        colour_args = []
        for key, value in parts:
            colour_args.extend([f"!{key.lower()}", value])
        return self.colour_fstr(*colour_args, separator="")

    def interpret_codes(self, text: str) -> str:
        import re
        def replace_code(match):
            code = match.group(1)
            return self.ANSI_FG_COLOUR_SET.get(code, f"{{{code}}}")  # if not found, leave as {code}
        return re.sub(r'\{(\w+)\}', replace_code, text)


class Logger(LoggerInterface):
    def __init__(self, colour_manager: ColourManager, log_files=None):
        self.Colour_Mgr = colour_manager
        self._log_queue = []
        self.event_history = deque(maxlen=1000)
        self.last_log_entry = None
        self.app_id = os.environ.get("TUILKIT_APP_ID", "tuilkit")
        self.session_id = os.environ.get("TUILKIT_SESSION_ID") or str(uuid.uuid4())
        self.correlation_id = os.environ.get("TUILKIT_CORRELATION_ID") or self.session_id
        self.source_layer = "tuilkit"
        self.dual_logging = bool(os.environ.get("TUILKIT_DUAL_LOGGING", "1") == "1")
        if config_loader is not None:
            self.LOG_KEYS = config_loader.global_config.get("LOG_CATEGORIES", {
                "default": ["MASTER", "SESSION"],
                "error": ["ERROR", "SESSION", "MASTER"],
                "fs": ["MASTER", "SESSION", "FS"],
                "init": ["INIT", "SESSION", "MASTER"]
            })
        else:
            self.LOG_KEYS = {
                "default": ["MASTER", "SESSION"],
                "error": ["ERROR", "SESSION", "MASTER"],
                "fs": ["MASTER", "SESSION", "FS"],
                "init": ["INIT", "SESSION", "MASTER"]
            }
        self.test_mode = bool(os.environ.get("TUILKIT_TEST_MODE", "0") == "1")
        if self.test_mode:
            tests_options = config_loader.global_config.get("TESTS_OPTIONS", {}) if config_loader is not None else {}
            test_logs_folder = tests_options.get("TEST_LOGS_FOLDER", ".testlogs/tUilKit/")
            self.log_files = {}
            for key in LOG_FILES:
                log_name = os.path.basename(LOG_FILES[key])
                self.log_files[key] = os.path.join(test_logs_folder, log_name)
        else:
            self.log_files = log_files or copy.deepcopy(LOG_FILES)
        # Clean the session log on initialization to ensure it only contains the current execution
        self._clean_session_log()

    @staticmethod
    def normalize_metadata(metadata=None, **overrides):
        return LogEntry.normalize_metadata(metadata, **overrides)

    def create_log_entry(self, message: Any, *, category: str = "default", severity: Optional[str] = None,
                         verbosity: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None,
                         app_id: Optional[str] = None, component: str = "logger", module: str = "",
                         session_id: Optional[str] = None, correlation_id: Optional[str] = None,
                         source_layer: str = "tuilkit", target: str = "terminal", file_path: str = "",
                         output_targets: Optional[Iterable[str]] = None, palette_key: str = "",
                         palette_version: str = "unknown", parent_event_id: str = "") -> LogEntry:
        resolved_meta = self.normalize_metadata(metadata)
        resolved_meta.setdefault("app_id", app_id or self.app_id)
        resolved_meta.setdefault("session_id", session_id or self.session_id)
        resolved_meta.setdefault("correlation_id", correlation_id or self.correlation_id)
        resolved_meta.setdefault("source_layer", source_layer or self.source_layer)
        return LogEntry.from_message(
            message,
            category=category,
            severity=severity,
            verbosity=verbosity,
            app_id=resolved_meta.get("app_id"),
            component=component,
            module=module,
            session_id=resolved_meta.get("session_id"),
            correlation_id=resolved_meta.get("correlation_id"),
            source_layer=resolved_meta.get("source_layer"),
            target=target,
            file_path=file_path,
            output_targets=output_targets,
            metadata=resolved_meta,
            palette_key=palette_key,
            palette_version=palette_version,
            parent_event_id=parent_event_id,
        )

    def _clean_session_log(self):
        """
        Clears the session log file to ensure it only contains logs from the current execution.
        """
        session_log = self.log_files.get("SESSION")
        if session_log:
            try:
                # Ensure the log directory exists
                log_dir = os.path.dirname(session_log)
                if not os.path.exists(log_dir):
                    os.makedirs(log_dir)
                # Clear the session log file
                with open(session_log, 'w', encoding='utf-8') as log:
                    log.write("")  # Clear the file
            except Exception as e:
                # If we can't clear the session log, log to terminal only (avoid recursion)
                print(f"Warning: Could not clear session log {session_log}: {e}")

    def _get_log_files(self, category):
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

    @staticmethod
    def split_time_string(time_string: str) -> tuple[str, str]:
        parts = time_string.strip().split()
        if len(parts) >= 2:
            return parts[0], parts[1]
        elif len(parts) == 1:
            return parts[0], ""
        else:
            return "", ""

    def log_message(self, message: str, log_files = None, end: str = "\n", log_to: str = "both", time_stamp: bool = True, dual_log: 'bool | None' = None, entry: Optional[LogEntry] = None):
        """
        log_files: list of str or str or None
        log_to: "both", "file", "term", "queue"
        time_stamp: if True, prepend date and time to the message
        """
        if isinstance(log_files, str):
            log_files = [log_files]
        elif log_files is None:
            log_files = []

        if entry is not None:
            self.last_log_entry = entry
            self.event_history.append(entry)
            if not entry.output_targets and log_files:
                entry.output_targets = list(log_files)
            if entry.file_path == "" and log_files:
                entry.file_path = log_files[0]

        if time_stamp:
            date, time = self.split_time_string(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            # Apply colored timestamp with proper reset before message
            timestamp_str = self.Colour_Mgr.colour_fstr("!date", date, "!time", time)
            message = f"{timestamp_str} {message}"

        # Dual logging: if SESSION log, also log to tUilKit central if not already
        effective_log_files = list(log_files)
        if (dual_log if dual_log is not None else self.dual_logging):
            session_log = self.log_files.get("SESSION")
            if session_log and session_log not in effective_log_files:
                effective_log_files.append(session_log)
            if TUILKIT_SESSION_LOG and TUILKIT_SESSION_LOG not in effective_log_files:
                effective_log_files.append(TUILKIT_SESSION_LOG)

        if log_to in ("file", "both") and effective_log_files:
            for log_file in effective_log_files:
                log_dir = os.path.dirname(log_file)
                if not os.path.exists(log_dir):
                    # Queue the message if the log folder doesn't exist
                    self._log_queue.append((message, log_file, end))
                    if log_to == "file":
                        continue
                else:
                    self.flush_log_queue(log_file)
                    if not os.path.exists(log_file):
                        self._log_queue.append((f"Log file created: {log_file}", log_file, "\n"))
                    with open(log_file, 'a', encoding='utf-8') as log:
                        log.write(self.Colour_Mgr.strip_ansi(message) + end)

        if log_to in ("term", "both"):
            print(message, end=end)

        if log_to == "queue" and effective_log_files:
            for log_file in effective_log_files:
                self._log_queue.append((message, log_file, end))

    def flush_log_queue(self, log_file: str):
        log_dir = os.path.dirname(log_file)
        if os.path.exists(log_dir):
            with open(log_file, 'a', encoding='utf-8') as log:
                for msg, lf, end in self._log_queue:
                    if lf == log_file:
                        log.write(self.Colour_Mgr.strip_ansi(msg) + end)
            # Remove flushed messages
            self._log_queue = [item for item in self._log_queue if item[1] != log_file]

    def colour_log(self, *args, category="default", spacer=0, log_files=None, end="\n", log_to="both", time_stamp=True, metadata=None, severity=None, verbosity=None):
        # Exposed for external use in tUilKit: Use to replace print(f"") with colored, timestamped logging.
        category_files = self._get_log_files(category)
        if log_files is None:
            effective_log_files = category_files
        else:
            if isinstance(log_files, str):
                log_files = [log_files]
            effective_log_files = list(set(category_files + log_files))

        rendered_message = " ".join(str(arg) for arg in args)
        entry = self.create_log_entry(
            rendered_message,
            category=category,
            severity=severity,
            verbosity=verbosity,
            metadata=metadata,
            source_layer=self.source_layer,
            target=log_to,
            file_path=effective_log_files[0] if effective_log_files else "",
            output_targets=effective_log_files,
            component="logger",
            module="output.colour_log",
        )
        if time_stamp:
            date, time = self.split_time_string(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            prefix = ("!date", date, "!time", time)
        else:
            prefix = ()
        if spacer > 0:
            coloured_message = self.Colour_Mgr.colour_fstr(*prefix, f"{' ' * spacer}", *args)
        else:
            coloured_message = self.Colour_Mgr.colour_fstr(*prefix, *args)
        entry.rendered_text = coloured_message
        entry.message = rendered_message
        entry.raw_message = rendered_message
        # Pass time_stamp=False so log_message does not add its own (uncoloured) timestamp
        self.log_message(coloured_message, log_files=effective_log_files, end=end, log_to=log_to, time_stamp=False, entry=entry)

    def colour_log_text(self, message: str, log_files=None, log_to="both", time_stamp=True):
        if time_stamp:
            date, time = self.split_time_string(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            prefix = f"{date} {time} "
        else:
            prefix = ""
        coloured_message = prefix + self.Colour_Mgr.interpret_codes(message)
        self.log_message(coloured_message, log_files=log_files, log_to=log_to, time_stamp=False)

    def log_exception(self, description: str, exception: Exception, category="error", log_files=None, log_to: str = "both", metadata=None) -> None:
        # Exposed for external use in tUilKit: Use for logging exceptions with colored formatting.
        category_files = self._get_log_files(category)
        if log_files is None:
            effective_log_files = category_files
        else:
            if isinstance(log_files, str):
                log_files = [log_files]
            effective_log_files = list(set(category_files + log_files))
        self.colour_log("", log_files=effective_log_files, time_stamp=False, log_to=log_to, metadata=metadata)
        self.colour_log("", log_files=effective_log_files, time_stamp=False, log_to=log_to, metadata=metadata)
        self.colour_log("!error", "UNEXPECTED ERROR:", "!info", description, "!error", str(exception), log_files=effective_log_files, log_to=log_to, severity="ERROR", metadata=metadata)

    def log_done(self, log_files = None, end: str = "\n", log_to: str = "both", time_stamp=True):
        self.colour_log("!done", "Done!", category="default", log_files=log_files, end=end, log_to=log_to, time_stamp=time_stamp)

    # Compatibility wrappers for conventional logger API
    def info(self, message: str, *args, **kwargs):
        try:
            msg = message % args if args else str(message)
        except Exception:
            msg = str(message)
        self.colour_log("!info", msg, category="default", log_files=kwargs.get("log_files"), log_to=kwargs.get("log_to", "both"))

    def error(self, message: str, *args, **kwargs):
        try:
            msg = message % args if args else str(message)
        except Exception:
            msg = str(message)
        self.colour_log("!error", msg, category="error", log_files=kwargs.get("log_files"), log_to=kwargs.get("log_to", "both"))

    def warning(self, message: str, *args, **kwargs):
        try:
            msg = message % args if args else str(message)
        except Exception:
            msg = str(message)
        self.colour_log("!warn", msg, category="default", log_files=kwargs.get("log_files"), log_to=kwargs.get("log_to", "both"))

    def debug(self, message: str, *args, **kwargs):
        try:
            msg = message % args if args else str(message)
        except Exception:
            msg = str(message)
        self.colour_log("!debug", msg, category="default", log_files=kwargs.get("log_files"), log_to=kwargs.get("log_to", "both"))

    def exception(self, message: str, *args, exc: Exception = None, **kwargs):
        """Log an exception; if exc provided, include exception details using `log_exception`."""
        try:
            msg = message % args if args else str(message)
        except Exception:
            msg = str(message)
        if exc is not None:
            self.log_exception(msg, exc, category=kwargs.get("category", "error"), log_files=kwargs.get("log_files"), log_to=kwargs.get("log_to", "both"))
        else:
            # Fallback to error-style logging
            self.colour_log("!error", msg, category=kwargs.get("category", "error"), log_files=kwargs.get("log_files"), log_to=kwargs.get("log_to", "both"))

    def log_column_list(self, df, filename, log_files=None, log_to: str = "both"):
        self.colour_log(
            "!path", os.path.dirname(filename), "/",
            "!file", os.path.basename(filename),
            ": ",
            "!info", "Columns:",
            "!output", df.columns.tolist(),
            category="default",
            log_files=log_files,
            log_to=log_to)

    def _apply_gradient(self, text: str, fg_gradient=None, bg_gradient=None, rainbow=False) -> list:
        """
        Helper to build colour_fstr args for character-by-character gradient.
        Returns list of args ready for colour_fstr.
        """
        if rainbow:
            rainbow_colours = [
                'RED', 'CRIMSON', 'ORANGE', 'CORAL', 'GOLD',
                'YELLOW', 'CHARTREUSE', 'GREEN', 'CYAN',
                'BLUE', 'INDIGO', 'VIOLET', 'MAGENTA'
            ]
            fg_gradient = rainbow_colours + rainbow_colours[::-1][1:-1]
        
        args = []
        if fg_gradient or bg_gradient:
            text_len = len(text)
            for i, char in enumerate(text):
                if fg_gradient:
                    color_idx = int((i / text_len) * len(fg_gradient)) if text_len > 1 else 0
                    args.append(fg_gradient[min(color_idx, len(fg_gradient) - 1)])
                if bg_gradient:
                    bg_idx = int((i / text_len) * len(bg_gradient)) if text_len > 1 else 0
                    args.append(f"BG_{bg_gradient[min(bg_idx, len(bg_gradient) - 1)]}")
                args.append(char)
        else:
            args.append(text)
        return args

    def print_rainbow_row(self, pattern="X-O-", spacer=0, log_files=None, end="\n", log_to="both"):
        bright_colours = [
            'RED', 'CRIMSON', 'ORANGE', 'CORAL', 'GOLD',
            'YELLOW', 'CHARTREUSE', 'GREEN', 'CYAN',
            'BLUE', 'INDIGO', 'VIOLET', 'MAGENTA'
        ]
        self.log_message(f"{' ' * spacer}", log_files=log_files, end="", log_to=log_to, time_stamp=False)
        rainbow_colours = bright_colours + bright_colours[::-1][1:-1]
        for colour in rainbow_colours:
            self.log_message(self.Colour_Mgr.colour_fstr(colour, pattern), log_files=log_files, end="", log_to=log_to, time_stamp=False)
        self.log_message(self.Colour_Mgr.colour_fstr("RED", f"{pattern}"[0]), log_files=log_files, end=end, log_to=log_to, time_stamp=False)

    def print_top_border(self, pattern, length, index=0, log_files=None, border_colour='!proc', border_fg_gradient=None, border_bg_gradient=None, border_rainbow=False, log_to: str = "both"):
        """
        Print top border with optional gradient or rainbow coloring.
        
        Args:
            border_colour: Single colour key for border (default, used if no gradient/rainbow)
            border_fg_gradient: List of colour keys for border foreground gradient
            border_bg_gradient: List of colour keys for border background gradient
            border_rainbow: If True, apply rainbow gradient to border (overrides border_fg_gradient)
        """
        top_pattern = pattern['TOP'][index] if isinstance(pattern['TOP'], list) else pattern['TOP']
        top = top_pattern * (length // len(top_pattern))
        
        if border_rainbow or border_fg_gradient or border_bg_gradient:
            gradient_args = self._apply_gradient(top, fg_gradient=border_fg_gradient, bg_gradient=border_bg_gradient, rainbow=border_rainbow)
            coloured_message = self.Colour_Mgr.colour_fstr(*gradient_args, separator="")
            self.log_message(" " + coloured_message, log_files=log_files, log_to=log_to, time_stamp=True)
        else:
            self.colour_log(border_colour, f" {top}", category="default", log_files=log_files, log_to=log_to)

    def print_text_line(self, text, pattern, length, index=0, log_files=None, border_colour='!proc', text_colour='!proc', border_fg_gradient=None, border_bg_gradient=None, border_rainbow=False, text_fg_gradient=None, text_bg_gradient=None, text_rainbow=False, justify='left', log_to: str = "both"):
        """
        Print text line with optional gradient or rainbow coloring on borders and text.
        
        Args:
            border_colour: Single colour key for borders (default, used if no gradient/rainbow)
            text_colour: Single colour key for text (default, used if no gradient/rainbow)
            border_fg_gradient: List of colour keys for border foreground gradient
            border_bg_gradient: List of colour keys for border background gradient
            border_rainbow: If True, apply rainbow gradient to borders
            text_fg_gradient: List of colour keys for text foreground gradient
            text_bg_gradient: List of colour keys for text background gradient
            text_rainbow: If True, apply rainbow gradient to text
            justify: Text alignment - 'left', 'center', or 'right' (default: 'left')
        """
        left = pattern['LEFT'][index] if isinstance(pattern['LEFT'], list) else pattern['LEFT']
        right = pattern['RIGHT'][index] if isinstance(pattern['RIGHT'], list) else pattern['RIGHT']
        inner_text_length = len(left) + len(text) + len(right)
        total_space = length - inner_text_length
        
        # Calculate spacing based on justification
        if justify == 'center':
            leading_space = total_space // 2
            trailing_space = total_space - leading_space
        elif justify == 'right':
            leading_space = total_space
            trailing_space = 0
        else:  # 'left' or default
            leading_space = 0
            trailing_space = total_space
        
        # Check if we need gradients for border or text
        border_has_gradient = border_rainbow or border_fg_gradient or border_bg_gradient
        text_has_gradient = text_rainbow or text_fg_gradient or text_bg_gradient
        
        if border_has_gradient or text_has_gradient:
            # Build gradient components
            if border_has_gradient:
                left_args = self._apply_gradient(left, fg_gradient=border_fg_gradient, bg_gradient=border_bg_gradient, rainbow=border_rainbow)
                right_args = self._apply_gradient(right, fg_gradient=border_fg_gradient, bg_gradient=border_bg_gradient, rainbow=border_rainbow)
            else:
                left_args = [border_colour, left]
                right_args = [border_colour, right]
            
            if text_has_gradient:
                text_args = self._apply_gradient(text, fg_gradient=text_fg_gradient, bg_gradient=text_bg_gradient, rainbow=text_rainbow)
            else:
                text_args = [text_colour, text]
            
            # Build complete message
            complete_args = [*left_args, f"{' ' * leading_space}", *text_args, f"{' ' * trailing_space}", *right_args]
            coloured_message = self.Colour_Mgr.colour_fstr(*complete_args, separator="")
            self.log_message(" " + coloured_message, log_files=log_files, log_to=log_to, time_stamp=True)
        else:
            # Simple color version
            text_with_spaces = f"{' ' * leading_space}{text}{' ' * trailing_space}"
            text_line_args = [border_colour, left, text_colour, text_with_spaces, border_colour, right]
            self.colour_log(*text_line_args, category="default", log_files=log_files, log_to=log_to)

    def print_bottom_border(self, pattern, length, index=0, log_files=None, border_colour='!proc', border_fg_gradient=None, border_bg_gradient=None, border_rainbow=False, log_to: str = "both"):
        """
        Print bottom border with optional gradient or rainbow coloring.
        
        Args:
            border_colour: Single colour key for border (default, used if no gradient/rainbow)
            border_fg_gradient: List of colour keys for border foreground gradient
            border_bg_gradient: List of colour keys for border background gradient
            border_rainbow: If True, apply rainbow gradient to border
        """
        bottom_pattern = pattern['BOTTOM'][index] if isinstance(pattern['BOTTOM'], list) else pattern['BOTTOM']
        bottom = bottom_pattern * (length // len(bottom_pattern))
        
        if border_rainbow or border_fg_gradient or border_bg_gradient:
            gradient_args = self._apply_gradient(bottom, fg_gradient=border_fg_gradient, bg_gradient=border_bg_gradient, rainbow=border_rainbow)
            coloured_message = self.Colour_Mgr.colour_fstr(*gradient_args, separator="")
            self.log_message(" " + coloured_message, log_files=log_files, log_to=log_to, time_stamp=True)
        else:
            self.colour_log(border_colour, f" {bottom}", category="default", log_files=log_files, log_to=log_to)

    def apply_border(self, text, pattern, total_length=None, index=0, log_files=None, border_colour='!proc', text_colour='!proc', border_fg_gradient=None, border_bg_gradient=None, border_rainbow=False, text_fg_gradient=None, text_bg_gradient=None, text_rainbow=False, justify='left', log_to: str = "both"):
        """
        Apply border with optional gradient or rainbow coloring on borders and text.
        
        Args:
            border_colour: Single colour key for borders (default)
            text_colour: Single colour key for text (default)
            border_fg_gradient: List of colour keys for border foreground gradient (e.g., ['RED', 'YELLOW', 'GREEN'])
            border_bg_gradient: List of colour keys for border background gradient
            border_rainbow: If True, apply rainbow gradient to borders
            text_fg_gradient: List of colour keys for text foreground gradient
            text_bg_gradient: List of colour keys for text background gradient
            text_rainbow: If True, apply rainbow gradient to text
            justify: Text alignment - 'left', 'center', or 'right' (default: 'left')
        """
        # Exposed for external use in tUilKit: Use for highlighting header text in the terminal with borders.
        left = pattern['LEFT'][index] if isinstance(pattern['LEFT'], list) else pattern['LEFT']
        right = pattern['RIGHT'][index] if isinstance(pattern['RIGHT'], list) else pattern['RIGHT']
        inner_text_length = len(left) + len(text) + len(right)
        if total_length and total_length > inner_text_length:
            length = total_length
        else:
            length = inner_text_length
        self.print_top_border(pattern, length, index, log_files=log_files, border_colour=border_colour, border_fg_gradient=border_fg_gradient, border_bg_gradient=border_bg_gradient, border_rainbow=border_rainbow, log_to=log_to)
        self.print_text_line(text, pattern, length, index, log_files=log_files, border_colour=border_colour, text_colour=text_colour, border_fg_gradient=border_fg_gradient, border_bg_gradient=border_bg_gradient, border_rainbow=border_rainbow, text_fg_gradient=text_fg_gradient, text_bg_gradient=text_bg_gradient, text_rainbow=text_rainbow, justify=justify, log_to=log_to)
        self.print_bottom_border(pattern, length, index, log_files=log_files, border_colour=border_colour, border_fg_gradient=border_fg_gradient, border_bg_gradient=border_bg_gradient, border_rainbow=border_rainbow, log_to=log_to)

    def apply_border_multiline(self, text_lines, pattern, total_length=None, index=0, log_files=None, border_colour='!proc', text_colour='!proc', border_fg_gradient=None, border_bg_gradient=None, border_rainbow=False, text_fg_gradient=None, text_bg_gradient=None, text_rainbow=False, justify='left', log_to: str = "both"):
        """
        Apply border around multiple lines of text with optional gradient or rainbow coloring.
        
        Args:
            text_lines: List of text strings, one per line
            border_colour: Single colour key for borders (default)
            text_colour: Single colour key for text (default)
            border_fg_gradient: List of colour keys for border foreground gradient
            border_bg_gradient: List of colour keys for border background gradient
            border_rainbow: If True, apply rainbow gradient to borders
            text_fg_gradient: List of colour keys for text foreground gradient
            text_bg_gradient: List of colour keys for text background gradient
            text_rainbow: If True, apply rainbow gradient to text
            justify: Text alignment - 'left', 'center', or 'right' (default: 'left')
        """
        if not text_lines:
            return
        
        # Calculate length based on longest line
        left = pattern['LEFT'][index] if isinstance(pattern['LEFT'], list) else pattern['LEFT']
        right = pattern['RIGHT'][index] if isinstance(pattern['RIGHT'], list) else pattern['RIGHT']
        
        if total_length:
            length = total_length
        else:
            max_text_len = max(len(line) for line in text_lines)
            length = len(left) + max_text_len + len(right)
        
        # Print top border
        self.print_top_border(pattern, length, index, log_files=log_files, border_colour=border_colour, border_fg_gradient=border_fg_gradient, border_bg_gradient=border_bg_gradient, border_rainbow=border_rainbow, log_to=log_to)
        
        # Print each text line
        for line in text_lines:
            self.print_text_line(line, pattern, length, index, log_files=log_files, border_colour=border_colour, text_colour=text_colour, border_fg_gradient=border_fg_gradient, border_bg_gradient=border_bg_gradient, border_rainbow=border_rainbow, text_fg_gradient=text_fg_gradient, text_bg_gradient=text_bg_gradient, text_rainbow=text_rainbow, justify=justify, log_to=log_to)
        
        # Print bottom border
        self.print_bottom_border(pattern, length, index, log_files=log_files, border_colour=border_colour, border_fg_gradient=border_fg_gradient, border_bg_gradient=border_bg_gradient, border_rainbow=border_rainbow, log_to=log_to)
