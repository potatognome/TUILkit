# Lib/site-packages/tUilKit/utils/formatter.py
"""
    This module provides utilities for formatting dataframes, including applying column widths
    and padding to ensure consistent display in terminal applications.
"""
import json

def load_column_widths():
    """Loads predefined column widths from JSON configuration."""
    config_loader = ConfigLoader()
    config_path = config_loader.get_config_file_path("COLUMN_MAPPING")
    with open(config_path, "r") as file:
        return json.load(file)

def apply_column_format(df):
    """Applies width and formatting rules to dataframe columns."""
    column_widths = load_column_widths()
    for col in df.columns:
        if col in column_widths:
            df[col] = df[col].apply(lambda x: str(x).ljust(column_widths[col]))  # Apply width padding
    return df  