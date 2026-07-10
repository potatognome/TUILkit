"""Compatibility shims for legacy inline menu helpers.

Provide `show_numbered_menu`, `show_menu_with_preview`, and `_print_options`
wrappers that delegate to the canonical `CLIMenuHandler` obtained via
`tUilKit.get_cli_menu_handler()`.

This allows incremental replacement of inline menu implementations by
importing these shims and delegating behaviour without a large bulk change.
"""
from typing import Any, Callable, Iterable, List, Optional

from tUilKit.factories import get_cli_menu_handler


def show_numbered_menu(title: str, options: Iterable[str], default: Optional[int] = None) -> Any:
    handler = get_cli_menu_handler()
    # CLIMenuHandler.show_numbered_menu semantics vary; attempt to call
    try:
        return handler.show_numbered_menu(title, list(options), default)
    except TypeError:
        # fallback to older signature
        return handler.show_numbered_menu(title, list(options))


def show_menu_with_preview(title: str, items: Iterable[dict], preview_fn: Callable[[dict], str]) -> Any:
    handler = get_cli_menu_handler()
    return handler.show_menu_with_preview(title, list(items), preview_fn)


def _print_options(items: Iterable[str]) -> None:
    handler = get_cli_menu_handler()
    # Many legacy callers expect a simple print; delegate to handler to render consistently.
    try:
        handler.print_options(list(items))
    except Exception:
        # best-effort fallback
        for i, it in enumerate(items, start=1):
            print(f"{i}. {it}")


def display_header(title: str, *, is_main_menu: bool = False, ctx: Optional[object] = None) -> None:
    """Display a simple header using the CLIMenuHandler when available.

    This provides a compatible, minimal header for modules that previously
    had tiny `_display_header` implementations.
    """
    handler = None
    try:
        handler = get_cli_menu_handler()
    except Exception:
        handler = None

    if handler is not None:
        try:
            # Some handlers may support a display_header method.
            if hasattr(handler, "display_header"):
                handler.display_header(title, is_main_menu=is_main_menu)
                return
        except Exception:
            pass

    # Fallback plain-text header
    print("\n" + title)
    print("=" * len(title))


def prompt(text: str = "> ") -> str:
    """Prompt for input using handler prompt when possible, otherwise `input()`."""
    try:
        handler = get_cli_menu_handler()
        if hasattr(handler, "prompt"):
            return handler.prompt(text)
    except Exception:
        pass
    try:
        return input(text).strip()
    except (EOFError, KeyboardInterrupt):
        return ""


def pause(message: str = "Press Enter to continue...") -> None:
    """Pause helper; best-effort implementation."""
    try:
        handler = get_cli_menu_handler()
        if hasattr(handler, "pause"):
            handler.pause(message)
            return
    except Exception:
        pass
    try:
        input(message)
    except Exception:
        pass


def set_logger(logger) -> None:
    """Set logger on the handler if available; no-op otherwise."""
    try:
        handler = get_cli_menu_handler()
        if handler is not None and hasattr(handler, "set_logger"):
            handler.set_logger(logger)
    except Exception:
        pass
