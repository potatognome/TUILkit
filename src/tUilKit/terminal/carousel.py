"""Reusable terminal carousel selection widget with keyboard fallback."""

from __future__ import annotations

import sys
from typing import Callable, List, Optional

from tUilKit.terminal.canvas import Canvas
from tUilKit.terminal.cursor import Cursor

try:
    import msvcrt  # type: ignore

    HAS_MSVCRT = True
except ImportError:
    HAS_MSVCRT = False


class CarouselSelector:
    """Select one item from a list using arrow keys or numbered fallback."""

    def __init__(
        self,
        items: List[str],
        title: str,
        *,
        help_text: str = "Left/Right=move  Enter=select  Esc=back",
        line_factory: Optional[Callable[[int, str, bool], str]] = None,
        footer_factory: Optional[Callable[[int, str], List[str]]] = None,
    ) -> None:
        self._items = items
        self._title = title
        self._help_text = help_text
        self._line_factory = line_factory
        self._footer_factory = footer_factory

    def select(self) -> Optional[str]:
        """Run the selector and return the chosen item or None if cancelled."""
        if not self._items:
            return None

        if not HAS_MSVCRT or len(self._items) == 1:
            return self._select_numbered()

        return self._select_with_arrows()

    def _select_numbered(self) -> Optional[str]:
        print()
        print(self._title)
        for idx, item in enumerate(self._items, start=1):
            print(f"  {idx}. {item}")

        try:
            raw = input(f"\nSelect option (1-{len(self._items)}), or Enter to cancel: ").strip()
        except (KeyboardInterrupt, EOFError):
            return None

        if not raw:
            return None

        try:
            selected_index = int(raw) - 1
        except ValueError:
            return None

        if 0 <= selected_index < len(self._items):
            return self._items[selected_index]
        return None

    def _select_with_arrows(self) -> Optional[str]:
        canvas = Canvas()
        cursor = 0

        def _build_frame() -> List[str]:
            lines: List[str] = [self._title, self._help_text, ""]
            for idx, item in enumerate(self._items):
                if self._line_factory:
                    lines.append(self._line_factory(idx, item, idx == cursor))
                    continue
                marker = "◉" if idx == cursor else "○"
                pointer = ">" if idx == cursor else " "
                lines.append(f"{pointer} {marker}  {item}")

            if self._footer_factory:
                lines.extend([""] + self._footer_factory(cursor, self._items[cursor]))
            return lines

        try:
            sys.stdout.write(Cursor.hide())
            sys.stdout.flush()
            sys.stdout.write(canvas.draw(_build_frame()))
            sys.stdout.flush()

            while True:
                key = msvcrt.getch()
                if key in (b"\xe0", b"\x00"):
                    key2 = msvcrt.getch()
                    if key2 in (b"K", b"H"):
                        cursor = (cursor - 1) % len(self._items)
                    elif key2 in (b"M", b"P"):
                        cursor = (cursor + 1) % len(self._items)
                elif key == b"\r":
                    return self._items[cursor]
                elif key in (b"\x1b", b"q", b"Q"):
                    return None

                sys.stdout.write(canvas.redraw(_build_frame()))
                sys.stdout.flush()
        finally:
            sys.stdout.write(Cursor.show())
            sys.stdout.flush()
            print()
