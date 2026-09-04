#!/usr/bin/env python3
"""Regression checks for the logger interface and implementation contract."""

from __future__ import annotations

import sys
from inspect import _empty, getsource, signature
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from tUilKit.interfaces.logger_interface import LoggerInterface
from tUilKit.utils.output import Logger


def main() -> int:
    def normalized(method):
        sig = signature(method)
        return [
            (param.name, param.kind, param.default if param.default is not _empty else _empty)
            for param in sig.parameters.values()
        ]

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
        assert normalized(interface_method) == normalized(
            implementation_method
        ), f"Signature mismatch for {name}"

    info_source = getsource(Logger.info)
    exception_source = getsource(Logger.exception)
    log_exception_source = getsource(Logger.log_exception)

    assert "!reset" in info_source and "!info" not in info_source, "Logger.info should use !reset"
    assert "!reset" in log_exception_source and "!info" not in log_exception_source, (
        "Logger.log_exception should use !reset for neutral text"
    )
    assert "log_exception" in exception_source, "Logger.exception should delegate to log_exception when exc is provided"

    print("logger contract checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
