#!/usr/bin/env python3
"""Demo of the standardized configuration system."""

from __future__ import annotations

import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from qtframework.config import ConfigManager
from qtframework.utils import setup_logging, get_logger

# Setup logging to see what's happening
setup_logging()
logger = get_logger(__name__)


def main() -> None:
    """Demonstrate the standardized config system."""
    print("Qt Framework - Standardized Configuration Demo")
    print("=" * 50)

    # Initialize config manager
    config_manager = ConfigManager()

    # Define application defaults
    app_defaults = {
        "app": {
            "name": "Config Demo App",
            "version": "1.0.0",
            "debug": False,
        },
        "ui": {
            "theme": "light",
            "font_size": 12,
            "language": "en",
            "window": {
                "width": 800,
                "height": 600,
                "maximized": False,
            },
        },
        "features": {
            "auto_save": True,
            "notifications": True,
            "advanced_mode": False,
        },
        "performance": {
            "cache_size": 100,
            "max_threads": 4,
        },
    }

    print("\n1. Application Defaults:")
    print("   Defined sensible defaults for all settings")

    # Load standardized configuration
    app_name = "QtFrameworkConfigDemo"
    loaded_count = config_manager.load_standard_configs(
        app_name=app_name,
        config_filename="settings.json",
        defaults=app_defaults
    )

    print(f"\n2. Config Discovery & Loading:")
    print(f"   Loaded configuration from {loaded_count} sources")

    # Show configuration info
    config_info = config_manager.get_config_info(app_name, "settings.json")
    print(f"   User config directory: {config_info['user_config_dir']}")
    print(f"   Preferred save location: {config_info['preferred_config_path']}")

    if config_info['existing_configs']:
        print("   Found existing configs:")
        for config_file in config_info['existing_configs']:
            print(f"     - {config_file}")
    else:
        print("   No existing config files found (using defaults)")

    print(f"\n3. Configuration Sources (priority order):")
    for i, source in enumerate(config_manager.get_sources(), 1):
        print(f"   {i}. {source}")

    print(f"\n4. Current Configuration Values:")
    print(f"   App Name: {config_manager.get('app.name')}")
    print(f"   Theme: {config_manager.get('ui.theme')}")
    print(f"   Window Size: {config_manager.get('ui.window.width')}x{config_manager.get('ui.window.height')}")
    print(f"   Auto Save: {config_manager.get('features.auto_save')}")
    print(f"   Cache Size: {config_manager.get('performance.cache_size')} MB")

    print(f"\n5. Making Runtime Changes:")
    # Simulate user making changes
    config_manager.set("ui.theme", "dark")
    config_manager.set("ui.font_size", 14)
    config_manager.set("ui.window.maximized", True)
    config_manager.set("features.advanced_mode", True)
    config_manager.set("user.custom_setting", "my_preference")

    print("   > Changed theme to 'dark'")
    print("   > Increased font size to 14")
    print("   > Enabled window maximization")
    print("   > Enabled advanced mode")
    print("   > Added custom user setting")

    print(f"\n6. Saving User Configuration:")
    # Save only the changes (not defaults)
    save_success = config_manager.save_user_config(
        app_name=app_name,
        config_filename="settings.json",
        exclude_defaults=True
    )

    if save_success:
        print(f"   > Saved user config to: {config_info['preferred_config_path']}")
        print("   > Only changed values saved (clean user config)")

        # Show what was actually saved
        saved_path = Path(config_info['preferred_config_path'])
        if saved_path.exists():
            import json
            with open(saved_path, 'r') as f:
                saved_data = json.load(f)
            print("   Saved content:")
            print(json.dumps(saved_data, indent=6))

        # Clean up the demo file
        if saved_path.exists():
            saved_path.unlink()
            saved_path.parent.rmdir()
            print("   > Cleaned up demo files")
    else:
        print("   X Failed to save user config")

    print(f"\n7. Environment Variable Support:")
    print(f"   Set environment variables like:")
    print(f"   {app_name.upper()}_UI_THEME=dark")
    print(f"   {app_name.upper()}_FEATURES_AUTO_SAVE=false")
    print(f"   (These would override file-based settings)")

    print(f"\n8. Usage Summary:")
    print("   This system provides:")
    print("   * Cross-platform standard directories")
    print("   * Layered configuration (defaults -> system -> user -> local -> env)")
    print("   * Clean user config files (only overrides)")
    print("   * Automatic discovery and loading")
    print("   * Environment variable support")
    print("   * Validation and error handling")

    print(f"\nConfiguration demo completed successfully!")


if __name__ == "__main__":
    main()