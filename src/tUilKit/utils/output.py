"""
Contains functions for log files and displaying text output in the terminal using ANSI sequences to colour code output.
"""

import os
from datetime import datetime
from tUilKit.dict.DICT_COLOURS import RGB
from tUilKit.dict.DICT_CODES import ESCAPES, COMMANDS
from tUilKit.interfaces.logger_interface import LoggerInterface
from tUilKit.interfaces.colour_interface import ColourInterface
from tUilKit.utils.config import ConfigLoader
import copy

# ANSI ESCAPE CODE PREFIXES for colour coding f-strings
SET_FG_COLOUR = ESCAPES['OCTAL'] + COMMANDS['FGC']
SET_BG_COLOUR = ESCAPES['OCTAL'] + COMMANDS['BGC']
ANSI_RESET = ESCAPES['OCTAL'] + COMMANDS['RESET']
try:
    config_loader = ConfigLoader()
    LOG_FILES = copy.deepcopy(config_loader.global_config.get("LOG_FILES", {}))
    root_modes = config_loader.global_config.get("ROOT_MODES", {})
    log_root_mode = root_modes.get("LOGS", "project")
    if log_root_mode == "workspace":
        workspace_root = os.path.abspath(os.path.join(os.getcwd(), "../../"))
        for key in LOG_FILES:
            if not os.path.isabs(LOG_FILES[key]):
                app_name = LOG_FILES[key].split("/")[1] if "/" in LOG_FILES[key] else "tUilKit"
                log_name = os.path.basename(LOG_FILES[key])
                LOG_FILES[key] = os.path.join(workspace_root, LOG_FILES[key])
    elif log_root_mode == "auto":
        pass
except Exception:
    config_loader = None
    LOG_FILES = {}
    # For 'auto', default to workspace root
    workspace_root = os.path.abspath(os.path.join(os.getcwd(), "../../"))
    for key in LOG_FILES:
        if not os.path.isabs(LOG_FILES[key]):
            LOG_FILES[key] = os.path.join(workspace_root, LOG_FILES[key])

class ColourManager(ColourInterface):
    def __init__(self, colour_config: dict):
        self.ANSI_FG_COLOUR_SET = {}
        self.ANSI_BG_COLOUR_SET = {}
        for key, value in colour_config['COLOUR_KEY'].items():
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
        self.ANSI_FG_COLOUR_SET['RESET'] = ANSI_RESET

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

    def log_message(self, message: str, log_files = None, end: str = "\n", log_to: str = "both", time_stamp: bool = True, dual_log: 'bool | None' = None):
        """
        log_files: list of str or str or None
        log_to: "both", "file", "term", "queue"
        time_stamp: if True, prepend date and time to the message
        """
        if isinstance(log_files, str):
            log_files = [log_files]
        elif log_files is None:
            log_files = []

        if time_stamp:
            date, time = self.split_time_string(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            # Apply colored timestamp with proper reset before message
            timestamp_str = self.Colour_Mgr.colour_fstr("!date", date, "!time", time)
            message = f"{timestamp_str} {message}"

        # Dual logging: if SESSION log, also log to tUilKit central if not already
        effective_log_files = list(log_files)
        if (dual_log if dual_log is not None else self.dual_logging):
            session_log = self.log_files.get("SESSION")
            tuilkit_session = os.path.join(".logs", "tUilKit", "SESSION.log")
            if session_log and session_log not in effective_log_files:
                effective_log_files.append(session_log)
            if tuilkit_session not in effective_log_files:
                effective_log_files.append(tuilkit_session)

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

    def colour_log(self, *args, category="default", spacer=0, log_files=None, end="\n", log_to="both", time_stamp=True):
        # Exposed for external use in tUilKit: Use to replace print(f"") with colored, timestamped logging.
        category_files = self._get_log_files(category)
        if log_files is None:
            effective_log_files = category_files
        else:
            if isinstance(log_files, str):
                log_files = [log_files]
            effective_log_files = list(set(category_files + log_files))
        if time_stamp:
            date, time = self.split_time_string(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            prefix = ("!date", date, "!time", time)
        else:
            prefix = ()
        if spacer > 0:
            coloured_message = self.Colour_Mgr.colour_fstr(*prefix, f"{' ' * spacer}", *args)
        else:
            coloured_message = self.Colour_Mgr.colour_fstr(*prefix, *args)
        # Pass time_stamp=False so log_message does not add its own (uncoloured) timestamp
        self.log_message(coloured_message, log_files=effective_log_files, end=end, log_to=log_to, time_stamp=False)

    def colour_log_text(self, message: str, log_files=None, log_to="both", time_stamp=True):
        if time_stamp:
            date, time = self.split_time_string(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            prefix = f"{date} {time} "
        else:
            prefix = ""
        coloured_message = prefix + self.Colour_Mgr.interpret_codes(message)
        self.log_message(coloured_message, log_files=log_files, log_to=log_to, time_stamp=False)

    def log_exception(self, description: str, exception: Exception, category="error", log_files=None, log_to: str = "both") -> None:
        # Exposed for external use in tUilKit: Use for logging exceptions with colored formatting.
        category_files = self._get_log_files(category)
        if log_files is None:
            effective_log_files = category_files
        else:
            if isinstance(log_files, str):
                log_files = [log_files]
            effective_log_files = list(set(category_files + log_files))
        self.colour_log("", log_files=effective_log_files, time_stamp=False, log_to=log_to)
        self.colour_log("", log_files=effective_log_files, time_stamp=False, log_to=log_to)
        self.colour_log("!error", "UNEXPECTED ERROR:", "!info", description, "!error", str(exception), log_files=effective_log_files, log_to=log_to)

    def log_done(self, log_files = None, end: str = "\n", log_to: str = "both", time_stamp=True):
        self.colour_log("!done", "Done!", category="default", log_files=log_files, end=end, log_to=log_to, time_stamp=time_stamp)

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
