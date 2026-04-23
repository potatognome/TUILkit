#!/usr/bin/env python3
"""
Examples: cli_menus.py — CLIMenuHandler
Tests all public functions of CLIMenuHandler with normal, edge-case, and break inputs.
Uses unittest.mock.patch to inject controlled input without requiring user interaction.
"""
import os
import sys
import time
import json
import argparse
from pathlib import Path
from datetime import datetime
from unittest.mock import patch

# ---------------------------------------------------------------------------
# Bootstrap from test_paths.json
# ---------------------------------------------------------------------------
HERE = Path(__file__).resolve()
_paths_file = HERE.parent / "test_paths.json"
if not _paths_file.exists():
    raise FileNotFoundError(
        "test_paths.json not found. Run 'python examples/test_config.py' first."
    )
with open(_paths_file) as f:
    _p = json.load(f)

PROJECT_ROOT     = Path(_p["project_root"])
WORKSPACE_ROOT   = Path(_p["workspace_root"])
TEST_LOGS_FOLDER = Path(_p["test_logs_folder"])
sys.path.insert(0, str(PROJECT_ROOT / "src"))
TEST_LOGS_FOLDER.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Args
# ---------------------------------------------------------------------------
parser = argparse.ArgumentParser(description="tUilKit cli_menus.py examples")
parser.add_argument(
    "--clean",
    choices=["local", "all", "master", "tests"],
    default="local",
    help="Log cleanup scope on start"
)
args, _ = parser.parse_known_args()

# ---------------------------------------------------------------------------
# Factories
# ---------------------------------------------------------------------------
from tUilKit.factories import get_logger, get_cli_menu_handler

logger = get_logger()
menus  = get_cli_menu_handler()

TEST_LOG_FILE  = str(TEST_LOGS_FOLDER / "SESSION.log")
SCRIPT_LOG     = str(TEST_LOGS_FOLDER / f"{HERE.stem}.log")
BORDER_PATTERN = {"TOP": "=", "BOTTOM": "=", "LEFT": "| ", "RIGHT": " |"}

# ---------------------------------------------------------------------------
# Session start
# ---------------------------------------------------------------------------
os.system("cls" if os.name == "nt" else "clear")
now = datetime.now()
logger.print_rainbow_row(log_files=[TEST_LOG_FILE])
logger.colour_log(
    "!date", now.strftime("%Y-%m-%d %H:%M:%S"),
    "!proc", "Starting examples:", "!text", HERE.stem,
    log_files=[TEST_LOG_FILE]
)

# ---------------------------------------------------------------------------
# Shared test fixtures
# ---------------------------------------------------------------------------
SAMPLE_OPTIONS = [
    {"key": "opt_a", "label": "Option A", "icon": "🅰"},
    {"key": "opt_b", "label": "Option B", "icon": "🅱"},
    {"key": "opt_c", "label": "Option C", "icon": "©️"},
]

BREAK_INPUTS = [
    ("empty string",        ""),
    ("out-of-range number", "99"),
    ("non-numeric text",    "abc"),
    ("very long string",    "A" * 1000),
    ("null byte",           "\x00"),
    ("tab/newline",         "\t\n"),
    ("negative number",     "-1"),
    ("float",               "1.5"),
    ("special chars",       "!@#$%^&*()"),
]


# ===========================================================================
# Test functions
# ===========================================================================

def test_show_numbered_menu(function_log=None):
    """Tests CLIMenuHandler.show_numbered_menu — all inputs including break inputs."""
    log_targets = [TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE]

    # --- call header ---
    logger.colour_log(
        "!output", "result =", "!proc", "CLIMenuHandler.", "!text", "show_numbered_menu",
        "!args",   "with arguments:",
        "!data",   "title='Test Menu'",
        "!data",   "options=[opt_a, opt_b, opt_c]",
        "!data",   "allow_back=True",
        "!data",   "allow_quit=True",
        log_files=log_targets
    )

    # Happy path: valid choice
    with patch("builtins.input", return_value="1"):
        result = menus.show_numbered_menu("Test Menu", SAMPLE_OPTIONS)
    logger.colour_log("!done", "ran successfully.", "!output", "Producing output:",
                      "!data", repr(result), "!info", "→ assigned to result",
                      log_files=log_targets)
    logger.colour_log("!test", "Assert: valid choice returns correct key", log_files=log_targets)
    assert result == "opt_a", f"Expected 'opt_a', got {result!r}"
    logger.colour_log("!pass", "PASSED", log_files=log_targets)

    # Happy path: last option
    with patch("builtins.input", return_value="3"):
        result = menus.show_numbered_menu("Test Menu", SAMPLE_OPTIONS)
    assert result == "opt_c"
    logger.colour_log("!pass", "Last option PASSED", log_files=log_targets)

    # Quit
    with patch("builtins.input", return_value="quit"):
        result = menus.show_numbered_menu("Test Menu", SAMPLE_OPTIONS)
    logger.colour_log("!info", "quit →", "!data", repr(result), log_files=log_targets)
    assert result == "quit"
    logger.colour_log("!pass", "quit PASSED", log_files=log_targets)

    # Back
    with patch("builtins.input", return_value="back"):
        result = menus.show_numbered_menu("Test Menu", SAMPLE_OPTIONS)
    logger.colour_log("!info", "back →", "!data", repr(result), log_files=log_targets)
    assert result == "back"
    logger.colour_log("!pass", "back PASSED", log_files=log_targets)

    # q shortcut
    with patch("builtins.input", return_value="q"):
        result = menus.show_numbered_menu("Test Menu", SAMPLE_OPTIONS)
    assert result == "quit"
    logger.colour_log("!pass", "q shortcut PASSED", log_files=log_targets)

    # Break inputs — document behaviour, no assertion required
    for label, val in BREAK_INPUTS:
        with patch("builtins.input", return_value=val):
            try:
                result = menus.show_numbered_menu("Test Menu", SAMPLE_OPTIONS)
                logger.colour_log("!warn", f"Break ({label}) →", "!data", repr(result),
                                  log_files=log_targets)
            except Exception as e:
                logger.colour_log("!error", f"Break ({label}) raised:", "!data", str(e),
                                  log_files=log_targets)

    # Edge: empty options list
    with patch("builtins.input", return_value="1"):
        try:
            result = menus.show_numbered_menu("Empty Menu", [])
            logger.colour_log("!warn", "Empty options →", "!data", repr(result), log_files=log_targets)
        except Exception as e:
            logger.colour_log("!warn", "Empty options raised:", "!data", str(e), log_files=log_targets)


def test_confirm(function_log=None):
    """Tests CLIMenuHandler.confirm — y/n prompt with defaults and break inputs."""
    log_targets = [TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE]

    logger.colour_log(
        "!output", "result =", "!proc", "CLIMenuHandler.", "!text", "confirm",
        "!args",   "with arguments:",
        "!data",   "message='Proceed with operation?'",
        "!data",   "default=False",
        log_files=log_targets
    )

    # Happy path: yes
    with patch("builtins.input", return_value="y"):
        result = menus.confirm("Proceed with operation?")
    logger.colour_log("!done", "ran successfully.", "!output", "Producing output:",
                      "!data", repr(result), log_files=log_targets)
    logger.colour_log("!test", "Assert: 'y' returns True", log_files=log_targets)
    assert result is True
    logger.colour_log("!pass", "PASSED", log_files=log_targets)

    # Happy path: no
    with patch("builtins.input", return_value="n"):
        result = menus.confirm("Proceed?")
    assert result is False
    logger.colour_log("!pass", "'n' → False PASSED", log_files=log_targets)

    # Default=False, empty input
    with patch("builtins.input", return_value=""):
        result = menus.confirm("Proceed?", default=False)
    assert result is False
    logger.colour_log("!pass", "Empty → default False PASSED", log_files=log_targets)

    # Default=True, empty input
    with patch("builtins.input", return_value=""):
        result = menus.confirm("Proceed?", default=True)
    assert result is True
    logger.colour_log("!pass", "Empty → default True PASSED", log_files=log_targets)

    # "yes" / "no" full words
    for val, expected in [("yes", True), ("no", False), ("YES", False)]:
        with patch("builtins.input", return_value=val):
            result = menus.confirm("Proceed?")
        logger.colour_log("!info", f"'{val}' →", "!data", repr(result), log_files=log_targets)

    # Break inputs
    for label, val in BREAK_INPUTS[:6]:
        with patch("builtins.input", return_value=val):
            try:
                result = menus.confirm("Proceed?")
                logger.colour_log("!warn", f"Break ({label}) →", "!data", repr(result),
                                  log_files=log_targets)
            except Exception as e:
                logger.colour_log("!error", f"Break ({label}) raised:", "!data", str(e),
                                  log_files=log_targets)


def test_prompt_with_default(function_log=None):
    """Tests CLIMenuHandler.prompt_with_default — input with optional default and validator."""
    log_targets = [TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE]

    logger.colour_log(
        "!output", "result =", "!proc", "CLIMenuHandler.", "!text", "prompt_with_default",
        "!args",   "with arguments:",
        "!data",   "prompt='Enter a value'",
        "!data",   "default='hello'",
        "!data",   "validator=None",
        "!data",   "allow_empty=False",
        log_files=log_targets
    )

    # Happy path: user enters value
    with patch("builtins.input", return_value="my_value"):
        result = menus.prompt_with_default("Enter a value", default="hello")
    logger.colour_log("!done", "ran successfully.", "!output", "Producing output:",
                      "!data", repr(result), log_files=log_targets)
    assert result == "my_value"
    logger.colour_log("!pass", "User value PASSED", log_files=log_targets)

    # Default used (empty input)
    with patch("builtins.input", return_value=""):
        result = menus.prompt_with_default("Enter:", default="fallback")
    assert result == "fallback"
    logger.colour_log("!pass", "Default fallback PASSED", log_files=log_targets)

    # Cancel returns None
    with patch("builtins.input", return_value="cancel"):
        result = menus.prompt_with_default("Enter:", default="x")
    assert result is None
    logger.colour_log("!pass", "cancel → None PASSED", log_files=log_targets)

    # Validator: only accepts digits
    def digits_only(v):
        return v.isdigit()

    with patch("builtins.input", side_effect=["abc", "xyz", "42"]):
        result = menus.prompt_with_default("Enter number:", validator=digits_only)
    assert result == "42"
    logger.colour_log("!pass", "Validator retry PASSED", log_files=log_targets)

    # allow_empty=True
    with patch("builtins.input", return_value=""):
        result = menus.prompt_with_default("Enter:", allow_empty=True)
    assert result == ""
    logger.colour_log("!pass", "allow_empty PASSED", log_files=log_targets)

    # Break inputs
    for label, val in BREAK_INPUTS[:5]:
        with patch("builtins.input", side_effect=[val, "valid"]):
            try:
                result = menus.prompt_with_default("Enter:", default="x")
                logger.colour_log("!warn", f"Break ({label}) →", "!data", repr(result),
                                  log_files=log_targets)
            except Exception as e:
                logger.colour_log("!error", f"Break ({label}) raised:", "!data", str(e),
                                  log_files=log_targets)


def test_get_numeric_choice(function_log=None):
    """Tests CLIMenuHandler.get_numeric_choice — bounded integer input with cancel."""
    log_targets = [TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE]

    logger.colour_log(
        "!output", "result =", "!proc", "CLIMenuHandler.", "!text", "get_numeric_choice",
        "!args",   "with arguments:",
        "!data",   "min_val=1",
        "!data",   "max_val=5",
        "!data",   "prompt='Select option'",
        "!data",   "allow_cancel=True",
        log_files=log_targets
    )

    # Happy path
    with patch("builtins.input", return_value="3"):
        result = menus.get_numeric_choice(1, 5)
    logger.colour_log("!done", "ran successfully.", "!output", "Producing output:",
                      "!int", result, log_files=log_targets)
    assert result == 3
    logger.colour_log("!pass", "Valid choice PASSED", log_files=log_targets)

    # Boundary: min
    with patch("builtins.input", return_value="1"):
        result = menus.get_numeric_choice(1, 5)
    assert result == 1
    logger.colour_log("!pass", "Min boundary PASSED", log_files=log_targets)

    # Boundary: max
    with patch("builtins.input", return_value="5"):
        result = menus.get_numeric_choice(1, 5)
    assert result == 5
    logger.colour_log("!pass", "Max boundary PASSED", log_files=log_targets)

    # Cancel returns None
    with patch("builtins.input", return_value="cancel"):
        result = menus.get_numeric_choice(1, 5, allow_cancel=True)
    assert result is None
    logger.colour_log("!pass", "cancel → None PASSED", log_files=log_targets)

    # Break: out-of-range then valid (should retry)
    with patch("builtins.input", side_effect=["0", "99", "abc", "3"]):
        result = menus.get_numeric_choice(1, 5)
    assert result == 3
    logger.colour_log("!pass", "Retry after invalid PASSED", log_files=log_targets)

    # Break: float input (should loop to valid)
    with patch("builtins.input", side_effect=["2.5", "2"]):
        result = menus.get_numeric_choice(1, 5)
    assert result == 2
    logger.colour_log("!pass", "Float retry PASSED", log_files=log_targets)

    # Break: empty, very long string
    with patch("builtins.input", side_effect=["", "A" * 500, "4"]):
        result = menus.get_numeric_choice(1, 5)
    assert result == 4
    logger.colour_log("!pass", "Empty/long string retry PASSED", log_files=log_targets)

    # allow_cancel=False: cancel word not accepted, loops to valid
    with patch("builtins.input", side_effect=["cancel", "3"]):
        result = menus.get_numeric_choice(1, 5, allow_cancel=False)
    assert result == 3
    logger.colour_log("!pass", "allow_cancel=False PASSED", log_files=log_targets)


def test_show_info_screen(function_log=None):
    """Tests CLIMenuHandler.show_info_screen — displays a dict of label:value pairs."""
    log_targets = [TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE]

    logger.colour_log(
        "!output", "(side-effect)", "!proc", "CLIMenuHandler.", "!text", "show_info_screen",
        "!args",   "with arguments:",
        "!data",   "title='System Info'",
        "!data",   "info={...}",
        "!data",   "wait_for_input=False",
        log_files=log_targets
    )

    sample_info = {
        "Project":   "tUilKit",
        "Version":   "0.5.0",
        "Author":    "Daniel Austin",
        "Root":      str(PROJECT_ROOT),
        "Log Folder": str(TEST_LOGS_FOLDER),
    }

    # wait_for_input=False so we don't hang
    menus.show_info_screen("System Info", sample_info, wait_for_input=False)
    logger.colour_log("!done", "show_info_screen rendered", log_files=log_targets)

    # Edge: empty dict
    menus.show_info_screen("Empty Info", {}, wait_for_input=False)
    logger.colour_log("!done", "Empty dict info screen rendered", log_files=log_targets)

    # Edge: values with special types (int, list, None)
    mixed_info = {
        "Int value":   42,
        "Bool value":  True,
        "None value":  None,
        "List value":  [1, 2, 3],
        "Long string": "X" * 200,
    }
    menus.show_info_screen("Mixed Info", mixed_info, wait_for_input=False)
    logger.colour_log("!done", "Mixed type info screen rendered", log_files=log_targets)

    # wait_for_input=True — mock the Enter press
    with patch("builtins.input", return_value=""):
        menus.show_info_screen("Wait Screen", {"key": "value"}, wait_for_input=True)
    logger.colour_log("!done", "wait_for_input=True handled", log_files=log_targets)

    logger.colour_log("!pass", "PASSED: show_info_screen complete", log_files=log_targets)


def test_edit_key_value_pairs(function_log=None):
    """Tests CLIMenuHandler.edit_key_value_pairs — interactive dict editor."""
    log_targets = [TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE]

    logger.colour_log(
        "!output", "result =", "!proc", "CLIMenuHandler.", "!text", "edit_key_value_pairs",
        "!args",   "with arguments:",
        "!data",   "title='Edit Settings'",
        "!data",   "data={'name': 'test', 'count': '5'}",
        "!data",   "prompts={...}",
        log_files=log_targets
    )

    data    = {"name": "test_project", "count": "5", "enabled": "true"}
    prompts = {"name": "Project name", "count": "Item count", "enabled": "Enabled (true/false)"}

    # Accept all defaults (empty input for each)
    with patch("builtins.input", side_effect=["", "", ""]):
        result = menus.edit_key_value_pairs("Edit Settings", data, prompts)
    logger.colour_log("!done", "ran successfully.", "!output", "Producing output:",
                      "!data", repr(result), log_files=log_targets)
    assert result["name"] == "test_project", "Default should be preserved"
    logger.colour_log("!pass", "All-defaults PASSED", log_files=log_targets)

    # Update one value
    with patch("builtins.input", side_effect=["new_name", "", ""]):
        result = menus.edit_key_value_pairs("Edit Settings", data, prompts)
    assert result["name"] == "new_name"
    logger.colour_log("!pass", "Update one value PASSED", log_files=log_targets)

    # With validator
    def non_empty(v): return len(v.strip()) > 0
    validators = {"name": non_empty}

    with patch("builtins.input", side_effect=["", "valid_name", "", ""]):
        result = menus.edit_key_value_pairs("Edit Settings", data, prompts, validators=validators)
    logger.colour_log("!info", "Validator result:", "!data", repr(result), log_files=log_targets)

    # Break: cancel during edit
    with patch("builtins.input", side_effect=["cancel", "", ""]):
        result = menus.edit_key_value_pairs("Edit Settings", data, prompts)
    logger.colour_log("!warn", "cancel input →", "!data", repr(result), log_files=log_targets)

    # Break: very long value
    with patch("builtins.input", side_effect=["A" * 500, "", ""]):
        result = menus.edit_key_value_pairs("Edit Settings", data, prompts)
    logger.colour_log("!warn", "Long value →", "!data", repr(result.get("name", ""))[:40], log_files=log_targets)

    logger.colour_log("!pass", "PASSED: edit_key_value_pairs complete", log_files=log_targets)


def test_browse_directory(function_log=None):
    """Tests CLIMenuHandler.browse_directory — directory navigator with mock input."""
    log_targets = [TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE]

    logger.colour_log(
        "!output", "result =", "!proc", "CLIMenuHandler.", "!text", "browse_directory",
        "!args",   "with arguments:",
        "!data",   f"start_path={str(PROJECT_ROOT)!r}",
        "!data",   "title='Browse'",
        "!data",   "allow_creation=False",
        log_files=log_targets
    )

    # Happy path: select current directory immediately
    with patch("builtins.input", return_value="s"):
        result = menus.browse_directory(start_path=PROJECT_ROOT, title="Browse")
    logger.colour_log("!done", "ran successfully.", "!output", "Producing output:",
                      "!path", repr(str(result)), log_files=log_targets)
    assert result == PROJECT_ROOT, f"Expected {PROJECT_ROOT}, got {result}"
    logger.colour_log("!pass", "Select current dir PASSED", log_files=log_targets)

    # Cancel returns None
    with patch("builtins.input", return_value="cancel"):
        result = menus.browse_directory(start_path=PROJECT_ROOT)
    assert result is None
    logger.colour_log("!pass", "cancel → None PASSED", log_files=log_targets)

    # Navigate to parent then select
    with patch("builtins.input", side_effect=["0", "s"]):
        result = menus.browse_directory(start_path=PROJECT_ROOT)
    logger.colour_log("!info", "Navigate parent then select →", "!path", repr(str(result)), log_files=log_targets)

    # Break: invalid numeric input then select
    with patch("builtins.input", side_effect=["999", "abc", "", "s"]):
        result = menus.browse_directory(start_path=PROJECT_ROOT)
    logger.colour_log("!warn", "Invalid inputs → eventually selected:", "!path", repr(str(result)), log_files=log_targets)

    # Non-existent start path → should fall back to cwd
    with patch("builtins.input", return_value="s"):
        result = menus.browse_directory(start_path=Path("/nonexistent/path/xyz"))
    logger.colour_log("!warn", "Nonexistent start_path →", "!path", repr(str(result)), log_files=log_targets)

    logger.colour_log("!pass", "PASSED: browse_directory complete", log_files=log_targets)


def test_show_menu_with_preview(function_log=None):
    """Tests CLIMenuHandler.show_menu_with_preview — preview function integration."""
    log_targets = [TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE]

    logger.colour_log(
        "!output", "result =", "!proc", "CLIMenuHandler.", "!text", "show_menu_with_preview",
        "!args",   "with arguments:",
        "!data",   "title='Preview Menu'",
        "!data",   "items=[{label, data}, ...]",
        "!data",   "preview_func=<fn>",
        log_files=log_targets
    )

    items = [
        {"label": "Alpha", "data": {"value": 1, "desc": "First item"}},
        {"label": "Beta",  "data": {"value": 2, "desc": "Second item"}},
        {"label": "Gamma", "data": {"value": 3, "desc": "Third item"}},
    ]

    def preview_fn(data):
        return f"Value: {data['value']}\nDesc: {data['desc']}"

    # Preview an item then select it
    with patch("builtins.input", side_effect=["1", "", "s", "1"]):
        result = menus.show_menu_with_preview("Preview Menu", items, preview_fn)
    logger.colour_log("!done", "ran successfully.", "!output", "Producing output:",
                      "!data", repr(result), log_files=log_targets)

    # Direct cancel
    with patch("builtins.input", return_value="cancel"):
        result = menus.show_menu_with_preview("Preview Menu", items, preview_fn)
    assert result is None
    logger.colour_log("!pass", "cancel → None PASSED", log_files=log_targets)

    # Break: invalid then cancel
    with patch("builtins.input", side_effect=["abc", "99", "cancel"]):
        result = menus.show_menu_with_preview("Preview Menu", items, preview_fn)
    logger.colour_log("!warn", "Invalid then cancel →", "!data", repr(result), log_files=log_targets)

    # preview_func that raises
    def bad_preview(data):
        raise ValueError("Preview failed!")

    with patch("builtins.input", side_effect=["1", "cancel"]):
        try:
            result = menus.show_menu_with_preview("Preview Menu", items, bad_preview)
            logger.colour_log("!warn", "Raising preview_func did not propagate:", "!data", repr(result), log_files=log_targets)
        except Exception as e:
            logger.colour_log("!warn", "Raising preview_func propagated:", "!data", str(e), log_files=log_targets)

    logger.colour_log("!pass", "PASSED: show_menu_with_preview complete", log_files=log_targets)


# ===========================================================================
# Examples tuple
# ===========================================================================
Examples = [
    (1, "test_show_numbered_menu",  test_show_numbered_menu,  "show_numbered_menu — all inputs incl. break"),
    (2, "test_confirm",             test_confirm,             "confirm — y/n, defaults, break inputs"),
    (3, "test_prompt_with_default", test_prompt_with_default, "prompt_with_default — value, default, validator"),
    (4, "test_get_numeric_choice",  test_get_numeric_choice,  "get_numeric_choice — bounds, retry, cancel"),
    (5, "test_show_info_screen",    test_show_info_screen,    "show_info_screen — various value types"),
    (6, "test_edit_key_value_pairs",test_edit_key_value_pairs,"edit_key_value_pairs — update, cancel, break"),
    (7, "test_browse_directory",    test_browse_directory,    "browse_directory — navigate, cancel, bad path"),
    (8, "test_show_menu_with_preview", test_show_menu_with_preview, "show_menu_with_preview — preview fn integration"),
]

# ===========================================================================
# Test runner
# ===========================================================================
results: list = []
successful: list = []
unsuccessful: list = []

for num, name, func, description in Examples:
    function_log = str(TEST_LOGS_FOLDER / f"test_log_{name}.log")
    try:
        logger.print_rainbow_row(log_files=[TEST_LOG_FILE, function_log])
        logger.apply_border(
            f"Test {num}: {name}", BORDER_PATTERN, total_length=70,
            log_files=[TEST_LOG_FILE, function_log],
            border_colour="!proc", text_colour="!text"
        )
        logger.colour_log(
            "!test", "Running:", "!int", num, "!proc", name,
            "!info", "—", "!data", description,
            log_files=[TEST_LOG_FILE, function_log]
        )
        time.sleep(0.3)
        func(function_log=function_log)
        logger.colour_log(
            "!pass", "✅ PASSED:", "!int", num, "!proc", name,
            log_files=[TEST_LOG_FILE, function_log]
        )
        results.append((num, name, True))
        successful.append(name)
    except AssertionError as e:
        logger.colour_log(
            "!fail", "❌ ASSERTION FAILED:", "!int", num,
            "!error", str(e),
            log_files=[TEST_LOG_FILE, function_log]
        )
        results.append((num, name, False))
        unsuccessful.append(name)
    except Exception as e:
        logger.log_exception(
            f"Test {num} {name} raised unexpectedly", e,
            log_files=[TEST_LOG_FILE, function_log]
        )
        results.append((num, name, False))
        unsuccessful.append(name)

# ===========================================================================
# Summary
# ===========================================================================
logger.print_rainbow_row(log_files=[TEST_LOG_FILE])
logger.apply_border("Test Summary", BORDER_PATTERN, total_length=70, log_files=[TEST_LOG_FILE])
logger.colour_log(
    "!info",  "Total:",  "!int", len(results),
    "!done",  "Passed:", "!int", len(successful),
    "!error", "Failed:", "!int", len(unsuccessful),
    log_files=[TEST_LOG_FILE]
)
for num, name, passed in results:
    key = "!pass" if passed else "!fail"
    logger.colour_log("!int", num, key, "PASS" if passed else "FAIL", "!proc", name,
                      log_files=[TEST_LOG_FILE])

elapsed = (datetime.now() - now).total_seconds()
logger.colour_log(
    "!date", datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "!info", "Duration:", "!float", f"{elapsed:.2f}s",
    log_files=[TEST_LOG_FILE]
)
