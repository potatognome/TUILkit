#!/usr/bin/env python3
"""
Example: Customizing tUilKit Logging Categories

This example shows different ways to customize logging categories in tUilKit.
"""

import os
import json
from tUilKit.utils.output import Logger, ColourManager
from tUilKit.utils.fs import FileSystem
from tUilKit.config.config import ConfigLoader

def example_1_modify_global_config():
    """
    Method 1: Modify GLOBAL_CONFIG.json to add custom categories
    This is the easiest method for persistent customization.
    """
    print("=== Method 1: Modify GLOBAL_CONFIG.json ===")

    # Load colour config using ConfigLoader
    config_loader = ConfigLoader()
    colour_config = config_loader.load_colour_config()

    colour_manager = ColourManager(colour_config)
    logger = Logger(colour_manager)

    # Now you can use the custom categories defined in GLOBAL_CONFIG.json
    logger.colour_log("!info", "Testing custom 'debug' category", category="debug")
    logger.colour_log("!info", "Testing custom 'database' category", category="database")
    logger.colour_log("!info", "Testing custom 'warning' category", category="warning")
    logger.colour_log("!info", "Testing 'all' category (logs to all files)", category="all")

def example_2_runtime_customization():
    """
    Method 2: Create custom Logger/FileSystem with runtime category customization
    Useful for temporary or per-session customization.
    """
    print("\n=== Method 2: Runtime Customization ===")

    # Load colour config using ConfigLoader
    config_loader = ConfigLoader()
    colour_config = config_loader.load_colour_config()

    colour_manager = ColourManager(colour_config)

    # Define custom log files
    custom_log_files = {
        "SESSION": "logs/custom_session.log",
        "MASTER": "logs/custom_master.log",
        "ERROR": "logs/custom_error.log",
        "API": "logs/api.log",
        "NETWORK": "logs/network.log"
    }

    # Define custom categories
    custom_categories = {
        "default": ["MASTER", "SESSION"],
        "error": ["ERROR", "SESSION", "MASTER"],
        "api": ["API", "SESSION", "MASTER"],
        "network": ["NETWORK", "SESSION"],
        "security": ["ERROR", "MASTER", "API"],  # Custom security category
        "all": ["MASTER", "SESSION", "ERROR", "API", "NETWORK"]
    }

    # Create logger with custom setup
    logger = Logger(colour_manager, log_files=custom_log_files)
    # Override the LOG_KEYS with custom categories
    logger.LOG_KEYS = custom_categories

    # Create filesystem with same custom setup
    fs = FileSystem(logger, custom_log_files)
    fs.LOG_KEYS = custom_categories

    # Test custom categories
    logger.colour_log("!info", "Testing custom 'api' category", category="api")
    logger.colour_log("!info", "Testing custom 'network' category", category="network")
    logger.colour_log("!info", "Testing custom 'security' category", category="security")

    # Test filesystem with custom categories
    fs.validate_and_create_folder("test_custom_logs", category="security")

def example_3_category_inheritance():
    """
    Method 3: Create category inheritance/combinations
    Shows how to build complex logging setups.
    """
    print("\n=== Method 3: Category Inheritance ===")

    # Load colour config using ConfigLoader
    config_loader = ConfigLoader()
    colour_config = config_loader.load_colour_config()

    colour_manager = ColourManager(colour_config)

    # Advanced category setup with inheritance
    advanced_categories = {
        "default": ["MASTER", "SESSION"],
        "error": ["ERROR", "SESSION", "MASTER"],
        "fs": ["MASTER", "SESSION", "FS"],
        "init": ["INIT", "SESSION", "MASTER"],

        # Application-specific categories
        "auth": ["MASTER", "SESSION", "ERROR"],  # Authentication logs
        "business": ["MASTER", "SESSION"],       # Business logic logs
        "performance": ["MASTER", "DEBUG"],      # Performance monitoring

        # Combined categories (multi-category logging)
        "critical": ["ERROR", "MASTER", "SESSION", "DEBUG"],  # All important logs
        "verbose": ["MASTER", "SESSION", "ERROR", "FS", "INIT", "DEBUG"],  # Everything
    }

    logger = Logger(colour_manager)
    logger.LOG_KEYS = advanced_categories

    # Demonstrate different logging levels
    logger.colour_log("!info", "Standard business operation", category="business")
    logger.colour_log("!warn", "Authentication attempt", category="auth")
    logger.colour_log("!calc", "Performance metric: 150ms", category="performance")
    logger.colour_log("!error", "Critical system error", category="critical")

def example_4_dynamic_categories():
    """
    Method 4: Dynamic category creation based on runtime conditions
    Useful for plugins or modular applications.
    """
    print("\n=== Method 4: Dynamic Categories ===")

    # Load colour config using ConfigLoader
    config_loader = ConfigLoader()
    colour_config = config_loader.load_colour_config()

    colour_manager = ColourManager(colour_config)
    logger = Logger(colour_manager)

    # Start with base categories
    dynamic_categories = {
        "default": ["MASTER", "SESSION"],
        "error": ["ERROR", "SESSION", "MASTER"],
    }

    # Dynamically add categories based on available modules/plugins
    available_modules = ["user_mgmt", "payment", "inventory", "reporting"]

    for module in available_modules:
        # Create module-specific log file
        log_key = module.upper()
        log_path = f"logs/{module}.log"

        # Add to log files (in real usage, you'd create the file)
        logger.log_files[log_key] = log_path

        # Add category for this module
        dynamic_categories[module] = ["MASTER", "SESSION", log_key]
        dynamic_categories[f"{module}_error"] = ["ERROR", "SESSION", "MASTER", log_key]

    logger.LOG_KEYS = dynamic_categories

    # Test dynamic categories
    for module in available_modules:
        logger.colour_log("!info", f"Module {module} initialized", category=module)
        logger.colour_log("!warn", f"Module {module} warning", category=f"{module}_error")

if __name__ == "__main__":
    print("tUilKit Logging Categories Customization Examples")
    print("=" * 50)

    # Run examples
    example_1_modify_global_config()
    example_2_runtime_customization()
    example_3_category_inheritance()
    example_4_dynamic_categories()

    print("\n" + "=" * 50)
    print("All examples completed! Check the logs/ directory for output files.")