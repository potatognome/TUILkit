# COLOUR_KEY_HELP #
This section appears atop the COLOURS.json file in the config folder.

##
"COLOUR_KEY_HELP"   : {
    "!date"          : "For the DATE portion of datetime strings",
    "!time"          : "For the TIME portion of datetime strings",

    "!args"          : "For runtime arguments or parameters that are specified during runtime",
    "!cmd"           : "OS or batch execution of command line or terminal commands (e.g. copying files) -- ALONGSIDE <!done>",
    "!proc"          : "Internal process execution (e.g. procedure or function calls) -- ALONGSIDE <!done>",
    "!try"           : "For try blocks or test attempts",
    "!test"          : "For test cases",
    
    "!done"          : "!cmd/!proc execution completed successfully",
    "!pass"          : "For passed tests or matching comparisons used in assertions",
    "!warn"          : "For warnings",
    "!fail"          : "For failed operations",
    "!error"         : "For error handling, runtime warnings",

    "!output"        : "For miscellaneous variable output not better served by other keys [For numerical calculations: use !calc]",
    "!expect"        : "For expected values in comparisons",
    "!actual"        : "For actual values in comparisons",

    "!calc"          : "For output determined by a runtime calculation",
    "!data"          : "For data read from an input file or data frame",
    "!list"          : "For list data",
    "!int"           : "For integer values typically not part of a calculation [In those cases: use !calc]",
    "!float"         : "For float values typically not part of a calculation [In those cases: use !calc]",
    "!text"          : "For text strings",

    "!drive"         : "For drive letters in file paths",
    "!basefolder"    : "For base folder in file paths",
    "!midfolder"     : "For middle folders in file paths",
    "!thisfolder"    : "For current folder in file paths",
    "!path"          : "For file system folder paths not including base filename",
    "!file"          : "For file system filenames",
    "!file_ext"      : "For file system filename extensions",

    "!load"          : "For indicating that a file has been loaded -- ALONGSIDE <!path?><!file>",
    "!save"          : "For indicating that a file has been saved -- ALONGSIDE <!path?><!file>",
    "!create"        : "For creation operations",
    "!delete"        : "For deletion operations",

    "!info"          : "For general text output",
    "!reset"         : "Used automatically after colour_str and colour_log to reset terminal foreground and background text colour to defaults",

## COLOUR_KEY (FOREGROUND | BACKGROUND)
Specific colours are imported from the RGB dictionary in the /dict folder

"COLOUR_KEY"        : {
    "!date"         : "CORNFLOWER|BLACK",
    "!time"         : "LIME|BLACK",

    "!args"         : "YELLOW|BLACK",
    "!cmd"          : "CORAL|BLACK",
    "!proc"         : "CORAL|BLACK",
    "!try"          : "CYAN|BLACK",
    "!test"         : "CYAN|BLACK",

    "!done"         : "GREEN|BLACK",
    "!pass"         : "GOLD|BLACK",
    "!warn"         : "BLACK|ORANGE",
    "!fail"         : "RUST|BLACK",
    "!error"        : "RED|BLACK",

    "!output"       : "GREEN|BLACK",
    "!expected"     : "SKY BLUE|BLACK",
    "!actual"       : "MANGO|BLACK",

    "!int"          : "TURQUOISE|BLACK",
    "!float"        : "GREEN|BLACK",
    "!text"         : "CRIMSON|BLACK",
    "!calc"         : "BLUE|BLACK",
    "!data"         : "BLUE|BLACK",
    "!list"         : "VIOLET|BLACK",

    "!drive"        : "MAGENTA|BLACK",
    "!path"         : "LAVENDER|BLACK",
    "!basefolder"   : "LAVENDER|BLACK",
    "!midfolder"    : "BURGUNDY|BLACK",
    "!thisfolder"   : "LAVENDER|BLACK",
    "!file"         : "ROSE|BLACK",
    "!file_ext"     : "PEACH|BLACK",

    "!load"         : "PINK|BLACK",
    "!save"         : "PINK|BLACK",
    "!create"       : "MINT|BLACK",
    "!delete"       : "DARK ORANGE|BLACK",

    "!info"         : "LIGHT GREY|BLACK",
    "!reset"        : "LIGHT GREY|BLACK",

