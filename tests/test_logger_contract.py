#!/usr/bin/env python3
"""Regression checks for the logger interface and implementation contract."""

from __future__ import annotations

import sys
import tempfile
from inspect import _empty, signature
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from tUilKit.interfaces.logger_interface import LoggerInterface
from tUilKit.utils.output import Logger


class _Recorder:
    def __init__(self):
        self.calls = []
        self.log_files = {}

    def _get_log_files(self, category):
        return []

    def colour_log(self, *args, **kwargs):
        self.calls.append(("colour_log", args, kwargs))
        message = " ".join(str(arg) for arg in args)
        for log_file in kwargs.get("log_files", []) or []:
            path = Path(log_file)
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as handle:
                handle.write(message + "\n")

    def log_exception(self, *args, **kwargs):
        self.calls.append(("log_exception", args, kwargs))


def _normalized(method):
    sig = signature(method)
    return [
        (param.name, param.kind, param.default if param.default is not _empty else _empty)
        for param in sig.parameters.values()
    ]


def test_logger_interface_matches_implementation():
    signature_pairs = [
        ("log_message", LoggerInterface.log_message, Logger.log_message),
        ("log_exception", LoggerInterface.log_exception, Logger.log_exception),
        ("colour_log", LoggerInterface.colour_log, Logger.colour_log),
        ("log_done", LoggerInterface.log_done, Logger.log_done),
        ("print_top_border", LoggerInterface.print_top_border, Logger.print_top_border),
        ("print_text_line", LoggerInterface.print_text_line, Logger.print_text_line),
        ("print_bottom_border", LoggerInterface.print_bottom_border, Logger.print_bottom_border),
        ("apply_border", LoggerInterface.apply_border, Logger.apply_border),
    ]

    for name, interface_method, implementation_method in signature_pairs:
        assert _normalized(interface_method) == _normalized(
            implementation_method
        ), f"Signature mismatch for {name}"


def test_logger_info_uses_reset():
    recorder = _Recorder()

    Logger.info(recorder, "alpha")
    assert recorder.calls[-1][1][0] == "!reset", "Logger.info should use !reset"


def test_logger_log_exception_uses_reset():
    recorder = _Recorder()

    Logger.log_exception(recorder, "problem", ValueError("boom"))
    colour_calls = [call for call in recorder.calls if call[0] == "colour_log"]
    assert any(call[1][:4] == ("!error", "UNEXPECTED ERROR:", "!reset", "problem") for call in colour_calls), (
        "Logger.log_exception should use !reset for neutral text"
    )


def test_logger_exception_delegates_to_log_exception():
    recorder = _Recorder()

    Logger.exception(recorder, "problem", exc=ValueError("boom"))
    assert recorder.calls and recorder.calls[0][0] == "log_exception", (
        "Logger.exception should delegate to log_exception when exc is provided"
    )


def test_logger_contract_logs_pass_message():
    with tempfile.TemporaryDirectory(prefix="tuilkit-logger-contract-") as temp_dir:
        logger = _Recorder()
        log_file = Path(temp_dir) / "test_logger_contract.log"
        logger.colour_log("!pass", "logger contract checks passed", log_files=[str(log_file)])
        assert log_file.exists()


def main() -> int:
    test_logger_interface_matches_implementation()
    test_logger_info_uses_reset()
    test_logger_log_exception_uses_reset()
    test_logger_exception_delegates_to_log_exception()
    test_logger_contract_logs_pass_message()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
