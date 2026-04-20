"""
chroma.py - ANSI colour and style utilities for tUilKit terminal output.
Pure functions, namespace-style class. No side effects.
"""
import os
import sys
import platform
from tUilKit.dict.ansi_colours import FG_COLOURS, BG_COLOURS, STYLES

class Chroma:
    @staticmethod
    def supports_ansi():
        force = os.environ.get("TUILKIT_FORCE_ANSI")
        if force is not None:
            return force.lower() in ("1", "true", "yes", "on")
        if not sys.stdout.isatty():
            return False
        if sys.platform == "win32":
            ver = platform.version().split(".")
            try:
                return int(ver[0]) >= 10
            except Exception:
                return False
        return True

    @staticmethod
    def fgset(fore_colour):
        if not Chroma.supports_ansi():
            return ""
        return FG_COLOURS.get(fore_colour, "")

    @staticmethod
    def bgset(back_colour):
        if not Chroma.supports_ansi():
            return ""
        return BG_COLOURS.get(back_colour, "")

    @staticmethod
    def bold(text):
        return Chroma.apply(text, STYLES["bold"])

    @staticmethod
    def dim(text):
        return Chroma.apply(text, STYLES["dim"])

    @staticmethod
    def rainbowtext(text):
        if not Chroma.supports_ansi():
            return text
        rainbow = ["red", "yellow", "green", "cyan", "blue", "magenta"]
        out = []
        for i, c in enumerate(text):
            colour = FG_COLOURS.get(rainbow[i % len(rainbow)], "")
            out.append(f"{colour}{c}")
        return "".join(out) + STYLES["reset"]

    @staticmethod
    def apply(text, *styles):
        if not Chroma.supports_ansi() or not styles:
            return text
        codes = "".join(styles)
        return f"{codes}{text}{STYLES['reset']}"
