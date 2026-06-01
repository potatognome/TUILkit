"""
Tests for Widget, TextWidget, and FilledWidget.
"""
import pytest
from tUilKit.output.widgets.widget import Widget, TextWidget, FilledWidget
from tUilKit.output.draw.draw_context import DrawContext, Rect
from tUilKit.output.backend.backend import Style


# ---------------------------------------------------------------------------
# Mock surface
# ---------------------------------------------------------------------------

class MockSurface:
    def __init__(self):
        self.cells: dict = {}

    def draw_rune(self, x, y, ch, style):
        self.cells[(x, y)] = ch

    def draw_string(self, x, y, s, style):
        for i, ch in enumerate(s):
            self.draw_rune(x + i, y, ch, style)


def _make_ctx(w=20, h=10):
    surf = MockSurface()
    clip = Rect(0, 0, w, h)
    ctx = DrawContext(surf, clip, 0, 0)
    return ctx, surf


# ---------------------------------------------------------------------------
# Widget base
# ---------------------------------------------------------------------------

class TestWidget:
    def test_measure_returns_assigned_dims(self):
        class ConcreteWidget(Widget):
            def render(self, ctx):
                pass

        w = ConcreteWidget()
        w.layout(0, 0, 10, 5)
        assert w.measure() == (10, 5)

    def test_layout_sets_position_and_size(self):
        class ConcreteWidget(Widget):
            def render(self, ctx):
                pass

        w = ConcreteWidget()
        w.layout(3, 7, 15, 8)
        assert w.x == 3
        assert w.y == 7
        assert w.width == 15
        assert w.height == 8


# ---------------------------------------------------------------------------
# TextWidget
# ---------------------------------------------------------------------------

class TestTextWidget:
    def test_measure_reflects_text_length(self):
        tw = TextWidget("Hello")
        assert tw.measure() == (5, 1)

    def test_render_draws_text(self):
        ctx, surf = _make_ctx()
        tw = TextWidget("Hi", Style())
        tw.render(ctx)
        assert surf.cells.get((0, 0)) == "H"
        assert surf.cells.get((1, 0)) == "i"

    def test_render_empty_text(self):
        ctx, surf = _make_ctx()
        TextWidget("").render(ctx)
        assert surf.cells == {}

    def test_render_clips_long_text(self):
        # Context is only 3 cells wide.
        ctx, surf = _make_ctx(w=3, h=1)
        TextWidget("Hello World", Style()).render(ctx)
        # Only first 3 characters should be drawn.
        assert (0, 0) in surf.cells
        assert (1, 0) in surf.cells
        assert (2, 0) in surf.cells
        assert (3, 0) not in surf.cells


# ---------------------------------------------------------------------------
# FilledWidget
# ---------------------------------------------------------------------------

class TestFilledWidget:
    def test_render_fills_area(self):
        ctx, surf = _make_ctx(w=3, h=2)
        FilledWidget("*", Style()).render(ctx)
        expected = {(c, r) for r in range(2) for c in range(3)}
        assert set(surf.cells.keys()) == expected
        assert all(v == "*" for v in surf.cells.values())

    def test_first_char_only(self):
        fw = FilledWidget("AB")
        assert fw.ch == "A"

    def test_empty_ch_defaults_to_space(self):
        fw = FilledWidget("")
        assert fw.ch == " "
