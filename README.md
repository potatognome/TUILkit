tUilKit

# Project Name
tUilKit

**Current version: 0.5.0**

## Recent Enhancements (v0.5.0)

- **Root Mode Coverage**: Added focused tests validating `project` vs `workspace` config root mode resolution.
- **Shared Config Coverage**: Added tests ensuring shared config lookup follows `ROOTS`, `ROOT_MODES`, `PATHS`, and `SHARED_CONFIG`.
- **Test Bootstrap Reliability**: Existing tests now bootstrap local `src` imports so direct script runs from `tests/` work reliably.
- **Config Test Alignment**: Updated shared config expectations to match current `config/GLOBAL_SHARED.d` contents.


tUilKit (formerly utilsbase) is a modular Python toolkit providing utility functions, dictionaries, and configuration for development projects.  
The package is structured around clear **interfaces** for logging, colour management, file system operations, and configuration loading, making it easy to extend or swap implementations.  
tUilKit is organized into three main components:
- **/config**: JSON files for customization and configuration
- **/dict**: Python dictionaries and constants (e.g., ANSI codes, RGB values)
- **/utils**: Toolkit modules implementing the interfaces

## Folder Structure 


```
    /config
        tuIlKit_CONFIG.json             # Folder paths and logging/display options
        /GLOBAL_SHARED.d                # Shared project level config
            BORDER_PATTERNS.json        # Border Patterns
            COLOURS.json                # Foreground text COLOUR_KEY and RGB Reference
    /src
        /config                         # Default global config files (deployed by H3l3n)
            BORDER_PATTERNS.json        # Border Patterns
            COLOURS.json                # Foreground text COLOUR_KEY and RGB Reference
            COLUMN_MAPPING.json         # DataFrame column mapping
        /dict
            DICT_CODES.py               # ANSI escape code parts for sequencing
            DICT_COLOURS.py             # RGB ANSI escape codes for sequencing
        /interfaces
            colour_interface.py         # ColourInterface (abstract base class)
            config_loader_interface.py  # ConfigLoaderInterface (abstract base class)
            df_interface.py             # DataFrameInterface (abstract base class)
            file_system_interface.py    # FileSystemInterface (abstract base class)
            logger_interface.py         # LoggerInterface (abstract base class)
        /utils
            config.py                   # ConfigLoader implementation
            fs.py                       # Core - File system operations (FileSystem)
            output.py                   # Core - Printing/Debugging/Logging (Logger, ColourManager)
            sheets.py                   # Primary - CSV/XLSX utilities
            formatter.py                # Primary Extension - formatting utilities (early development)
            pdf.py                      # Add-on - PDF file utilities (early development)
            sql.py                      # Add-on - SQL query utilities (planned)
            calc.py                     # Add-on - Specialized calculations
            wallet.py                   # Add-on - Specialized crypto wallet utilities
            data.py                     # Add-on - Specialized data utilities
    /docs
        tUilKit_Comprehensive_Usage_Guide.md  # Complete usage documentation
        ColourKey_Usage_Guide.md              # Colour key addendum
        FileSystem_Usage_Guide.md             # File system addendum
    /tests
        /config
            /GLOBAL_SHARED.d
                COLOURS.json          # Isolated test config for colour keys
        test_config.py                # ConfigLoader + config paths
        test_config_minimal.py        # Minimal ConfigLoader test
        test_output.py                # Output/logging functions
        test_fs_ops.py                # File system operations
        test_multi_category.py        # Multi-category logging
        test_interfaces.py            # Interface compliance
        test_sheets.py                # DataFrame utilities
```

## Interfaces

tUilKit uses Python abstract base classes to define clear interfaces for:

**4 Primary Interfaces:**
- **LoggerInterface**: Logging, coloured output, and border printing with selective file routing
- **ColourInterface**: Colour formatting and ANSI code management  
- **FileSystemInterface**: File and folder operations with integrated logging
- **ConfigLoaderInterface**: Configuration loading and path resolution

**Additional Interface:**
- **DataFrameInterface**: Data frame operations and intelligent column handling

All implementations in `/utils` and `/config` inherit from these interfaces, ensuring modularity and testability.

## Installation
Follow these instructions to install and set up the project:

```bash
# Navigate to the project directory
cd tUilKit

# (Optional) Create and activate a virtual environment
# python -m venv venv
# source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt
```

## Usage

For comprehensive usage instructions, see [`docs/tUilKit_Comprehensive_Usage_Guide.md`](docs/tUilKit_Comprehensive_Usage_Guide.md). For colour codes and filesystem patterns, see [`docs/ColourKey_Usage_Guide.md`](docs/ColourKey_Usage_Guide.md) and [`docs/FileSystem_Usage_Guide.md`](docs/FileSystem_Usage_Guide.md).

### Quick Start

#### Using Factory Functions (Recommended)

```python
from tUilKit import get_logger, get_file_system, get_config_loader

# Initialize all components with a single call per component
logger = get_logger()
fs = get_file_system()
config = get_config_loader()

# Basic logging with colours
logger.colour_log("!info", "tUilKit initialized", "!done", "ready")

# Multi-category logging
logger.colour_log("!info", "Complex operation", category=["fs", "error"])
```

#### Direct Initialization (Advanced)

```python
from tUilKit.utils.output import Logger, ColourManager
from tUilKit.utils.fs import FileSystem
from tUilKit.config.config import ConfigLoader

# Initialize core components manually
config_loader = ConfigLoader()
colour_config = config_loader.load_colour_config()
colour_manager = ColourManager(colour_config)
logger = Logger(colour_manager, log_files=config_loader.global_config.get("LOG_FILES", {}))
file_system = FileSystem(logger, log_files=config_loader.global_config.get("LOG_FILES", {}))
```

### Key Features

- **4 Primary Interfaces**: Logger, ColourManager, FileSystem, ConfigLoader
- **Multi-Category Logging**: Log to multiple files simultaneously
- **Colour-Coded Output**: Consistent terminal formatting with COLOUR_KEY
- **DataFrame Utilities**: Smart merging and column mapping
- **Configuration-Driven**: JSON-based customization

Sample usage and tests can be found in the `/tests` folder.

## Contributing
If you would like to contribute, please fork the repository and use a feature branch. Pull requests are warmly welcome.

We’re actively seeking contributors to help enhance tUilKit! Whether you’re passionate about terminal functionality, advanced data operations, or document creation, there’s plenty of room to leave your mark.

### Areas for Contribution

- **Enhanced ANSI Sequences**:  
    - Fetching user keystrokes, moving cursor, background colours, advanced terminal features.
- **DataFrame / Spreadsheet Functionality**:  
    - Smart diff, smart merging, custom autoformatting and updates to the DataFrameInterface and sheets utilities.
- **LaTeX and PDF Functionality**:  
    - Reading/writing LaTeX, PDF file manipulation (generation, formatting, searching, editing).

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements
- Thanks to everyone who contributed to this project.

