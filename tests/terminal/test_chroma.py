"""
Test Chroma ANSI colour/style and fallback logic.
"""
import os
import sys
import types
import pytest

from tUilKit.terminal.chroma import Chroma
from tUilKit.dict.ansi_colours import FG_COLOURS, BG_COLOURS, STYLES

def patch_ansi(val):
    orig = Chroma.supports_ansi
    Chroma.supports_ansi = staticmethod(lambda: val)
    return orig

def test_fgset_bgset_ansi(monkeypatch):
    orig = patch_ansi(True)
    assert Chroma.fgset("red") == FG_COLOURS["red"]
    assert Chroma.bgset("blue") == BG_COLOURS["blue"]
    Chroma.supports_ansi = orig

def test_fgset_bgset_noansi(monkeypatch):
    orig = patch_ansi(False)
    assert Chroma.fgset("red") == ""
    assert Chroma.bgset("blue") == ""
    Chroma.supports_ansi = orig

def test_bold_dim_apply(monkeypatch):
    orig = patch_ansi(True)
    s = Chroma.bold("hi")
    assert s.startswith(STYLES["bold"])
    assert s.endswith(STYLES["reset"])
    s2 = Chroma.dim("hi")
    assert s2.startswith(STYLES["dim"])
    assert s2.endswith(STYLES["reset"])
    s3 = Chroma.apply("hi", STYLES["bold"], STYLES["dim"])
    assert s3.startswith(STYLES["bold"] + STYLES["dim"])
    assert s3.endswith(STYLES["reset"])
    Chroma.supports_ansi = orig

def test_apply_noansi(monkeypatch):
    orig = patch_ansi(False)
    assert Chroma.apply("hi", STYLES["bold"]) == "hi"
    Chroma.supports_ansi = orig

def test_rainbowtext(monkeypatch):
    orig = patch_ansi(True)
    s = Chroma.rainbowtext("hello")
    assert all(FG_COLOURS[c] in s for c in ["red", "yellow", "green", "cyan", "blue"])
    assert s.endswith(STYLES["reset"])
    Chroma.supports_ansi = orig

def test_rainbowtext_noansi(monkeypatch):
    orig = patch_ansi(False)
    assert Chroma.rainbowtext("hello") == "hello"
    Chroma.supports_ansi = orig

def test_env_override(monkeypatch):
    monkeypatch.setenv("TUILKIT_FORCE_ANSI", "1")
    assert Chroma.supports_ansi() is True
    monkeypatch.setenv("TUILKIT_FORCE_ANSI", "0")
    assert Chroma.supports_ansi() is False
    monkeypatch.delenv("TUILKIT_FORCE_ANSI", raising=False)
