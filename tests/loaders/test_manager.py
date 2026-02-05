"""Test suite for ConfigLoader manager."""

from pathlib import Path

import pytest

from pyconfigr.loaders import BaseLoader, ConfigLoader


class TestConfigLoader:
    """Tests for ConfigLoader manager class."""

    def test_detect_and_load_yaml(self, yaml_config_file: Path) -> None:
        """Test auto-detection and loading of YAML file.

        Verifies that ConfigLoader can automatically detect YAML format
        and load the configuration correctly.

        Parameters
        ----------
        yaml_config_file : Path
            Fixture providing a temporary YAML config file.
        """
        config = ConfigLoader.detect_and_load(yaml_config_file)

        assert config["app_name"] == "test_application"
        assert config["debug"] is True

    def test_detect_and_load_json(self, json_config_file: Path) -> None:
        """Test auto-detection and loading of JSON file.

        Verifies that ConfigLoader can automatically detect JSON format
        and load the configuration correctly.

        Parameters
        ----------
        json_config_file : Path
            Fixture providing a temporary JSON config file.
        """
        config = ConfigLoader.detect_and_load(json_config_file)

        assert config["app_name"] == "test_application"
        assert config["debug"] is True

    def test_detect_and_load_toml(self, toml_config_file: Path) -> None:
        """Test auto-detection and loading of TOML file.

        Verifies that ConfigLoader can automatically detect TOML format
        and load the configuration correctly.

        Parameters
        ----------
        toml_config_file : Path
            Fixture providing a temporary TOML config file.
        """
        config = ConfigLoader.detect_and_load(toml_config_file)

        assert config["app_name"] == "test_application"
        assert config["debug"] is True

    def test_detect_unsupported_extension(self, temp_dir: Path) -> None:
        """Test error for unsupported file extension.

        Verifies that ConfigLoader raises an error when attempting to
        load a file with an unsupported extension.

        Parameters
        ----------
        temp_dir : Path
            Fixture providing a temporary directory.
        """
        unsupported_file = temp_dir / "config.ini"
        unsupported_file.write_text("")

        with pytest.raises(ValueError, match="Unsupported file format"):
            ConfigLoader.detect_and_load(unsupported_file)

    def test_get_registered_loaders(self) -> None:
        """Test retrieving list of registered loaders.

        Verifies that all expected loaders are registered and can be
        retrieved from the ConfigLoader.
        """
        loaders = ConfigLoader.list_loaders()

        assert "yaml" in loaders
        assert "json" in loaders
        assert "toml" in loaders
        assert "env" in loaders

    def test_list_extensions(self) -> None:
        """Test retrieving registered file extensions.

        Verifies that all expected file extensions are registered and
        can be retrieved from the ConfigLoader.
        """
        extensions = ConfigLoader.list_extensions()

        assert ".yaml" in extensions
        assert ".yml" in extensions
        assert ".json" in extensions
        assert ".toml" in extensions


class TestConfigLoaderErrorHandling:
    """Test error handling in ConfigLoader."""

    def test_get_unregistered_loader(self) -> None:
        """Test error when requesting unregistered loader type."""
        with pytest.raises(ValueError, match="Unknown loader type"):
            ConfigLoader.get_loader("nonexistent")

    def test_register_invalid_loader_type(self) -> None:
        """Test error when registering non-BaseLoader object."""
        with pytest.raises(TypeError, match="must inherit from BaseLoader"):
            ConfigLoader.register_loader("invalid", "not a loader")

    def test_register_loader_with_extensions(self) -> None:
        """Test registering custom loader with extensions."""

        class DummyLoader(BaseLoader):
            def __call__(self, *args, **kwargs) -> dict:
                return {"test": "value"}

        # Save original registries
        original_loaders = ConfigLoader._loader_registry.copy()
        original_extensions = ConfigLoader._extension_registry.copy()

        try:
            # Register with extensions
            ConfigLoader.register_loader(
                "dummy", DummyLoader(), extensions=[".dummy", "dmy"]
            )

            # Verify registration
            assert "dummy" in ConfigLoader._loader_registry
            assert ".dummy" in ConfigLoader._extension_registry
            assert ".dmy" in ConfigLoader._extension_registry
            assert ConfigLoader._extension_registry[".dummy"] == "dummy"
        finally:
            # Restore original registries
            ConfigLoader._loader_registry.clear()
            ConfigLoader._loader_registry.update(original_loaders)
            ConfigLoader._extension_registry.clear()
            ConfigLoader._extension_registry.update(original_extensions)

    def test_get_loader_returns_singleton(self) -> None:
        """Test that get_loader returns same instance each time."""
        loader1 = ConfigLoader.get_loader("yaml")
        loader2 = ConfigLoader.get_loader("yaml")

        assert loader1 is loader2

    def test_list_loaders_contains_all_defaults(self) -> None:
        """Test that list_loaders shows all expected default loaders."""
        loaders = ConfigLoader.list_loaders()

        assert len(loaders) >= 4
        assert all(loader in loaders for loader in ["yaml", "json", "toml", "env"])

    def test_list_extensions_mapping(self) -> None:
        """Test that extensions are properly mapped to loaders."""
        extensions = ConfigLoader.list_extensions()

        assert extensions.get(".yaml") == "yaml"
        assert extensions.get(".yml") == "yaml"
        assert extensions.get(".json") == "json"
        assert extensions.get(".toml") == "toml"
