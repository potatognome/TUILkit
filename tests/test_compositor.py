"""
Integration tests for the Compositor.

These tests verify that the full pipeline — WindowManager → Compositor →
RenderBackend — works correctly: borders are drawn, content widgets paint
into their window's content area, z-order is respected, and only changed
cells are flushed.
"""
import io
import pytest
from tUilKit.output.backend.ansi_backend import AnsiRenderBackend
from tUilKit.output.backend.backend import Style
from tUilKit.output.compositor.compositor import Compositor
from tUilKit.output.window.window_manager import WindowManager
from tUilKit.output.widgets.widget import TextWidget, FilledWidget
from tUilKit.output.draw.border import _BORDER_CHARS


# ---------------------------------------------------------------------------
# Mock backend for introspection
# ---------------------------------------------------------------------------

class RecordingBackend:
    """Backend that records every draw_rune call for assertion."""

    def __init__(self):
        self.calls: list[tuple[int, int, str]] = []
        self.flush_count = 0

    def move_cursor(self, x, y): pass

    def draw_rune(self, x, y, ch, style):
        self.calls.append((x, y, ch))

    def draw_string(self, x, y, s, style):
        for i, ch in enumerate(s):
            self.calls.append((x + i, y, ch))

    def flush(self):
        self.flush_count += 1

    def clear_region(self, x, y, w, h): pass

    def cell(self, x, y):
        for cx, cy, ch in reversed(self.calls):
            if cx == x and cy == y:
                return ch
        return None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_compositor(w=40, h=20, backend=None):
    if backend is None:
        backend = RecordingBackend()
    comp = Compositor(backend, width=w, height=h)
    return comp, backend


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestCompositor:
    def test_render_frame_flushes_backend(self):
        comp, back = _make_compositor()
        wm = WindowManager()
        wm.create_window(x=0, y=0, width=10, height=5)
        comp.render_frame(wm.list_windows_in_z_order())
        assert back.flush_count == 1

    def test_border_corners_painted(self):
        comp, back = _make_compositor()
        wm = WindowManager()
        wm.create_window(x=0, y=0, width=10, height=5, border_style="single")
        comp.render_frame(wm.list_windows_in_z_order())
        expected_tl = _BORDER_CHARS["single"]["tl"]
        assert back.cell(0, 0) == expected_tl

    def test_content_widget_rendered_inside_border(self):
        comp, back = _make_compositor()
        wm = WindowManager()
        widget = TextWidget("ABC", Style())
        wm.create_window(x=0, y=0, width=10, height=5, content=widget, border_style="single")
        comp.render_frame(wm.list_windows_in_z_order())
        # Content area starts at (1,1) for a bordered window.
        assert back.cell(1, 1) == "A"
        assert back.cell(2, 1) == "B"
        assert back.cell(3, 1) == "C"

    def test_content_clipped_to_window(self):
        # Window is 5 wide (3 inner), widget text is longer.
        comp, back = _make_compositor()
        wm = WindowManager()
        widget = TextWidget("ABCDEFGH", Style())
        wm.create_window(x=0, y=0, width=5, height=3, content=widget, border_style="single")
        comp.render_frame(wm.list_windows_in_z_order())
        # Inner width = 3, so only A, B, C should be drawn.
        assert back.cell(1, 1) == "A"
        assert back.cell(2, 1) == "B"
        assert back.cell(3, 1) == "C"
        # Column 4 is the border character, not a widget character.
        assert back.cell(4, 1) == _BORDER_CHARS["single"]["v"]
        # Column 5 is outside the window — should not be drawn.
        assert back.cell(5, 1) is None

    def test_z_order_higher_overwrites_lower(self):
        comp, back = _make_compositor(w=20, h=10)
        wm = WindowManager()
        # Both windows overlap at (0,0).
        wid1 = wm.create_window(x=0, y=0, width=5, height=3, z_index=0, border_style="none",
                                 content=FilledWidget("A", Style()))
        wid2 = wm.create_window(x=0, y=0, width=5, height=3, z_index=1, border_style="none",
                                 content=FilledWidget("B", Style()))
        comp.render_frame(wm.list_windows_in_z_order())
        # Higher z-index (wid2) should appear on top.
        assert back.cell(0, 0) == "B"

    def test_second_render_no_diff_no_backend_calls(self):
        comp, back = _make_compositor()
        wm = WindowManager()
        wm.create_window(x=0, y=0, width=5, height=3, border_style="none",
                         content=FilledWidget("X", Style()))
        comp.render_frame(wm.list_windows_in_z_order())
        first_call_count = len(back.calls)
        # Render the identical frame — nothing changed.
        comp.render_frame(wm.list_windows_in_z_order())
        second_call_count = len(back.calls)
        assert second_call_count == first_call_count

    def test_no_border_style_skips_border(self):
        comp, back = _make_compositor()
        wm = WindowManager()
        widget = TextWidget("X", Style())
        wm.create_window(x=0, y=0, width=5, height=3, content=widget, border_style="none")
        comp.render_frame(wm.list_windows_in_z_order())
        # With no border content starts at (0, 0).
        assert back.cell(0, 0) == "X"

    def test_title_drawn_in_border(self):
        comp, back = _make_compositor(w=30, h=5)
        wm = WindowManager()
        wm.create_window(x=0, y=0, width=20, height=5, border_style="single", title="Test")
        comp.render_frame(wm.list_windows_in_z_order())
        top_row = "".join(back.cell(col, 0) or " " for col in range(20))
        assert "Test" in top_row

    def test_resize_clears_buffers(self):
        comp, back = _make_compositor(w=10, h=5)
        comp.resize(20, 10)
        assert comp._width == 20
        assert comp._height == 10
        assert len(comp._back) == 10
        assert len(comp._back[0]) == 20


class TestCompositorAnsiIntegration:
    """Smoke test wiring Compositor to the real AnsiRenderBackend."""

    def test_render_produces_ansi_output(self):
        stream = io.StringIO()
        backend = AnsiRenderBackend(stream=stream)
        comp = Compositor(backend, width=20, height=5)
        wm = WindowManager()
        wm.create_window(x=0, y=0, width=10, height=3, border_style="single")
        comp.render_frame(wm.list_windows_in_z_order())
        out = stream.getvalue()
        # ANSI cursor positioning sequences should be present.
        assert "\033[" in out
