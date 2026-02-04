"""
Fluent API builder for configuration management.

This module provides the ConfigBuilder class that allows loading and merging
configuration from multiple sources with Pydantic validation.
"""

from pathlib import Path
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from .exceptions import ConfigLoadError, ConfigNotFoundError, ConfigValidationError
from .loaders import ConfigLoader

T = TypeVar("T", bound=BaseModel)


class ConfigBuilder:
    """
    Fluent API builder for loading and validating configuration.

    Allows loading configuration from multiple sources (YAML, JSON, TOML,
    environment variables, dictionaries) and merging them with proper
    priority. The final configuration is validated using a Pydantic model.

    Examples
    --------
    Basic usage:

    >>> from pydantic import BaseModel
    >>> from pyconfigr import ConfigBuilder
    >>>
    >>> class AppConfig(BaseModel):
    ...     debug: bool = False
    ...     port: int = 8000
    >>>
    >>> config = (ConfigBuilder(AppConfig)
    ...     .from_file("config.yaml")
    ...     .from_env("MYAPP_")
    ...     .build())

    Multiple sources with priority:

    >>> config = (ConfigBuilder(AppConfig)
    ...     .from_file("base.yaml")      # Lowest priority
    ...     .from_file("overrides.json")  # Medium priority
    ...     .from_env("MYAPP_")           # Higher priority
    ...     .from_dict({"debug": True})   # Highest priority
    ...     .build())
    """

    def __init__(self, config_class: type[T]) -> None:
        """
        Initialize the ConfigBuilder.

        Parameters
        ----------
        config_class : type[T]
            Pydantic BaseModel class to use for validation.
        """
        self.config_class = config_class
        self._data: dict[str, Any] = {}

    def from_file(self, path: str | Path, optional: bool = False) -> "ConfigBuilder":
        """
        Load configuration from a file with auto-detected format.

        Automatically detects file format from extension and uses the
        appropriate loader. Supports all registered loaders: YAML, JSON, TOML,
        and any custom loaders.

        Parameters
        ----------
        path : str | Path
            Path to configuration file (.yaml, .json, .toml, etc.)
        optional : bool, optional
            If True, don't raise error if file doesn't exist. Default is False.

        Returns
        -------
        ConfigBuilder
            Self for method chaining.

        Raises
        ------
        ConfigNotFoundError
            If file not found and optional=False.
        ConfigLoadError
            If file cannot be loaded or parsed.
        ValueError
            If file extension is not supported.

        Examples
        --------
        >>> config = (ConfigBuilder(AppConfig)
        ...     .from_file("config.yaml")
        ...     .build())

        >>> config = (ConfigBuilder(AppConfig)
        ...     .from_file("config.json", optional=True)
        ...     .from_file("config.toml", optional=True)
        ...     .build())
        """
        path = Path(path)
        if not path.exists():
            if optional:
                return self
            raise ConfigNotFoundError(f"Configuration file not found: {path}")

        try:
            data = ConfigLoader.detect_and_load(path)
            self._merge(data)
        except ValueError:
            # Re-raise ValueError from unsupported extension as-is
            raise
        except ConfigLoadError:
            # Re-raise ConfigLoadError from loaders as-is
            raise
        except Exception as e:
            # Catch any other exceptions and wrap them
            raise ConfigLoadError(
                f"Failed to load configuration from {path}: {e}"
            ) from e

        return self

    def from_env(
        self, prefix: str = "", lowercase: bool = True, strip_prefix: bool = True
    ) -> "ConfigBuilder":
        """
        Load configuration from environment variables.

        Parameters
        ----------
        prefix : str, optional
            Only load variables with this prefix (e.g., "MYAPP_")
            Default is empty string.
        lowercase : bool, optional
            Convert keys to lowercase. Default is True.
        strip_prefix : bool, optional
            Remove prefix from keys. Default is True.

        Returns
        -------
        ConfigBuilder
            Self for method chaining.

        Examples
        --------
        With MYAPP_DEBUG=true, MYAPP_PORT=8000

        >>> config = (ConfigBuilder(AppConfig)
        ...     .from_env("MYAPP_")
        ...     .build())
        """
        loader = ConfigLoader.get_loader("env")
        data = loader(prefix=prefix, lowercase=lowercase, strip_prefix=strip_prefix)
        self._merge(data)
        return self

    def from_dict(self, data: dict[str, Any]) -> "ConfigBuilder":
        """
        Load configuration from a dictionary.

        Parameters
        ----------
        data : dict[str, Any]
            Configuration dictionary.

        Returns
        -------
        ConfigBuilder
            Self for method chaining.

        Examples
        --------
        >>> config = (ConfigBuilder(AppConfig)
        ...     .from_dict({"debug": True, "port": 3000})
        ...     .build())
        """
        self._merge(data)
        return self

    def set(self, key: str, value: Any) -> "ConfigBuilder":
        """
        Set a single configuration value.

        Parameters
        ----------
        key : str
            Configuration key (supports dot notation for nested keys).
        value : Any
            Configuration value.

        Returns
        -------
        ConfigBuilder
            Self for method chaining.

        Examples
        --------
        >>> config = (ConfigBuilder(AppConfig)
        ...     .set("debug", True)
        ...     .set("server.port", 8080)
        ...     .build())
        """
        # Support dot notation for nested keys
        if "." in key:
            keys = key.split(".")
            current = self._data
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            current[keys[-1]] = value
        else:
            self._data[key] = value

        return self

    def _merge(self, new_data: dict[str, Any]) -> None:
        """
        Deep merge new data into existing configuration.

        Later calls override earlier ones for the same keys.

        Parameters
        ----------
        new_data : dict[str, Any]
            Dictionary to merge.
        """
        self._deep_merge(self._data, new_data)

    def _deep_merge(self, target: dict[str, Any], source: dict[str, Any]) -> None:
        """
        Recursively merge source dictionary into target dictionary.

        Parameters
        ----------
        target : dict[str, Any]
            Target dictionary (modified in place).
        source : dict[str, Any]
            Source dictionary.
        """
        for key, value in source.items():
            if (
                key in target
                and isinstance(target[key], dict)
                and isinstance(value, dict)
            ):
                # Recursively merge nested dictionaries
                self._deep_merge(target[key], value)
            else:
                # Override value
                target[key] = value

    def build(self) -> T:
        """
        Build and validate the final configuration.

        Returns
        -------
        T
            Validated configuration object (instance of config_class).

        Raises
        ------
        ConfigValidationError
            If configuration fails validation.

        Examples
        --------
        >>> config = (ConfigBuilder(AppConfig)
        ...     .from_file("config.yaml")
        ...     .build())
        >>> print(config.debug)
        """
        try:
            return self.config_class.model_validate(self._data)
        except ValidationError as e:
            raise ConfigValidationError(
                f"Configuration validation failed for {self.config_class.__name__}: {e}"
            ) from e

    def get_raw_data(self) -> dict[str, Any]:
        """
        Get the raw configuration data before validation.

        Useful for debugging or when you need the unvalidated data.

        Returns
        -------
        dict[str, Any]
            Raw configuration dictionary.
        """
        return self._data.copy()
