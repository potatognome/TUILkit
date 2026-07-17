#!/usr/bin/env python3
"""Lightweight manual AI quality gate for tUilKit changes.

Usage:
    python scripts/ai_quality_gate.py
    python scripts/ai_quality_gate.py --strict
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ABS_PATH_RE = re.compile(r"[A-Za-z]:\\\\")
SCAN_SUFFIXES = {".py", ".md", ".json", ".yaml", ".yml", ".toml", ".txt"}


def run_git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git command failed")
    return result.stdout


def changed_files() -> list[str]:
    status = run_git("status", "--porcelain", "--untracked-files=all")
    files: list[str] = []
    for line in status.splitlines():
        # format: XY <path> or XY <old> -> <new>
        if not line.strip():
            continue
        payload = line[3:]
        if " -> " in payload:
            payload = payload.split(" -> ", 1)[1]
        files.append(payload.strip())
    return sorted(set(files))


def scan_for_absolute_paths(paths: list[str]) -> list[str]:
    findings: list[str] = []
    for rel in paths:
        path = REPO_ROOT / rel
        if path.suffix.lower() not in SCAN_SUFFIXES:
            continue
        if not path.exists() or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if ABS_PATH_RE.search(text):
            findings.append(rel)
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Run tUilKit AI quality checks.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as failures.",
    )
    args = parser.parse_args()

    try:
        files = changed_files()
    except RuntimeError as exc:
        print(f"[FAIL] Could not inspect git status: {exc}")
        return 2

    if not files:
        print("[PASS] No local changes detected.")
        return 0

    changed = set(files)
    has_src_change = any(f.startswith("src/") for f in changed)
    has_test_change = any(f.startswith("tests/") for f in changed)
    has_doc_change = "README.md" in changed or "CHANGELOG.md" in changed
    has_version_change = any(f in changed for f in ("pyproject.toml", "setup.py"))

    warnings: list[str] = []
    failures: list[str] = []

    if has_src_change and not has_test_change:
        warnings.append("Source changes detected without test changes under tests/.")

    if has_src_change and not has_doc_change:
        warnings.append("Source changes detected without README.md or CHANGELOG.md updates.")

    if has_version_change and "CHANGELOG.md" not in changed:
        warnings.append("Version metadata changed without CHANGELOG.md update.")

    abs_path_hits = scan_for_absolute_paths(files)
    if abs_path_hits:
        failures.append(
            "Possible machine-specific absolute paths found in: " + ", ".join(abs_path_hits)
        )

    print("Changed files:")
    for f in files:
        print(f"- {f}")

    for msg in failures:
        print(f"[FAIL] {msg}")

    for msg in warnings:
        level = "FAIL" if args.strict else "WARN"
        print(f"[{level}] {msg}")
        if args.strict:
            failures.append(msg)

    if failures:
        print("\nResult: FAILED")
        return 1

    if warnings:
        print("\nResult: PASSED WITH WARNINGS")
        return 0

    print("\nResult: PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
