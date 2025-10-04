"""Resource management for themes, icons, and other assets."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from qtframework.utils.logger import get_logger


if TYPE_CHECKING:
    from collections.abc import Sequence

logger = get_logger(__name__)


class ResourceManager:
    """Manager for application resources (themes, icons, translations, etc.)."""

    def __init__(self, base_dir: Path | None = None) -> None:
        """Initialize resource manager.

        Args:
            base_dir: Base directory for framework resources (defaults to package resources/)
        """
        self._base_dir = base_dir or self._get_default_base_dir()
        self._search_paths: dict[str, list[Path]] = {
            "themes": [],
            "icons": [],
            "translations": [],
        }

        # Add default paths from framework
        self.add_search_path("themes", self._base_dir / "themes")
        self.add_search_path("icons", self._base_dir / "icons")
        self.add_search_path("translations", self._base_dir / "translations")

    def _get_default_base_dir(self) -> Path:
        """Get default base directory for framework resources.

        Returns:
            Path to framework's resources directory
        """
        # When installed as a package, resources are in the package root
        # When running from source, resources are in the project root
        try:
            import qtframework

            package_dir = Path(qtframework.__file__).parent.parent.parent
            resources_dir = package_dir / "resources"
            if resources_dir.exists():
                return resources_dir
        except (ImportError, AttributeError):
            pass

        # Fallback to current working directory
        return Path.cwd() / "resources"

    def add_search_path(self, resource_type: str, path: Path | str) -> None:
        """Add a search path for a resource type.

        Args:
            resource_type: Type of resource (themes, icons, translations)
            path: Path to search for resources

        Example:
            >>> manager = ResourceManager()
            >>> manager.add_search_path("themes", Path("my_app/themes"))
            >>> manager.add_search_path("icons", Path("my_app/icons"))
        """
        path = Path(path)
        if resource_type not in self._search_paths:
            self._search_paths[resource_type] = []

        if path.exists() and path not in self._search_paths[resource_type]:
            self._search_paths[resource_type].append(path)
            logger.info("Added %s search path: %s", resource_type, path)
        elif not path.exists():
            logger.debug("%s search path does not exist: %s", resource_type, path)

    def get_search_paths(self, resource_type: str) -> list[Path]:
        """Get all search paths for a resource type.

        Args:
            resource_type: Type of resource (themes, icons, translations)

        Returns:
            List of search paths in priority order (user paths first, framework paths last)
        """
        return self._search_paths.get(resource_type, []).copy()

    def find_resource(
        self, resource_type: str, resource_name: str, extensions: Sequence[str] | None = None
    ) -> Path | None:
        """Find a resource by name in search paths.

        Args:
            resource_type: Type of resource (themes, icons, translations)
            resource_name: Name of the resource (with or without extension)
            extensions: Optional list of extensions to try (e.g., ['.yaml', '.json'])

        Returns:
            Path to resource if found, None otherwise

        Example:
            >>> manager = ResourceManager()
            >>> theme_path = manager.find_resource("themes", "monokai", [".yaml"])
            >>> icon_path = manager.find_resource("icons", "dropdown-arrow.svg")
        """
        search_paths = self.get_search_paths(resource_type)

        # If resource_name already has an extension, search for exact match
        if Path(resource_name).suffix:
            for search_path in search_paths:
                resource_path = search_path / resource_name
                if resource_path.exists():
                    logger.debug("Found %s resource: %s", resource_type, resource_path)
                    return resource_path
        else:
            # Try with different extensions
            extensions = extensions or [""]
            for search_path in search_paths:
                for ext in extensions:
                    resource_path = search_path / f"{resource_name}{ext}"
                    if resource_path.exists():
                        logger.debug("Found %s resource: %s", resource_type, resource_path)
                        return resource_path

        logger.debug(
            "Resource not found: %s/%s (searched %d paths)",
            resource_type,
            resource_name,
            len(search_paths),
        )
        return None

    def find_all_resources(self, resource_type: str, pattern: str = "*") -> list[Path]:
        """Find all resources of a type matching a pattern.

        Args:
            resource_type: Type of resource (themes, icons, translations)
            pattern: Glob pattern to match (default: "*")

        Returns:
            List of matching resource paths

        Example:
            >>> manager = ResourceManager()
            >>> all_themes = manager.find_all_resources("themes", "*.yaml")
            >>> all_icons = manager.find_all_resources("icons", "*.svg")
        """
        search_paths = self.get_search_paths(resource_type)
        resources: list[Path] = []

        for search_path in search_paths:
            if search_path.exists():
                resources.extend(search_path.glob(pattern))

        logger.debug("Found %d %s resources matching '%s'", len(resources), resource_type, pattern)
        return resources

    def get_resource_url(
        self, resource_type: str, resource_name: str, extensions: Sequence[str] | None = None
    ) -> str | None:
        """Get a resource as a URL for use in stylesheets.

        Args:
            resource_type: Type of resource (themes, icons, translations)
            resource_name: Name of the resource
            extensions: Optional list of extensions to try

        Returns:
            Resource URL (file://...) or None if not found

        Example:
            >>> manager = ResourceManager()
            >>> icon_url = manager.get_resource_url("icons", "dropdown-arrow.svg")
            >>> # Returns: "file:///path/to/resources/icons/dropdown-arrow.svg"
        """
        resource_path = self.find_resource(resource_type, resource_name, extensions)
        if resource_path:
            # Convert to URL format with forward slashes
            url = resource_path.as_posix()
            # For absolute paths, add file:// prefix
            if resource_path.is_absolute():
                return f"file:///{url}" if not url.startswith("/") else f"file://{url}"
            return url
        return None

    def set_base_dir(self, base_dir: Path | str) -> None:
        """Set the base directory for framework resources.

        This will clear existing framework paths and add new ones.

        Args:
            base_dir: New base directory for resources
        """
        base_dir = Path(base_dir)
        self._base_dir = base_dir

        # Clear and re-add default paths
        for resource_type in ["themes", "icons", "translations"]:
            # Remove old framework paths (keep user-added paths)
            self._search_paths[resource_type] = [
                p
                for p in self._search_paths.get(resource_type, [])
                if not str(p).startswith(str(self._base_dir))
            ]
            # Add new framework path
            self.add_search_path(resource_type, base_dir / resource_type)

        logger.info("Set resource base directory to: %s", base_dir)
