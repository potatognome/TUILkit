"""
Test Cursor ANSI cursor movement and fallback logic.
"""
import sys
import types
import pytest

from tUilKit.terminal.cursor import Cursor

# Helper to patch is_ansi_supported
class AnsiPatch:
    def __init__(self, value):
        self.value = value
        self.orig = None
    def __enter__(self):
        import tUilKit.utils.ansi
        self.orig = tUilKit.utils.ansi.is_ansi_supported
        tUilKit.utils.ansi.is_ansi_supported = lambda: self.value
    def __exit__(self, exc_type, exc_val, exc_tb):
        import tUilKit.utils.ansi
        tUilKit.utils.ansi.is_ansi_supported = self.orig

def test_cursor_ansi_enabled():
    with AnsiPatch(True):
        assert Cursor.up(3) == "\033[3A"
        assert Cursor.down(2) == "\033[2B"
        assert Cursor.right(5) == "\033[5C"
        assert Cursor.left(4) == "\033[4D"
        assert Cursor.clear_line() == "\033[2K"
        assert Cursor.clear_screen() == "\033[2J"
        assert Cursor.hide() == "\033[?25l"
        assert Cursor.show() == "\033[?25h"

def test_cursor_ansi_disabled():
    with AnsiPatch(False):
        assert Cursor.up(3) == ""
        assert Cursor.down(2) == ""
        assert Cursor.right(5) == ""
        assert Cursor.left(4) == ""
        assert Cursor.clear_line() == "\n"
        assert Cursor.clear_screen() == ""
        assert Cursor.hide() == ""
        assert Cursor.show() == ""
