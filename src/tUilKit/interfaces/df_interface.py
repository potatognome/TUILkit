# Lib/site-packages/tUilKit/interfaces/df_interface.py
"""
    This module defines the DataFrameInterface, which provides an abstract interface for
    intelligent dataframe handling, including merging and comparing dataframes.
"""
from abc import ABC, abstractmethod 
import pandas as pd

class DataFrameInterface(ABC):
    """Abstract interface for intelligent dataframe handling."""

    @abstractmethod
    def merge(self, df_list, merge_type="outer", config_loader=None):
        """Merges multiple dataframes intelligently."""
        pass

    @abstractmethod
    def compare(self, df1, df2):
        """Compares two dataframes while handling inconsistencies."""
        pass
