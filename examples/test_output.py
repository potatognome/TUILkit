#!/usr/bin/env python3
"""
Examples: output.py — ColourManager and Logger
Tests all public functions of ColourManager and Logger with normal, edge-case,
and adversarial inputs. Includes deliberate break attempts.
"""
import os
import sys
import time
import json
import argparse
from pathlib import Path
from datetime import datetime

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
parser = argparse.ArgumentParser(description="tUilKit output.py examples")
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
from tUilKit.factories import get_colour_manager, get_logger

colour_manager = get_colour_manager()
logger         = get_logger()

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


# ===========================================================================
# Test functions
# ===========================================================================

def test_colour_fstr(function_log=None):
    """Tests ColourManager.colour_fstr with normal, edge, and break inputs."""
    log_targets = [TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE]

    # --- call header ---
    logger.colour_log(
        "!output", "result =", "!proc", "ColourManager.", "!text", "colour_fstr",
        "!args",   "with arguments:",
        "!data",   "*args=['!info', 'hello world']",
        "!data",   "bg=None",
        "!data",   "separator=' '",
        log_files=log_targets
    )
    result = colour_manager.colour_fstr("!info", "hello world")
    logger.colour_log(
        "!done", "ran successfully.", "!output", "Producing output:",
        "!text", repr(result)[:60], "!info", "→ assigned to result",
        log_files=log_targets
    )

    # Assertion 1: basic output contains ANSI
    logger.colour_log("!test", "Assert: ANSI escape present in output", log_files=log_targets)
    assert "\033[" in result, "colour_fstr should produce ANSI escape code"
    logger.colour_log("!pass", "PASSED", log_files=log_targets)

    # Edge: empty args
    logger.colour_log(
        "!output", "result_empty =", "!proc", "ColourManager.", "!text", "colour_fstr",
        "!args", "with arguments: (none)",
        log_files=log_targets
    )
    result_empty = colour_manager.colour_fstr()
    logger.colour_log("!test", "Assert: empty args returns str", log_files=log_targets)
    assert isinstance(result_empty, str), "colour_fstr() should return str for empty args"
    logger.colour_log("!pass", "PASSED", log_files=log_targets)

    # Edge: multiple key-text pairs
    result_multi = colour_manager.colour_fstr("!info", "a", "!proc", "b", "!done", "c")
    logger.colour_log("!test", "Assert: multi-key call returns str", log_files=log_targets)
    assert isinstance(result_multi, str)
    logger.colour_log("!pass", "PASSED", log_files=log_targets)

    # Edge: custom separator
    result_sep = colour_manager.colour_fstr("!info", "x", "!proc", "y", separator="|")
    logger.colour_log("!info", "Custom separator result (first 40):", "!text", repr(result_sep)[:40], log_files=log_targets)

    # Break: unknown colour key
    result_bad = colour_manager.colour_fstr("!nonexistent_key_xyz", "value")
    logger.colour_log(
        "!warn", "Unknown key result:", "!data", repr(result_bad)[:40],
        log_files=log_targets
    )

    # Break: None as text argument (str coercion expected)
    try:
        r = colour_manager.colour_fstr("!info", None)
        logger.colour_log("!warn", "None arg did not raise — coerced to:", "!data", repr(r)[:30], log_files=log_targets)
    except Exception as e:
        logger.colour_log("!warn", "None arg raised:", "!data", str(e), log_files=log_targets)

    # Break: list argument
    try:
        r = colour_manager.colour_fstr("!info", ["a", "b", "c"])
        logger.colour_log("!info", "List arg result:", "!data", repr(r)[:40], log_files=log_targets)
    except Exception as e:
        logger.colour_log("!warn", "List arg raised:", "!data", str(e), log_files=log_targets)

    # Break: bg override
    result_bg = colour_manager.colour_fstr("!info", "bg override", bg="BLUE")
    logger.colour_log("!info", "bg override result (first 40):", "!text", repr(result_bg)[:40], log_files=log_targets)


def test_colour_path(function_log=None):
    """Tests ColourManager.colour_path with various path structures."""
    log_targets = [TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE]

    test_paths = [
        r"C:\Repo\Project\src\main.py",
        r"C:\logs\SESSION.log",
        r"C:\deep\path\to\some\folder\file.txt",
        r"relative/path.py",
        r"just_a_file.txt",
        r"",
        r"C:\\",
    ]

    for path_str in test_paths:
        logger.colour_log(
            "!output", "result =", "!proc", "ColourManager.", "!text", "colour_path",
            "!args", "with arguments:", "!path", repr(path_str),
            log_files=log_targets
        )
        try:
            result = colour_manager.colour_path(path_str)
            logger.colour_log(
                "!done", "ran successfully.", "!output", "Producing output:",
                "!text", repr(result)[:60], log_files=log_targets
            )
        except Exception as e:
            logger.colour_log("!error", "raised:", "!data", str(e), log_files=log_targets)

    # Break: non-string input
    try:
        colour_manager.colour_path(None)  # type: ignore
        logger.colour_log("!warn", "None did not raise", log_files=log_targets)
    except Exception as e:
        logger.colour_log("!warn", "None raised:", "!data", str(e), log_files=log_targets)

    try:
        colour_manager.colour_path(12345)  # type: ignore
        logger.colour_log("!warn", "Integer did not raise", log_files=log_targets)
    except Exception as e:
        logger.colour_log("!warn", "Integer raised:", "!data", str(e), log_files=log_targets)


def test_strip_ansi(function_log=None):
    """Tests ColourManager.strip_ansi — removes escape codes from strings."""
    log_targets = [TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE]

    coloured = colour_manager.colour_fstr("!info", "hello", "!done", "world")
    logger.colour_log(
        "!output", "stripped =", "!proc", "ColourManager.", "!text", "strip_ansi",
        "!args", "with arguments:", "!data", "fstring=<coloured string>",
        log_files=log_targets
    )
    stripped = colour_manager.strip_ansi(coloured)
    logger.colour_log(
        "!done", "ran successfully.", "!output", "Producing output:",
        "!text", repr(stripped), log_files=log_targets
    )

    logger.colour_log("!test", "Assert: no ANSI codes remain after strip", log_files=log_targets)
    assert "\033[" not in stripped, "strip_ansi should remove all escape codes"
    logger.colour_log("!pass", "PASSED", log_files=log_targets)

    logger.colour_log("!test", "Assert: plain text passes through unchanged", log_files=log_targets)
    plain = "hello world"
    assert colour_manager.strip_ansi(plain) == plain, "Plain text should be unchanged"
    logger.colour_log("!pass", "PASSED", log_files=log_targets)

    # Break: empty string
    assert colour_manager.strip_ansi("") == ""
    logger.colour_log("!info", "strip_ansi('') →", "!data", "''", log_files=log_targets)

    # Break: only escape codes
    only_codes = "\033[38;2;255;0;0m\033[49m"
    result = colour_manager.strip_ansi(only_codes)
    logger.colour_log("!info", "strip_ansi(codes only) →", "!data", repr(result), log_files=log_targets)
    assert result == "", "Only escape codes should strip to empty string"
    logger.colour_log("!pass", "PASSED", log_files=log_targets)


def test_interpret_codes(function_log=None):
    """Tests ColourManager.interpret_codes — replaces {KEY} tokens with ANSI."""
    log_targets = [TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE]

    test_cases = [
        ("This is {RED}red{RESET} text.",        "{RED}", "\033["),
        ("{INFO}info text",                       "{INFO}", "\033["),
        ("no codes here",                         None, None),
        ("{UNKNOWN_KEY_XYZ}value",               "{UNKNOWN_KEY_XYZ}", None),  # should stay as-is
        ("",                                      None, None),
    ]

    for text, absent_token, present_fragment in test_cases:
        logger.colour_log(
            "!output", "result =", "!proc", "ColourManager.", "!text", "interpret_codes",
            "!args", "with arguments:", "!text", repr(text)[:50],
            log_files=log_targets
        )
        try:
            result = colour_manager.interpret_codes(text)
            logger.colour_log(
                "!done", "ran successfully.", "!output", "Producing output:",
                "!text", repr(result)[:60], log_files=log_targets
            )
            if absent_token and absent_token in result:
                logger.colour_log("!warn", f"Token {absent_token!r} still present in output", log_files=log_targets)
            elif present_fragment and present_fragment not in result:
                logger.colour_log("!warn", f"Expected fragment {present_fragment!r} not found", log_files=log_targets)
            else:
                logger.colour_log("!pass", "Tokens handled correctly", log_files=log_targets)
        except Exception as e:
            logger.colour_log("!error", "raised:", "!data", str(e), log_files=log_targets)


def test_colour_log(function_log=None):
    """Tests Logger.colour_log with various argument patterns and log_files combinations."""
    log_targets = [TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE]

    logger.colour_log(
        "!output", "(side-effect only)", "!proc", "Logger.", "!text", "colour_log",
        "!args", "with arguments:", "!data", "*args (various)", "!data", "log_files",
        log_files=log_targets
    )

    # Single token
    logger.colour_log("!info", "single token call", log_files=log_targets)
    logger.colour_log("!done", "single token logged", log_files=log_targets)

    # Multiple token pairs
    logger.colour_log(
        "!info", "multi:", "!data", "val1", "!int", "42", "!proc", "step",
        log_files=log_targets
    )
    logger.colour_log("!done", "multi-token logged", log_files=log_targets)

    # No log_files → defaults
    logger.colour_log("!warn", "no log_files arg — should use category default")
    logger.colour_log("!done", "default log_files logged", log_files=log_targets)

    # log_files=None explicit
    logger.colour_log("!info", "log_files=None explicit", log_files=None)
    logger.colour_log("!done", "None log_files handled", log_files=log_targets)

    # log_files as string (single file)
    logger.colour_log("!info", "log_files as string", log_files=TEST_LOG_FILE)
    logger.colour_log("!done", "string log_files handled", log_files=log_targets)

    # spacer argument
    logger.colour_log("!info", "with spacer=2", spacer=2, log_files=log_targets)
    logger.colour_log("!done", "spacer handled", log_files=log_targets)

    # Break: no args
    try:
        logger.colour_log(log_files=log_targets)
        logger.colour_log("!warn", "Empty colour_log did not raise", log_files=log_targets)
    except Exception as e:
        logger.colour_log("!warn", "Empty colour_log raised:", "!data", str(e), log_files=log_targets)

    # Break: unknown colour key
    logger.colour_log("!nonexistent_xyz", "unknown key value", log_files=log_targets)
    logger.colour_log("!done", "Unknown key handled without crash", log_files=log_targets)

    logger.colour_log("!pass", "PASSED: colour_log break tests complete", log_files=log_targets)


def test_print_rainbow_row(function_log=None):
    """Tests Logger.print_rainbow_row with various patterns and spacings."""
    log_targets = [TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE]

    logger.colour_log(
        "!output", "(side-effect)", "!proc", "Logger.", "!text", "print_rainbow_row",
        "!args", "with arguments:", "!data", "pattern", "!data", "spacer",
        log_files=log_targets
    )

    for pattern, spacer in [("X-O-", 0), ("=-", 1), ("*", 2), ("ABC", 0)]:
        logger.colour_log(
            "!info", "pattern=", "!text", pattern, "!info", "spacer=", "!int", spacer,
            log_files=log_targets
        )
        logger.print_rainbow_row(pattern=pattern, spacer=spacer, log_files=log_targets)

    # Break: empty pattern
    try:
        logger.print_rainbow_row(pattern="", log_files=log_targets)
        logger.colour_log("!warn", "Empty pattern did not raise", log_files=log_targets)
    except Exception as e:
        logger.colour_log("!warn", "Empty pattern raised:", "!data", str(e), log_files=log_targets)

    # Break: very long pattern
    logger.print_rainbow_row(pattern="A" * 200, log_files=log_targets)
    logger.colour_log("!info", "Long pattern handled", log_files=log_targets)

    logger.colour_log("!pass", "PASSED: print_rainbow_row complete", log_files=log_targets)


def test_apply_border(function_log=None):
    """Tests Logger.apply_border with normal text, multiline text, and break inputs."""
    log_targets = [TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE]

    logger.colour_log(
        "!output", "(side-effect)", "!proc", "Logger.", "!text", "apply_border",
        "!args", "with arguments:", "!data", "text", "!data", "pattern",
        "!data", "total_length", "!data", "border_colour", "!data", "text_colour",
        log_files=log_targets
    )

    pattern = {"TOP": "=", "BOTTOM": "=", "LEFT": "| ", "RIGHT": " |"}

    # Normal usage
    logger.apply_border("Normal border test", pattern, total_length=60,
                        log_files=log_targets, border_colour="!proc", text_colour="!text")
    logger.colour_log("!done", "Normal border rendered", log_files=log_targets)

    # Short text
    logger.apply_border("X", pattern, total_length=60, log_files=log_targets)
    logger.colour_log("!done", "Short text border rendered", log_files=log_targets)

    # Empty text
    try:
        logger.apply_border("", pattern, total_length=60, log_files=log_targets)
        logger.colour_log("!warn", "Empty text border — check output", log_files=log_targets)
    except Exception as e:
        logger.colour_log("!warn", "Empty text raised:", "!data", str(e), log_files=log_targets)

    # Very long text
    long_text = "A" * 200
    logger.apply_border(long_text, pattern, total_length=60, log_files=log_targets)
    logger.colour_log("!warn", "Long text border — check wrapping/overflow", log_files=log_targets)

    # Special characters
    logger.apply_border("Special: ✅❌🔥 \x00\t", pattern, total_length=60, log_files=log_targets)
    logger.colour_log("!warn", "Special chars border — check rendering", log_files=log_targets)

    # Border rainbow
    logger.apply_border("Rainbow border", pattern, total_length=60,
                        border_rainbow=True, log_files=log_targets)
    logger.colour_log("!done", "Rainbow border rendered", log_files=log_targets)

    logger.colour_log("!pass", "PASSED: apply_border complete", log_files=log_targets)


def test_log_exception(function_log=None):
    """Tests Logger.log_exception with various exception types."""
    log_targets = [TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE]

    logger.colour_log(
        "!output", "(side-effect)", "!proc", "Logger.", "!text", "log_exception",
        "!args", "with arguments:", "!data", "description", "!data", "exception",
        "!data", "category", "!data", "log_files",
        log_files=log_targets
    )

    for exc_type, exc_val in [
        (ValueError,        ValueError("bad value")),
        (FileNotFoundError, FileNotFoundError("no such file")),
        (TypeError,         TypeError("wrong type")),
        (KeyError,          KeyError("missing_key")),
        (RuntimeError,      RuntimeError("something went wrong")),
    ]:
        logger.colour_log(
            "!info", "Testing exception type:", "!text", exc_type.__name__,
            log_files=log_targets
        )
        logger.log_exception(
            f"Deliberate {exc_type.__name__} during examples",
            exc_val,
            log_files=log_targets
        )
        logger.colour_log("!done", f"{exc_type.__name__} logged without crash", log_files=log_targets)

    logger.colour_log("!pass", "PASSED: log_exception complete", log_files=log_targets)


# ===========================================================================
# Examples tuple
# ===========================================================================
Examples = [
    (1, "test_colour_fstr",     test_colour_fstr,     "colour_fstr — normal, edge, and break inputs"),
    (2, "test_colour_path",     test_colour_path,     "colour_path — various path structures"),
    (3, "test_strip_ansi",      test_strip_ansi,      "strip_ansi — removes escape codes"),
    (4, "test_interpret_codes", test_interpret_codes, "interpret_codes — {KEY} token replacement"),
    (5, "test_colour_log",      test_colour_log,      "colour_log — argument patterns and log_files"),
    (6, "test_print_rainbow_row", test_print_rainbow_row, "print_rainbow_row — patterns and spacers"),
    (7, "test_apply_border",    test_apply_border,    "apply_border — normal, long, and break inputs"),
    (8, "test_log_exception",   test_log_exception,   "log_exception — various exception types"),
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
