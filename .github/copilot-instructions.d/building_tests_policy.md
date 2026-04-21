# Building Tests Policy (modular)

Purpose
- Standardized template and guidelines for creating test files in the `tests/` folders across projects.
- Ensures consistency, readability, and proper logging/coloring in test suites.
- Tests should follow a structured workflow to facilitate debugging, logging, and user experience.

Key Guidelines
- **Include test_paths.json for absolute paths**: Every tests folder must contain a `test_paths.json` file with absolute paths for:
   - tests folder
   - config folder
   - tUilKit src folder
   - test logs folder
This file should be generated at test setup and read by all test scripts for robust path resolution and environment independence.
2.6. **Test Paths JSON Resolution**
   - Always read `test_paths.json` from the tests folder at the start of each test script.
   - All tUilKit test suites must use `test_config.py` as the primary config loader and reference for test configuration and paths.
   - Use the absolute paths from `test_config.py` (via `test_paths.json`) to resolve imports, config, and log locations.
   - Prefer these paths over dynamic os/cwd resolution for consistency.
- **Clear screen on terminal at start**: Use terminal commands to clear the screen before running tests for a clean output.
- **Print rainbow row**: Immediately after clearing, display a rainbow row using `print_rainbow_row` to visually separate test runs.
- **Display last command**: Show the last terminal command including prompt, virtual environment name (if applicable), and full command with arguments. Example: `(base) PS C:\Repository\Daniel\dev_local\Projects\tUilKit> python .\tests\test_sheets.py`
- **Use print_rainbow_row between sections**: Separate major sections (e.g., between tests) with rainbow rows for visual clarity.
- **Use apply_border for header titles**: Wrap section headers or test titles with `apply_border` for emphasis.
- **Add time delays**: Include `time.sleep()` between tests, before assertions, or key operations to allow for visual inspection and prevent overwhelming output.
- **Utilize logging functions extensively**: Use `colour_log`, `log_exception`, `log_done`, and `colour_path` for all output. Avoid plain `print` statements.
- **Include sections and headers**: Structure test code with clear sections following the preferred workflow.
- **Segregated Log files**: All test files must use the test logs folder specified in `TESTS_OPTIONS` from `tUilKit_CONFIG.json`, loaded via `test_config.py`. Use centralized workspace level `.testlogs` folder or project-level folder as defined in config. Always load `TESTS_OPTIONS` via the config loader in `test_config.py` and resolve log paths accordingly.

Preferred Workflow Sections
2.5. **Test Log Folder Resolution**
   - Use the `TEST_LOGS_FOLDER` value from `GLOBAL_SHARED.d\TESTS_OPTIONS.json` to resolve all test log file paths.
   - Ensure all loggers and test output files are written to this folder.
1. **Command Line Args**
   - Parse arguments like `--clean` with options: "local" (delete logs for this test), "all" (delete all logs in folder), "master" (delete main log only), "tests" (delete test-specific logs only).
   - Use `argparse` for parsing.

2. **Imports and Initialization**
   - Import necessary modules, classes, and functions.
   - Initialize loggers, config loaders, and other shared objects.
   - Load test data from `tests/testInputData` if needed.

3. **Test Variables**
   - Define variables for test inputs, expected outputs, and sample data.
   - Typically import or generate data here.

4. **Test Functions**
   - Each test function should accept an optional `function_log` argument to log results separately.
   - Use assertions or checks with colored logging for pass/fail.
   - Make use of COLOUR_KEY_HELP and/or COLOUR_KEY guidance in copilot-instructions.d
   - Log inputs, expected vs. actual values, and outcomes.

5. **Tests Tuple**
   - Define a `TESTS` tuple or list with entries like `(test_number, "test_name", test_function)`.
   - Similar to `test_output.py`.

6. **Test Runner**
   - Iterate through `TESTS`.
   - For each test: print rainbow row, apply border around test info, 
   - Display log messages using colour_log with Test Functions: log what the test does, inputs/outputs where appropriate, expected vs. actual. where appropriate
   - Handle exceptions with `log_exception`.

7. **Test Summary**
   - Summarize successful vs. unsuccessful tests.
   - Color-code results: using COLOUR_KEY_HELP and/or COLOUR_KEY guidance.
   - Detail any errors or failures.

Example Structure (Pseudocode)
# Example: Reading test_paths.json
import json
with open(os.path.join(os.path.dirname(__file__), "test_paths.json"), "r") as f:
   paths = json.load(f)
tests_folder = paths["tests_folder"]
config_folder = paths["config_folder"]
tUilKit_src_folder = paths["tUilKit_src_folder"]
test_logs_folder = paths["test_logs_folder"]
```python
# 1. Command Line Args
parser = argparse.ArgumentParser()
parser.add_argument('--clean', choices=['local', 'all', 'master', 'tests'], default='local')
args, _ = parser.parse_known_args()

# 2. Imports and Initialization
from tUilKit.utils.output import Logger, ColourManager
# ... initialize logger, etc.

# 3. Test Variables
test_data = load_from_testInputData()

# 4. Test Functions
def test_example(function_log=None):
    # Log inputs, perform test, log results
    logger.colour_log ("!info","This test function","!test", test_example, "!info", " provides a description of what our test does.", log_files=[TEST_LOG_FILE, function_log])
    
    # Test interpret_codes
    interpreted = colour_manager.interpret_codes("This is {RED}red{RESET} text.")
    logger.colour_log ("!test","Testing assertion:","!expect", "Expect:", {RED}, "not in interpreted codes",
         log_files=[TEST_LOG_FILE, function_log])
    assert "{RED}" not in interpreted, "interpret_codes should replace {RED}"
    logger.colour_log ("!test","Testing assertion:","!expect", "Expect: '\033[38;2;255;0;0m' in interpreted codes",
         log_files=[TEST_LOG_FILE, function_log])
    assert "\033[38;2;255;0;0m" in interpreted, "Should include ANSI code"
    
    if function_log:
        logger.colour_log("!proc", "ColourManager tests passed.", log_files=[TEST_LOG_FILE,function_log])
    else:
        logger.colour_log("!proc", "ColourManager tests passed.", log_files=TEST_LOG_FILE)
    

# 5. TESTS tuple
TESTS = [(1, "test_example", test_example, test_description)]

# 6. Test Runner
for num, name, func, description in TESTS:
   function_log = os.path.join(TEST_LOG_FOLDER, f"{name}.log")
   try:
      logger.print_rainbow_row(pattern="X-O-", spacer=2, log_files=[TEST_LOG_FILE, function_log])
      logger.apply_border(border_pattern, f"Test {num}: {name}", total_length=60, log_files=[TEST_LOG_FILE, function_log], border_colour='!proc', text_colour='!proc')
      logger.colour_log("!test", "Running test", "!int", num, "!info", ":", "!proc", name, log_files=[TEST_LOG_FILE, function_log])
      time.sleep(1)
      func(function_log=function_log)
      logger.colour_log("!test", "Test", "!int", num, "!info", ":", "!proc", name, "!pass", "PASSED.", log_files=[TEST_LOG_FILE, function_log])
      results.append((num, name, True))
      successful.append(name)
   except Exception as e:
      logger.log_exception(f"{name} failed", e, log_files=[TEST_LOG_FILE, function_log])
      results.append((num, name, False))
      unsuccessful.append(name)
   # Log details, run func, handle results

# 7. Test Summary
# Color-coded summary of passes/failures

# Standardized Test Start/End Section Template

## Start Section
os.system("cls")
print("=== Starting tUilKit ConfigLoader Minimal Test ===")
print(f"Date/Time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"User: {username}")
print(f"Working Directory: {current_path}")
print(f"Command: {' '.join(sys.argv)}")
print("=== Running tUilKit ConfigLoader Minimal Test ===")

## End Section
print("=== tUilKit ConfigLoader Minimal Test ===")
print(f"Date/Time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Duration: {duration:.2f} seconds")
print("=== tUilKit Tests Completed ===")

# Usage: Place these at the start and end of each test script for standardized output and logging.