"""
Tests for Rect and DrawContext.
"""
import pytest
from tUilKit.output.draw.draw_context import Rect, DrawContext
from tUilKit.output.backend.backend import Style


# ---------------------------------------------------------------------------
# Rect
# ---------------------------------------------------------------------------

class TestRect:
    def test_contains_inside(self):
        r = Rect(2, 3, 5, 4)
        assert r.contains(2, 3)   # top-left
        assert r.contains(6, 6)   # bottom-right (inclusive limit)
        assert r.contains(4, 5)   # middle

    def test_contains_outside(self):
        r = Rect(2, 3, 5, 4)
        assert not r.contains(1, 3)   # left of rect
        assert not r.contains(7, 3)   # right boundary (exclusive)
        assert not r.contains(2, 7)   # below bottom boundary (exclusive)

    def test_intersects_overlapping(self):
        r1 = Rect(0, 0, 5, 5)
        r2 = Rect(3, 3, 5, 5)
        assert r1.intersects(r2)
        assert r2.intersects(r1)

    def test_intersects_adjacent_no_overlap(self):
        r1 = Rect(0, 0, 5, 5)
        r2 = Rect(5, 0, 5, 5)
        assert not r1.intersects(r2)


# ---------------------------------------------------------------------------
# Mock surface to capture draw calls
# ---------------------------------------------------------------------------

class MockSurface:
    def __init__(self):
        self.calls: list = []

    def draw_rune(self, x, y, ch, style):
        self.calls.append(("rune", x, y, ch))

    def draw_string(self, x, y, s, style):
        self.calls.append(("string", x, y, s))


# ---------------------------------------------------------------------------
# DrawContext
# ---------------------------------------------------------------------------

class TestDrawContext:
    def _ctx(self, cx=0, cy=0, cw=10, ch=10, ox=0, oy=0):
        surf = MockSurface()
        clip = Rect(cx, cy, cw, ch)
        ctx = DrawContext(surf, clip, ox, oy)
        return ctx, surf

    def test_draw_rune_inside_clip(self):
        ctx, surf = self._ctx(cx=0, cy=0, cw=10, ch=10, ox=0, oy=0)
        ctx.draw_rune(3, 3, "X", Style())
        assert ("rune", 3, 3, "X") in surf.calls

    def test_draw_rune_outside_clip_discarded(self):
        ctx, surf = self._ctx(cx=0, cy=0, cw=5, ch=5, ox=0, oy=0)
        ctx.draw_rune(5, 5, "X", Style())   # exactly on boundary (exclusive)
        assert not surf.calls

    def test_draw_rune_applies_offset(self):
        ctx, surf = self._ctx(cx=10, cy=10, cw=5, ch=5, ox=10, oy=10)
        # local (0, 0) → screen (10, 10)
        ctx.draw_rune(0, 0, "A", Style())
        assert ("rune", 10, 10, "A") in surf.calls

    def test_draw_string_clips_partial(self):
        # clip is cols 0-4, string starts at col 3 and has 4 chars
        ctx, surf = self._ctx(cx=0, cy=0, cw=5, ch=5, ox=0, oy=0)
        ctx.draw_string(3, 0, "ABCD", Style())
        drawn_cols = {c[1] for c in surf.calls}
        assert 3 in drawn_cols
        assert 4 in drawn_cols
        assert 5 not in drawn_cols
        assert 6 not in drawn_cols

    def test_empty_ch_discarded(self):
        ctx, surf = self._ctx()
        ctx.draw_rune(0, 0, "", Style())
        assert not surf.calls

    def test_width_height_properties(self):
        ctx, surf = self._ctx(cw=20, ch=15)
        assert ctx.width == 20
        assert ctx.height == 15

    def test_sub_context_clips_correctly(self):
        ctx, surf = self._ctx(cx=0, cy=0, cw=10, ch=10, ox=0, oy=0)
        sub = ctx.sub_context(2, 2, 4, 4)
        # sub context local (0,0) → screen (2,2)
        sub.draw_rune(0, 0, "S", Style())
        assert ("rune", 2, 2, "S") in surf.calls

    def test_sub_context_cannot_exceed_parent_clip(self):
        ctx, surf = self._ctx(cx=0, cy=0, cw=5, ch=5, ox=0, oy=0)
        sub = ctx.sub_context(3, 3, 10, 10)  # tries to go beyond parent
        sub.draw_rune(5, 5, "X", Style())     # well outside parent clip
        # the draw should be discarded
        assert not surf.calls
