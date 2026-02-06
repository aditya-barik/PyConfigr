"""Configuration loader manager with auto-detection and registry management."""

from pathlib import Path
from typing import Any

from .base import BaseLoader


class ConfigLoader:
    """
    Unified configuration loader with auto-detection and registry management.

    Manages loader instantiation and delegation based on file extensions.
    Supports dynamic loader registration for maximum extensibility.

    When a new loader is added (e.g., loaders/ini.py with INILoader class),
    it's automatically discovered and registered. No code changes needed elsewhere.

    Examples
    --------
    Auto-detect and load by file extension:
    >>> ConfigLoader.detect_and_load("config.yaml")
    {'debug': True, 'port': 8000}

    Get specific loader:
    >>> yaml_loader = ConfigLoader.get_loader("yaml")
    >>> config = yaml_loader("config.yaml")

    Register custom loader:
    >>> ConfigLoader.register_loader("custom", CustomLoader())
    """

    # Registry mapping file extensions to loader types
    _extension_registry: dict[str, str] = {
        ".yaml": "yaml",
        ".yml": "yaml",
        ".json": "json",
        ".toml": "toml",
    }

    # Registry mapping loader types to loader instances
    _loader_registry: dict[str, BaseLoader] = {}

    @classmethod
    def detect_and_load(cls, path: str | Path) -> dict[str, Any]:
        """
        Auto-detect file format and load configuration.

        Detects format from file extension and uses appropriate loader.

        Parameters
        ----------
        path : str | Path
            Path to configuration file.

        Returns
        -------
        dict[str, Any]
            Dictionary containing configuration.

        Raises
        ------
        ConfigLoadError
            If file cannot be loaded or parsed.
        ValueError
            If file extension is not recognized.

        Examples
        --------
        >>> config = ConfigLoader.detect_and_load("config.yaml")
        >>> config = ConfigLoader.detect_and_load("config.json")
        """
        file_path = Path(path)
        extension = file_path.suffix.lower()

        if extension not in cls._extension_registry:
            raise ValueError(
                f"Unsupported file format: {extension}. "
                f"Supported formats: {', '.join(cls._extension_registry.keys())}"
            )

        loader_type = cls._extension_registry[extension]
        loader = cls.get_loader(loader_type)
        return loader(file_path)

    @classmethod
    def get_loader(cls, loader_type: str) -> BaseLoader:
        """
        Get a loader instance by type.

        Parameters
        ----------
        loader_type : str
            Type of loader ("yaml", "json", "toml", "env", etc.).

        Returns
        -------
        BaseLoader
            Loader instance.

        Raises
        ------
        ValueError
            If loader_type is not registered.

        Examples
        --------
        >>> yaml_loader = ConfigLoader.get_loader("yaml")
        >>> json_loader = ConfigLoader.get_loader("json")
        """
        if loader_type not in cls._loader_registry:
            raise ValueError(
                f"Unknown loader type: {loader_type}. "
                f"Available loaders: {', '.join(cls._loader_registry.keys())}"
            )
        return cls._loader_registry[loader_type]

    @classmethod
    def register_loader(
        cls, loader_type: str, loader: BaseLoader, extensions: list[str] | None = None
    ) -> None:
        """
        Register a loader instance.

        Allows both built-in and custom loaders to be registered.
        Optionally register file extensions for auto-detection.

        Parameters
        ----------
        loader_type : str
            Identifier for the loader (e.g., "yaml", "ini").
        loader : BaseLoader
            Loader instance (must inherit from BaseLoader).
        extensions : list[str] | None, optional
            List of file extensions to register (e.g., [".ini", ".cfg"]).

        Raises
        ------
        TypeError
            If loader doesn't inherit from BaseLoader.

        Examples
        --------
        Register built-in loader:
        >>> from .yaml import YAMLLoader
        >>> ConfigLoader.register_loader("yaml", YAMLLoader())

        Register custom loader with extensions:
        >>> ConfigLoader.register_loader(
        ...     "ini",
        ...     INILoader(),
        ...     extensions=[".ini", ".cfg"]
        ... )
        """
        if not isinstance(loader, BaseLoader):
            raise TypeError(f"Loader must inherit from BaseLoader, got {type(loader)}")

        cls._loader_registry[loader_type] = loader

        if extensions:
            for ext in extensions:
                # Normalize extension format
                normalized_ext = ext if ext.startswith(".") else f".{ext}"
                cls._extension_registry[normalized_ext.lower()] = loader_type

    @classmethod
    def list_loaders(cls) -> list[str]:
        """
        List all registered loaders.

        Returns
        -------
        list[str]
            List of registered loader type names.

        Examples
        --------
        >>> ConfigLoader.list_loaders()
        ['yaml', 'json', 'toml', 'env']
        """
        return list(cls._loader_registry.keys())

    @classmethod
    def list_extensions(cls) -> dict[str, str]:
        """
        List all registered file extensions and their loader types.

        Returns
        -------
        dict[str, str]
            Dictionary mapping extensions to loader types.

        Examples
        --------
        >>> ConfigLoader.list_extensions()
        {'.yaml': 'yaml', '.yml': 'yaml', '.json': 'json', ...}
        """
        return cls._extension_registry.copy()
