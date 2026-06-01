"""
Tests for border drawing utilities.
"""
import pytest
from tUilKit.output.draw.draw_context import DrawContext, Rect
from tUilKit.output.draw.border import (
    draw_border,
    draw_titled_border,
    get_border_chars,
    _BORDER_CHARS,
)
from tUilKit.output.backend.backend import Style


# ---------------------------------------------------------------------------
# Helper surface
# ---------------------------------------------------------------------------

class CaptureCtx:
    """A minimal surface+context that records every draw_rune call."""

    def __init__(self, w=40, h=20):
        self.cells: dict[tuple[int, int], str] = {}
        clip = Rect(0, 0, w, h)
        self.ctx = DrawContext(self, clip, 0, 0)

    def draw_rune(self, x, y, ch, style):
        self.cells[(x, y)] = ch

    def draw_string(self, x, y, s, style):
        for i, ch in enumerate(s):
            self.draw_rune(x + i, y, ch, style)


# ---------------------------------------------------------------------------
# get_border_chars
# ---------------------------------------------------------------------------

class TestGetBorderChars:
    def test_known_styles(self):
        for style in ("single", "double", "heavy", "rounded"):
            chars = get_border_chars(style)
            for key in ("tl", "tr", "bl", "br", "h", "v"):
                assert key in chars and chars[key]

    def test_unknown_style_defaults_to_single(self):
        chars = get_border_chars("invalid_style")
        assert chars == _BORDER_CHARS["single"]


# ---------------------------------------------------------------------------
# draw_border
# ---------------------------------------------------------------------------

class TestDrawBorder:
    def _draw(self, w, h, style="single"):
        cap = CaptureCtx(w, h)
        rect = Rect(0, 0, w, h)
        draw_border(cap.ctx, rect, style, Style())
        return cap.cells

    def test_corners_single(self):
        cells = self._draw(5, 4, "single")
        chars = _BORDER_CHARS["single"]
        assert cells[(0, 0)] == chars["tl"]
        assert cells[(4, 0)] == chars["tr"]
        assert cells[(0, 3)] == chars["bl"]
        assert cells[(4, 3)] == chars["br"]

    def test_corners_double(self):
        cells = self._draw(5, 4, "double")
        chars = _BORDER_CHARS["double"]
        assert cells[(0, 0)] == chars["tl"]
        assert cells[(4, 0)] == chars["tr"]

    def test_corners_heavy(self):
        cells = self._draw(5, 4, "heavy")
        chars = _BORDER_CHARS["heavy"]
        assert cells[(0, 0)] == chars["tl"]

    def test_corners_rounded(self):
        cells = self._draw(5, 4, "rounded")
        chars = _BORDER_CHARS["rounded"]
        assert cells[(0, 0)] == chars["tl"]

    def test_horizontal_edges(self):
        cells = self._draw(6, 4, "single")
        h_char = _BORDER_CHARS["single"]["h"]
        for col in range(1, 5):
            assert cells.get((col, 0)) == h_char
            assert cells.get((col, 3)) == h_char

    def test_vertical_edges(self):
        cells = self._draw(6, 5, "single")
        v_char = _BORDER_CHARS["single"]["v"]
        for row in range(1, 4):
            assert cells.get((0, row)) == v_char
            assert cells.get((5, row)) == v_char

    def test_too_small_noop(self):
        cap = CaptureCtx(1, 1)
        draw_border(cap.ctx, Rect(0, 0, 1, 1), "single", Style())
        assert cap.cells == {}


# ---------------------------------------------------------------------------
# draw_titled_border
# ---------------------------------------------------------------------------

class TestDrawTitledBorder:
    def test_title_appears_in_top_edge(self):
        cap = CaptureCtx(20, 5)
        draw_titled_border(cap.ctx, Rect(0, 0, 20, 5), "single", "Hello", Style())
        top_row = "".join(cap.cells.get((col, 0), " ") for col in range(20))
        assert "Hello" in top_row

    def test_no_title_no_extra_chars(self):
        cap1 = CaptureCtx(20, 5)
        cap2 = CaptureCtx(20, 5)
        draw_border(cap1.ctx, Rect(0, 0, 20, 5), "single", Style())
        draw_titled_border(cap2.ctx, Rect(0, 0, 20, 5), "single", "", Style())
        assert cap1.cells == cap2.cells
