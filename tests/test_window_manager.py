"""
Tests for WindowManager.
"""
import pytest
from tUilKit.output.window.window_manager import WindowManager


class TestWindowManager:
    def setup_method(self):
        self.wm = WindowManager()

    def test_create_returns_id(self):
        wid = self.wm.create_window()
        assert isinstance(wid, str) and len(wid) > 0

    def test_create_stores_window(self):
        wid = self.wm.create_window(x=1, y=2, width=40, height=20)
        win = self.wm.get_window(wid)
        assert win is not None
        assert win.x == 1
        assert win.y == 2
        assert win.width == 40
        assert win.height == 20

    def test_window_count(self):
        self.wm.create_window()
        self.wm.create_window()
        assert self.wm.window_count == 2

    def test_close_window_removes_it(self):
        wid = self.wm.create_window()
        self.wm.close_window(wid)
        assert self.wm.get_window(wid) is None
        assert self.wm.window_count == 0

    def test_close_nonexistent_is_noop(self):
        self.wm.close_window("ghost")  # must not raise

    def test_move_window(self):
        wid = self.wm.create_window(x=0, y=0)
        self.wm.move_window(wid, 10, 15)
        win = self.wm.get_window(wid)
        assert win.x == 10
        assert win.y == 15

    def test_resize_window(self):
        wid = self.wm.create_window(width=80, height=24)
        self.wm.resize_window(wid, 100, 30)
        win = self.wm.get_window(wid)
        assert win.width == 100
        assert win.height == 30

    def test_focus_window(self):
        wid = self.wm.create_window(focusable=True)
        self.wm.focus_window(wid)
        assert self.wm.focused_id == wid
        assert self.wm.get_window(wid).focused

    def test_focus_unfocuses_previous(self):
        w1 = self.wm.create_window(focusable=True)
        w2 = self.wm.create_window(focusable=True)
        self.wm.focus_window(w1)
        self.wm.focus_window(w2)
        assert not self.wm.get_window(w1).focused
        assert self.wm.get_window(w2).focused

    def test_focus_non_focusable_ignored(self):
        wid = self.wm.create_window(focusable=False)
        self.wm.focus_window(wid)
        assert self.wm.focused_id is None

    def test_list_windows_in_z_order(self):
        w1 = self.wm.create_window(z_index=5)
        w2 = self.wm.create_window(z_index=1)
        w3 = self.wm.create_window(z_index=3)
        order = self.wm.list_windows_in_z_order()
        z_values = [w.z_index for w in order]
        assert z_values == sorted(z_values)

    def test_raise_window(self):
        w1 = self.wm.create_window(z_index=0)
        w2 = self.wm.create_window(z_index=1)
        self.wm.raise_window(w1)
        order = self.wm.list_windows_in_z_order()
        assert order[-1].id == w1

    def test_lower_window(self):
        w1 = self.wm.create_window(z_index=0)
        w2 = self.wm.create_window(z_index=1)
        self.wm.lower_window(w2)
        order = self.wm.list_windows_in_z_order()
        assert order[0].id == w2

    def test_set_z_index(self):
        wid = self.wm.create_window(z_index=0)
        self.wm.set_z_index(wid, 42)
        assert self.wm.get_window(wid).z_index == 42

    def test_focus_raises_window_to_top(self):
        w1 = self.wm.create_window(z_index=0)
        w2 = self.wm.create_window(z_index=10)
        self.wm.focus_window(w1)
        order = self.wm.list_windows_in_z_order()
        assert order[-1].id == w1

    def test_close_focused_clears_focus(self):
        wid = self.wm.create_window()
        self.wm.focus_window(wid)
        self.wm.close_window(wid)
        assert self.wm.focused_id is None
