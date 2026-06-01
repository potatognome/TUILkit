"""
Tests for Style dataclass and AnsiRenderBackend.
"""
import io
import pytest
from tUilKit.output.backend.backend import Style
from tUilKit.output.backend.ansi_backend import AnsiRenderBackend


# ---------------------------------------------------------------------------
# Style
# ---------------------------------------------------------------------------

class TestStyle:
    def test_defaults(self):
        s = Style()
        assert s.fg == ""
        assert s.bg == ""
        assert not s.bold
        assert not s.dim
        assert not s.underline
        assert not s.reverse

    def test_equality(self):
        assert Style() == Style()
        assert Style(bold=True) != Style()

    def test_custom_fields(self):
        s = Style(fg="\033[31m", bold=True, reverse=True)
        assert s.fg == "\033[31m"
        assert s.bold
        assert s.reverse


# ---------------------------------------------------------------------------
# AnsiRenderBackend
# ---------------------------------------------------------------------------

class TestAnsiRenderBackend:
    def _backend(self):
        stream = io.StringIO()
        backend = AnsiRenderBackend(stream=stream)
        return backend, stream

    def test_draw_rune_appears_on_flush(self):
        b, stream = self._backend()
        b.draw_rune(0, 0, "X", Style())
        b.flush()
        out = stream.getvalue()
        assert "X" in out

    def test_absolute_cursor_positioning(self):
        b, stream = self._backend()
        # Column 5, row 3 → ANSI row=4, col=6 (1-indexed)
        b.draw_rune(5, 3, "A", Style())
        b.flush()
        out = stream.getvalue()
        assert "\033[4;6H" in out

    def test_draw_string_stages_multiple_cells(self):
        b, stream = self._backend()
        b.draw_string(2, 1, "Hi", Style())
        b.flush()
        out = stream.getvalue()
        assert "H" in out
        assert "i" in out

    def test_no_flush_when_nothing_changed(self):
        b, stream = self._backend()
        b.draw_rune(0, 0, "X", Style())
        b.flush()
        first = stream.getvalue()
        # Draw the exact same cell again — should produce no additional output.
        b.draw_rune(0, 0, "X", Style())
        b.flush()
        second = stream.getvalue()
        assert first == second

    def test_back_buffer_cleared_after_flush(self):
        b, stream = self._backend()
        b.draw_rune(1, 1, "Z", Style())
        b.flush()
        # After flush the back buffer must be empty.
        assert b._back == {}

    def test_clear_region_fills_with_spaces(self):
        b, stream = self._backend()
        b.clear_region(0, 0, 3, 2)
        assert all(b._back[(col, row)] == (" ", Style()) for row in range(2) for col in range(3))

    def test_bold_style_emits_ansi_codes(self):
        b, stream = self._backend()
        b.draw_rune(0, 0, "B", Style(bold=True))
        b.flush()
        out = stream.getvalue()
        # Bold attribute should produce \033[1m somewhere in the output.
        assert "\033[1m" in out

    def test_dim_style_emits_ansi_codes(self):
        b, stream = self._backend()
        b.draw_rune(0, 0, "D", Style(dim=True))
        b.flush()
        out = stream.getvalue()
        assert "\033[2m" in out

    def test_only_first_char_of_rune_stored(self):
        b, _ = self._backend()
        b.draw_rune(0, 0, "ABC", Style())
        assert b._back[(0, 0)][0] == "A"
