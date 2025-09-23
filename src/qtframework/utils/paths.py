"""Cross-platform path utilities for standard directories."""

from __future__ import annotations

import os
import platform
from pathlib import Path
from typing import Optional

from qtframework.utils.logger import get_logger

logger = get_logger(__name__)


def get_user_config_dir(app_name: str) -> Path:
    """Get user-specific config directory for the application.

    Args:
        app_name: Application name (used as subdirectory)

    Returns:
        Path to user config directory

    Examples:
        Windows: C:/Users/username/AppData/Local/MyApp
        macOS: ~/Library/Application Support/MyApp
        Linux: ~/.config/MyApp
    """
    system = platform.system().lower()

    if system == "windows":
        # Windows: %LOCALAPPDATA%/AppName
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    elif system == "darwin":
        # macOS: ~/Library/Application Support/AppName
        base = Path.home() / "Library" / "Application Support"
    else:
        # Linux/Unix: ~/.config/AppName (XDG Base Directory)
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))

    config_dir = base / app_name
    return config_dir


def get_user_data_dir(app_name: str) -> Path:
    """Get user-specific data directory for the application.

    Args:
        app_name: Application name (used as subdirectory)

    Returns:
        Path to user data directory

    Examples:
        Windows: C:/Users/username/AppData/Local/MyApp
        macOS: ~/Library/Application Support/MyApp
        Linux: ~/.local/share/MyApp
    """
    system = platform.system().lower()

    if system == "windows":
        # Windows: %LOCALAPPDATA%/AppName
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    elif system == "darwin":
        # macOS: ~/Library/Application Support/AppName
        base = Path.home() / "Library" / "Application Support"
    else:
        # Linux/Unix: ~/.local/share/AppName (XDG Base Directory)
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))

    data_dir = base / app_name
    return data_dir


def get_user_cache_dir(app_name: str) -> Path:
    """Get user-specific cache directory for the application.

    Args:
        app_name: Application name (used as subdirectory)

    Returns:
        Path to user cache directory

    Examples:
        Windows: C:/Users/username/AppData/Local/MyApp/Cache
        macOS: ~/Library/Caches/MyApp
        Linux: ~/.cache/MyApp
    """
    system = platform.system().lower()

    if system == "windows":
        # Windows: %LOCALAPPDATA%/AppName/Cache
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        cache_dir = base / app_name / "Cache"
    elif system == "darwin":
        # macOS: ~/Library/Caches/AppName
        cache_dir = Path.home() / "Library" / "Caches" / app_name
    else:
        # Linux/Unix: ~/.cache/AppName (XDG Base Directory)
        base = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
        cache_dir = base / app_name

    return cache_dir


def get_system_config_dir(app_name: str) -> Optional[Path]:
    """Get system-wide config directory for the application.

    Args:
        app_name: Application name (used as subdirectory)

    Returns:
        Path to system config directory, or None if not applicable

    Examples:
        Windows: None (no standard system config)
        macOS: /Library/Application Support/MyApp
        Linux: /etc/MyApp
    """
    system = platform.system().lower()

    if system == "windows":
        # Windows doesn't have a standard system config location
        return None
    elif system == "darwin":
        # macOS: /Library/Application Support/AppName
        return Path("/Library/Application Support") / app_name
    else:
        # Linux/Unix: /etc/AppName
        return Path("/etc") / app_name


def ensure_directory(path: Path) -> bool:
    """Ensure directory exists, creating it if necessary.

    Args:
        path: Directory path to ensure

    Returns:
        True if directory exists or was created successfully
    """
    try:
        path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured directory exists: {path}")
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {path}: {e}")
        return False


def find_config_files(app_name: str, config_filename: str = "config.json") -> list[Path]:
    """Find all possible config files for an application in standard locations.

    Args:
        app_name: Application name
        config_filename: Config file name (default: config.json)

    Returns:
        List of config file paths that exist, ordered by priority (system -> user -> local)
    """
    config_files = []

    # 1. System-wide config (lowest priority)
    system_dir = get_system_config_dir(app_name)
    if system_dir:
        system_config = system_dir / config_filename
        if system_config.exists():
            config_files.append(system_config)
            logger.debug(f"Found system config: {system_config}")

    # 2. User config directory (medium priority)
    user_dir = get_user_config_dir(app_name)
    user_config = user_dir / config_filename
    if user_config.exists():
        config_files.append(user_config)
        logger.debug(f"Found user config: {user_config}")

    # 3. Current working directory (highest priority)
    local_config = Path.cwd() / config_filename
    if local_config.exists():
        config_files.append(local_config)
        logger.debug(f"Found local config: {local_config}")

    return config_files


def get_preferred_config_path(app_name: str, config_filename: str = "config.json") -> Path:
    """Get the preferred path for saving user config.

    Args:
        app_name: Application name
        config_filename: Config file name (default: config.json)

    Returns:
        Preferred config file path for saving
    """
    user_dir = get_user_config_dir(app_name)
    return user_dir / config_filename