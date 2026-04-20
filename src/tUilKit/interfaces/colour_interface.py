# Lib/site-packages/tUilKit/interfaces/colour_interface.py
"""
    This module defines the ColourInterface, which provides an abstract interface for 
    colour management and ANSI escape code handling.
"""

from abc import ABC, abstractmethod

class ColourInterface(ABC):
    @abstractmethod
    def get_fg_colour(self, colour_code: str) -> str:
        pass

    @abstractmethod
    def get_bg_colour(self, colour_code: str) -> str:
        pass

    @abstractmethod
    def strip_ansi(self, fstring: str) -> str:
        pass

    @abstractmethod
    def colour_fstr(self, *args, bg=None) -> str:
        pass

    @abstractmethod
    def colour_path(self, path: str) -> str:
        pass

    @abstractmethod
    def interpret_codes(self, text: str) -> str:
        pass
