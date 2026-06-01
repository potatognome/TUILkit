"""
Tests for ZOrderManager.
"""
import pytest
from tUilKit.output.window.window import Window
from tUilKit.output.zorder.zorder import ZOrderManager


def _win(z: int, wid: str = None) -> Window:
    import uuid
    return Window(id=wid or str(uuid.uuid4()), z_index=z)


class TestZOrderManager:
    def test_add_single(self):
        zm = ZOrderManager()
        w = _win(0)
        zm.add(w)
        assert zm.list_in_z_order() == [w]

    def test_add_multiple_sorted(self):
        zm = ZOrderManager()
        w1 = _win(5)
        w2 = _win(1)
        w3 = _win(3)
        zm.add(w1)
        zm.add(w2)
        zm.add(w3)
        ids = [w.z_index for w in zm.list_in_z_order()]
        assert ids == sorted(ids)

    def test_remove(self):
        zm = ZOrderManager()
        w = _win(0, wid="abc")
        zm.add(w)
        zm.remove("abc")
        assert zm.list_in_z_order() == []

    def test_remove_nonexistent_is_noop(self):
        zm = ZOrderManager()
        zm.remove("ghost")  # must not raise

    def test_raise_window(self):
        zm = ZOrderManager()
        w1 = _win(0, "a")
        w2 = _win(1, "b")
        zm.add(w1)
        zm.add(w2)
        zm.raise_window("a")
        order = zm.list_in_z_order()
        assert order[-1].id == "a"

    def test_lower_window(self):
        zm = ZOrderManager()
        w1 = _win(0, "a")
        w2 = _win(1, "b")
        zm.add(w1)
        zm.add(w2)
        zm.lower_window("b")
        order = zm.list_in_z_order()
        assert order[0].id == "b"

    def test_set_z_index(self):
        zm = ZOrderManager()
        w = _win(0, "x")
        zm.add(w)
        zm.set_z_index("x", 99)
        assert w.z_index == 99

    def test_get_existing(self):
        zm = ZOrderManager()
        w = _win(0, "myid")
        zm.add(w)
        assert zm.get("myid") is w

    def test_get_missing_returns_none(self):
        zm = ZOrderManager()
        assert zm.get("nope") is None

    def test_list_returns_copy(self):
        zm = ZOrderManager()
        w = _win(0)
        zm.add(w)
        lst = zm.list_in_z_order()
        lst.pop()
        # original list should be unaffected
        assert len(zm.list_in_z_order()) == 1
