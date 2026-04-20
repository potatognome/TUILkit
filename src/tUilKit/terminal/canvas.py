"""
canvas.py - Multi-line rendering surface for in-place redraws using Cursor and Chroma.
Pure rendering logic, no side effects.
"""
from tUilKit.terminal.cursor import Cursor

class Canvas:
    def __init__(self):
        self.last_frame = []
        self.line_count = 0
        self._ansi = None

    def _supports_cursor(self):
        if self._ansi is not None:
            return self._ansi
        # Use Cursor.up(1) as proxy for ANSI support
        self._ansi = bool(Cursor.up(1))
        return self._ansi

    def draw(self, lines):
        """Initial render. Returns string to print."""
        self.last_frame = list(lines)
        self.line_count = len(lines)
        return "\n".join(lines) + ("\n" if lines else "")

    def redraw(self, lines):
        """In-place update. Returns string to print."""
        if not self._supports_cursor():
            # Fallback: just append new output
            self.last_frame = list(lines)
            self.line_count = len(lines)
            return "\n".join(lines) + ("\n" if lines else "")
        # Move cursor up to start of frame
        out = []
        if self.line_count:
            out.append(Cursor.up(self.line_count))
        # Clear each line and print new
        for line in lines:
            out.append(Cursor.clear_line())
            out.append(line)
            out.append("\n")
        self.last_frame = list(lines)
        self.line_count = len(lines)
        return "".join(out)

    def clear(self):
        self.last_frame = []
        self.line_count = 0
        self._ansi = None

    def as_text(self, lines):
        """Return plain text for testing (no ANSI)."""
        return "\n".join(lines) + ("\n" if lines else "")
