"""
cursor.py - ANSI cursor movement and screen control utilities for tUilKit
Pure functions, namespace-style class. No side effects.
"""

from tUilKit.utils import is_ansi_supported

class Cursor:
    """Namespace for ANSI cursor and screen control codes."""
    @staticmethod
    def up(n=1):
        if not is_ansi_supported():
            return ""
        return f"\033[{n}A"

    @staticmethod
    def down(n=1):
        if not is_ansi_supported():
            return ""
        return f"\033[{n}B"

    @staticmethod
    def right(n=1):
        if not is_ansi_supported():
            return ""
        return f"\033[{n}C"

    @staticmethod
    def left(n=1):
        if not is_ansi_supported():
            return ""
        return f"\033[{n}D"

    @staticmethod
    def clear_line():
        if not is_ansi_supported():
            return "\n"
        return "\033[2K"

    @staticmethod
    def clear_screen():
        if not is_ansi_supported():
            return ""
        return "\033[2J"

    @staticmethod
    def hide():
        if not is_ansi_supported():
            return ""
        return "\033[?25l"

    @staticmethod
    def show():
        if not is_ansi_supported():
            return ""
        return "\033[?25h"
