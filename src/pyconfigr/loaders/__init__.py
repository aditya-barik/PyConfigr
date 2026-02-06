"""Configuration loaders for different file formats and sources."""

from .base import BaseLoader
from .env import ENVLoader
from .json import JSONLoader
from .manager import ConfigLoader
from .toml import TOMLLoader
from .yaml import YAMLLoader

# Create singleton instances for convenient direct usage
yaml_loader = YAMLLoader()
json_loader = JSONLoader()
toml_loader = TOMLLoader()
env_loader = ENVLoader()

# Auto-register all loaders with ConfigLoader
# This allows auto-detection by file extension and centralized loader management
ConfigLoader.register_loader("yaml", yaml_loader, extensions=[".yaml", ".yml"])
ConfigLoader.register_loader("json", json_loader, extensions=[".json"])
ConfigLoader.register_loader("toml", toml_loader, extensions=[".toml"])
ConfigLoader.register_loader("env", env_loader)

__all__ = [
    # Base class
    "BaseLoader",
    # Loader classes
    "YAMLLoader",
    "JSONLoader",
    "TOMLLoader",
    "ENVLoader",
    # Loader manager
    "ConfigLoader",
    # Singleton instances for convenience
    "yaml_loader",
    "json_loader",
    "toml_loader",
    "env_loader",
]
