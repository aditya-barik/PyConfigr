"""
PyConfigr: Flexible configuration management with Pydantic validation.

A modern, type-safe configuration management library that supports multiple
formats (YAML, JSON, TOML, environment variables) with Pydantic validation
and a fluent API.

Examples:
    Basic usage:
    >>> from pydantic import BaseModel
    >>> from pyconfigr import ConfigBuilder
    >>>
    >>> class AppConfig(BaseModel):
    ...     debug: bool = False
    ...     port: int = 8000
    ...     database_url: str
    >>>
    >>> config = (
    ...     ConfigBuilder(AppConfig)
    ...     .from_yaml("config.yaml")
    ...     .from_env("MYAPP_")
    ...     .build()
    ... )

    Multiple sources:
    >>> config = (
    ...     ConfigBuilder(AppConfig)
    ...     .from_yaml("base.yaml")
    ...     .from_json("overrides.json")
    ...     .from_env()
    ...     .from_dict({"debug": True})
    ...     .build()
    ... )
"""

from importlib.metadata import PackageNotFoundError, version

from .builder import ConfigBuilder
from .exceptions import (
    ConfigError,
    ConfigLoadError,
    ConfigNotFoundError,
    ConfigValidationError,
)

try:
    __version__ = version("pyconfigr")
except PackageNotFoundError:
    __version__ = "0.1.0.dev0"

__all__ = [
    "ConfigBuilder",
    "ConfigError",
    "ConfigLoadError",
    "ConfigNotFoundError",
    "ConfigValidationError",
]
