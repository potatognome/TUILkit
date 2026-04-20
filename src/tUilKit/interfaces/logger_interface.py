# Lib/site-packages/tUilKit/interfaces/logger_interface.py
"""
    This module defines the LoggerInterface, which provides an abstract interface for
    logging messages, exceptions, and formatted output with ANSI colour codes.
""" 

from abc import ABC, abstractmethod

class LoggerInterface(ABC):
    @staticmethod
    @abstractmethod
    def split_time_string(time_string: str) -> tuple[str, str]:
        """Split a datetime string into date and time parts."""
        pass

    @abstractmethod
    def log_message(self, message: str, log_files = None, end: str = "\n") -> None:
        pass

    @abstractmethod
    def log_exception(self, description: str, exception: Exception, log_files = None) -> None:
        pass

    @abstractmethod
    def log_done(self, log_files = None, end: str = "\n") -> None:
        pass

    @abstractmethod
    def colour_log(self, *args, spacer=0, log_files=None, end="\n"):
        pass

    @abstractmethod
    def colour_log_text(self, message: str, log_files=None, log_to="both", time_stamp=True):
        pass

    @abstractmethod
    def log_column_list(self, df, filename, log_files=None):
        pass

    @abstractmethod
    def print_rainbow_row(self, pattern="X-O-", spacer=0, log_files=None, end="\n"):
        pass

    @abstractmethod
    def print_top_border(self, pattern, length, index=0, log_files=None, border_colour='RESET'):
        pass

    @abstractmethod
    def print_text_line(self, text, pattern, length, index=0, log_files=None, border_colour='RESET', text_colour='RESET'):
        pass

    @abstractmethod
    def print_bottom_border(self, pattern, length, index=0, log_files=None, border_colour='RESET'):
        pass

    @abstractmethod
    def apply_border(self, text, pattern, total_length=None, index=0, log_files=None, border_colour='RESET', text_colour='RESET'):
        pass

    @abstractmethod
    def flush_log_queue(self, log_file: str) -> None:
        """Flush any queued log messages to the specified log file."""
        pass
