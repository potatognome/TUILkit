# Lib/site-packages/tUilKit/dict/DICT_CODES.py
"""
    This module defines dictionaries for ANSI escape codes and cursor movement commands.
    It includes escape codes for formatting text, moving the cursor, and colour commands.
""" 
# Set up ANSI Escape codes dictionary for formatting text
ESCAPES = {
    'CTRL'      : '^[',
    'OCTAL'     : '\033[',
    'UNICODE'   : '\u001b[',
    'HEX'       : '\0x1B[',
    'DEC'       : '27['
}
# Set up ANSI codes dictionary for moving cursor
# Will fill out more of these codes as needed
CURSOR = {
    'HOME'      : 'Hm',
    'UP'        : '1Am',
    'DOWN'      : '1Bm',
    'LEFT'      : '1Cm',
    'RIGHT'     : '1Dm'
}
COMMANDS = {
    'RESET'     : '0m',
    'FGC'       : '38;2;',
    'BGC'       : '48;2;'
}

