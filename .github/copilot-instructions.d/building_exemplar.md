# Building Exemplar Policy

## Purpose

The `examples/` folder contains **supplementary test scripts that operate outside of pytest**.
These scripts serve a different purpose from pytest unit tests:

- **Exercise all public functions** with all reasonable input scenarios.
- **Deliberately attempt to break UI menus** and edge-case error paths (empty input,
  out-of-range values, special characters, very long strings).
- Provide visual, interactive, **colour-logged output** for human review alongside structured
  log files.
- Serve as **living documentation** of how each module behaves under normal and adversarial
  conditions.

In addition to these supplementary tests, the `examples/` folder should always contain a file called
`exemplar.py`.  The purpose of this file is to serve as a mock entry point for the applications operation.

The `exemplar.py` application should:
    - Load tUilKit factory imports in verbose mode where available (e.g. ConfigLoader)
    - Generate a standard CLI menu, including project name header and submenus  
    - Read projects primary config file
    - read and test load all ROOT_MODES
    - verify and display paths for LOG_FILES, CONFIG files and input data files
