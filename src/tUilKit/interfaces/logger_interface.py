"""
This module defines the LoggerInterface, which provides an abstract interface for
logging messages, exceptions, and formatted output with ANSI colour codes.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, Optional

class LoggerInterface(ABC):
    @staticmethod
    @abstractmethod
    def split_time_string(time_string: str) -> tuple[str, str]:
        """Split a datetime string into date and time parts."""
        pass

    @abstractmethod
    def log_message(
        self,
        message: str,
        log_files=None,
        end: str = "\n",
        log_to: str = "both",
        time_stamp: bool = True,
        dual_log: "bool | None" = None,
        entry: Optional[Any] = None,
    ) -> None:
        pass

    @abstractmethod
    def log_exception(
        self,
        description: str,
        exception: Exception,
        category: str = "error",
        log_files=None,
        log_to: str = "both",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        pass

    @staticmethod
    @abstractmethod
    def normalize_metadata(metadata=None, **overrides):
        pass

    @abstractmethod
    def create_log_entry(
        self,
        message,
        *,
        category="default",
        severity=None,
        verbosity=None,
        metadata=None,
        app_id=None,
        component="logger",
        module="",
        session_id=None,
        correlation_id=None,
        source_layer="tuilkit",
        target="terminal",
        file_path="",
        output_targets: Optional[Iterable[str]] = None,
        palette_key="",
        palette_version="unknown",
        parent_event_id="",
    ):
        pass

    @abstractmethod
    def log_done(
        self,
        log_files=None,
        end: str = "\n",
        log_to: str = "both",
        time_stamp: bool = True,
    ) -> None:
        pass

    @abstractmethod
    def colour_log(
        self,
        *args,
        category="default",
        spacer=0,
        log_files=None,
        end="\n",
        log_to="both",
        time_stamp=True,
        metadata=None,
        severity=None,
        verbosity=None,
    ):
        pass

    @abstractmethod
    def colour_log_text(self, message: str, log_files=None, log_to="both", time_stamp=True):
        pass

    @abstractmethod
    def log_column_list(self, df, filename, log_files=None, log_to: str = "both"):
        pass

    @abstractmethod
    def print_rainbow_row(self, pattern="X-O-", spacer=0, log_files=None, end="\n", log_to="both"):
        pass

    @abstractmethod
    def print_top_border(
        self,
        pattern,
        length,
        index=0,
        log_files=None,
        border_colour='!proc',
        border_fg_gradient=None,
        border_bg_gradient=None,
        border_rainbow=False,
        log_to: str = "both",
    ):
        pass

    @abstractmethod
    def print_text_line(
        self,
        text,
        pattern,
        length,
        index=0,
        log_files=None,
        border_colour='!proc',
        text_colour='!proc',
        border_fg_gradient=None,
        border_bg_gradient=None,
        border_rainbow=False,
        text_fg_gradient=None,
        text_bg_gradient=None,
        text_rainbow=False,
        justify='left',
        log_to: str = "both",
    ):
        pass

    @abstractmethod
    def print_bottom_border(
        self,
        pattern,
        length,
        index=0,
        log_files=None,
        border_colour='!proc',
        border_fg_gradient=None,
        border_bg_gradient=None,
        border_rainbow=False,
        log_to: str = "both",
    ):
        pass

    @abstractmethod
    def apply_border(
        self,
        text,
        pattern,
        total_length=None,
        index=0,
        log_files=None,
        border_colour='!proc',
        text_colour='!proc',
        border_fg_gradient=None,
        border_bg_gradient=None,
        border_rainbow=False,
        text_fg_gradient=None,
        text_bg_gradient=None,
        text_rainbow=False,
        justify='left',
        log_to: str = "both",
    ):
        pass

    @abstractmethod
    def flush_log_queue(self, log_file: str) -> None:
        """Flush any queued log messages to the specified log file."""
        pass
