"""
Test Canvas multi-line rendering and in-place redraw logic.
"""
import pytest
from tUilKit.terminal.canvas import Canvas
from tUilKit.terminal.cursor import Cursor

def patch_cursor_ansi(val):
    orig = Cursor.up
    Cursor.up = staticmethod(lambda n=1: "\033[{n}A" if val else "")
    return orig

def test_draw_and_as_text():
    c = Canvas()
    lines = ["A", "B", "C"]
    out = c.draw(lines)
    assert out == "A\nB\nC\n"
    assert c.as_text(lines) == "A\nB\nC\n"

def test_redraw_ansi(monkeypatch):
    c = Canvas()
    patch_cursor_ansi(True)
    c.draw(["A", "B"])
    out = c.redraw(["X", "Y"])
    # Should move up 2, clear, print X, clear, print Y
    assert "\033[2A" in out
    assert out.count(Cursor.clear_line()) == 2
    assert "X" in out and "Y" in out

def test_redraw_fallback(monkeypatch):
    c = Canvas()
    patch_cursor_ansi(False)
    c.draw(["A", "B"])
    out = c.redraw(["X", "Y"])
    # Should just append new output
    assert out == "X\nY\n"

def test_clear():
    c = Canvas()
    c.draw(["A"])
    c.clear()
    assert c.last_frame == []
    assert c.line_count == 0
