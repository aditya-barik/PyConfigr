"""Test suite for ConfigBuilder."""

import os
from pathlib import Path
from unittest import mock

import pytest

from pyconfigr import ConfigBuilder
from pyconfigr.exceptions import (
    ConfigLoadError,
    ConfigNotFoundError,
    ConfigValidationError,
)
from tests.conftest import ComplexConfig, SimpleConfig


class TestConfigBuilder:
    """Tests for ConfigBuilder fluent API."""

    def test_build_basic_config(self) -> None:
        """Test building simple configuration.

        Verifies that ConfigBuilder can create a validated configuration
        object with default values from the Pydantic model.
        """
        config: SimpleConfig = ConfigBuilder(SimpleConfig).build()

        assert config.app_name == "test_app"
        assert config.debug is False
        assert config.port == 8000

    def test_from_file_yaml(self, yaml_config_file: Path) -> None:
        """Test loading configuration from YAML file.

        Parameters
        ----------
        yaml_config_file : Path
            Fixture providing a temporary YAML config file.
        """
        config: ComplexConfig = (
            ConfigBuilder(ComplexConfig).from_file(yaml_config_file).build()
        )

        assert config.app_name == "test_application"
        assert config.debug is True
        assert config.port == 9000

    def test_from_file_json(self, json_config_file: Path) -> None:
        """Test loading configuration from JSON file.

        Parameters
        ----------
        json_config_file : Path
            Fixture providing a temporary JSON config file.
        """
        config: ComplexConfig = (
            ConfigBuilder(ComplexConfig).from_file(json_config_file).build()
        )

        assert config.app_name == "test_application"
        assert config.debug is True

    def test_from_file_optional_missing(self, temp_dir: Path) -> None:
        """Test optional file parameter with missing file.

        Verifies that missing optional files do not raise an error
        and configuration continues with defaults.

        Parameters
        ----------
        temp_dir : Path
            Fixture providing a temporary directory.
        """
        nonexistent = temp_dir / "missing.yaml"

        config: SimpleConfig = (
            ConfigBuilder(SimpleConfig).from_file(nonexistent, optional=True).build()
        )

        assert config.app_name == "test_app"

    def test_from_file_required_missing(self, temp_dir: Path) -> None:
        """Test error when required file is missing.

        Verifies that ConfigBuilder raises ConfigNotFoundError when
        a required configuration file is missing.

        Parameters
        ----------
        temp_dir : Path
            Fixture providing a temporary directory.
        """
        nonexistent = temp_dir / "missing.yaml"

        with pytest.raises(ConfigNotFoundError):
            ConfigBuilder(SimpleConfig).from_file(nonexistent).build()

    def test_from_env(self) -> None:
        """Test loading from environment variables.

        Sets environment variables and verifies they are loaded and
        properly type-parsed by the builder.
        """
        os.environ["SIMPLE_APP_NAME"] = "env_app"
        os.environ["SIMPLE_DEBUG"] = "true"
        os.environ["SIMPLE_PORT"] = "3000"

        try:
            config: SimpleConfig = (
                ConfigBuilder(SimpleConfig).from_env(prefix="SIMPLE_").build()
            )

            assert config.app_name == "env_app"
            assert config.debug is True
            assert config.port == 3000
        finally:
            for key in ["SIMPLE_APP_NAME", "SIMPLE_DEBUG", "SIMPLE_PORT"]:
                del os.environ[key]

    def test_from_dict(self) -> None:
        """Test loading from dictionary.

        Verifies that ConfigBuilder can load configuration from
        a Python dictionary.
        """
        config: SimpleConfig = (
            ConfigBuilder(SimpleConfig)
            .from_dict({"app_name": "dict_app", "port": 5000})
            .build()
        )

        assert config.app_name == "dict_app"
        assert config.port == 5000

    def test_set_value(self) -> None:
        """Test setting individual configuration values.

        Verifies that ConfigBuilder.set() can override individual
        configuration values.
        """
        config: SimpleConfig = (
            ConfigBuilder(SimpleConfig)
            .set("app_name", "set_app")
            .set("port", 7000)
            .build()
        )

        assert config.app_name == "set_app"
        assert config.port == 7000

    def test_set_nested_value(self) -> None:
        """Test setting nested configuration values.

        Verifies that ConfigBuilder.set() supports dot notation
        for setting nested configuration values.
        """
        config: ComplexConfig = (
            ConfigBuilder(ComplexConfig)
            .set("app_name", "test_app")
            .set("debug", True)
            .set("server.host", "example.com")
            .set("server.port", 5432)
            .build()
        )

        assert config.server["host"] == "example.com"
        assert config.server["port"] == 5432

    def test_multiple_sources_priority(
        self, yaml_config_file: Path, json_config_file: Path
    ) -> None:
        """Test priority merging of multiple sources.

        Verifies that when loading from multiple sources, later sources
        override earlier ones (YAML → JSON → dict).

        Parameters
        ----------
        yaml_config_file : Path
            Fixture providing a temporary YAML config file.
        json_config_file : Path
            Fixture providing a temporary JSON config file.
        """
        config: ComplexConfig = (
            ConfigBuilder(ComplexConfig)
            .from_file(yaml_config_file)
            .from_file(json_config_file)
            .from_dict({"port": 7000})
            .build()
        )

        assert config.app_name == "test_application"
        assert config.port == 7000

    def test_get_raw_data(self, yaml_config_file: Path) -> None:
        """Test retrieving unvalidated configuration data.

        Verifies that ConfigBuilder.get_raw_data() returns the raw
        dictionary before Pydantic validation.

        Parameters
        ----------
        yaml_config_file : Path
            Fixture providing a temporary YAML config file.
        """
        builder = ConfigBuilder(ComplexConfig).from_file(yaml_config_file)
        raw_data = builder.get_raw_data()

        assert isinstance(raw_data, dict)
        assert raw_data["app_name"] == "test_application"
        assert raw_data["debug"] is True

    def test_fluent_api_chaining(self, yaml_config_file: Path) -> None:
        """Test fluent API method chaining.

        Verifies that ConfigBuilder methods return self for method
        chaining in a fluent API style.

        Parameters
        ----------
        yaml_config_file : Path
            Fixture providing a temporary YAML config file.
        """
        config: ComplexConfig = (
            ConfigBuilder(ComplexConfig)
            .from_file(yaml_config_file)
            .set("port", 8888)
            .from_dict({"debug": False})
            .build()
        )

        assert config.app_name == "test_application"
        assert config.port == 8888
        assert config.debug is False


class TestIntegration:
    """Integration tests combining multiple components."""

    def test_complete_workflow(
        self, yaml_config_file: Path, json_config_file: Path
    ) -> None:
        """Test complete configuration loading workflow.

        Tests loading config from YAML, JSON, environment variables,
        and direct set() calls with proper priority ordering.

        Parameters
        ----------
        yaml_config_file : Path
            Fixture providing a temporary YAML config file.
        json_config_file : Path
            Fixture providing a temporary JSON config file.
        """
        os.environ["MYAPP_PORT"] = "6000"

        try:
            config: ComplexConfig = (
                ConfigBuilder(ComplexConfig)
                .from_file(yaml_config_file)
                .from_file(json_config_file)
                .from_env("MYAPP_")
                .set("debug", False)
                .build()
            )

            assert config.app_name == "test_application"
            assert config.port == 6000
            assert config.debug is False
        finally:
            del os.environ["MYAPP_PORT"]

    def test_yaml_yml_extension_detection(self, temp_dir: Path) -> None:
        """Test both .yaml and .yml extensions are detected.

        Verifies that ConfigLoader correctly handles both .yaml and .yml
        file extensions.

        Parameters
        ----------
        temp_dir : Path
            Fixture providing a temporary directory.
        """
        from pyconfigr.loaders import ConfigLoader

        yaml_file = temp_dir / "config.yaml"
        yml_file = temp_dir / "config.yml"

        content = "app_name: test\ndebug: false\nport: 8000"
        yaml_file.write_text(content)
        yml_file.write_text(content)

        yaml_config = ConfigLoader.detect_and_load(yaml_file)
        yml_config = ConfigLoader.detect_and_load(yml_file)

        assert yaml_config == yml_config


class TestConfigBuilderExceptionHandling:
    """Test exception handling and edge cases in ConfigBuilder."""

    def test_from_file_with_unsupported_extension(self, temp_dir: Path) -> None:
        """Test error when file has unsupported extension."""
        unsupported_file = temp_dir / "config.unknown"
        unsupported_file.write_text("some content")

        builder = ConfigBuilder(SimpleConfig)

        with pytest.raises(ValueError, match="Unsupported file format"):
            builder.from_file(unsupported_file).build()

    def test_from_file_generic_exception_wrapping(self, temp_dir: Path) -> None:
        """Test that generic exceptions are wrapped in ConfigLoadError."""
        config_file = temp_dir / "config.json"
        config_file.write_text('{"debug": true}')

        builder = ConfigBuilder(SimpleConfig)

        # Mock ConfigLoader.detect_and_load to raise generic exception
        with mock.patch("pyconfigr.builder.ConfigLoader.detect_and_load") as mock_load:
            mock_load.side_effect = RuntimeError("Unexpected error")

            with pytest.raises(ConfigLoadError, match="Failed to load configuration"):
                builder.from_file(config_file).build()

    def test_validation_error_on_invalid_type(self) -> None:
        """Test validation error when config has invalid types."""
        builder = ConfigBuilder(SimpleConfig)

        with pytest.raises(
            ConfigValidationError, match="Configuration validation failed"
        ):
            builder.from_dict({"port": "not_a_number"}).build()

    def test_from_file_propagates_value_error(self, temp_dir: Path) -> None:
        """Test that ValueError from unsupported extension is propagated."""
        unsupported_file = temp_dir / "config.xyz"
        unsupported_file.write_text("content")

        builder = ConfigBuilder(SimpleConfig)

        with pytest.raises(ValueError):
            builder.from_file(unsupported_file).build()

    def test_from_file_propagates_config_load_error(self, temp_dir: Path) -> None:
        """Test that ConfigLoadError from loaders is propagated."""
        config_file = temp_dir / "config.json"
        config_file.write_text('{"debug": true}')

        builder = ConfigBuilder(SimpleConfig)

        # Mock to raise ConfigLoadError directly
        with mock.patch("pyconfigr.builder.ConfigLoader.detect_and_load") as mock_load:
            mock_load.side_effect = ConfigLoadError("Parse error")

            with pytest.raises(ConfigLoadError, match="Parse error"):
                builder.from_file(config_file).build()


class TestConfigBuilderDeepMerge:
    """Test deep merge functionality in ConfigBuilder."""

    def test_deep_merge_nested_dicts(self) -> None:
        """Test merging nested dictionaries."""
        builder = ConfigBuilder(SimpleConfig)

        dict1 = {"nested": {"a": 1, "b": 2}}
        dict2 = {"nested": {"b": 3, "c": 4}}

        builder._deep_merge(dict1, dict2)

        assert dict1["nested"]["a"] == 1
        assert dict1["nested"]["b"] == 3
        assert dict1["nested"]["c"] == 4

    def test_deep_merge_overwrites_non_dict(self) -> None:
        """Test that deep merge overwrites non-dict values."""
        builder = ConfigBuilder(SimpleConfig)

        dict1 = {"value": "original"}
        dict2 = {"value": "updated"}

        builder._deep_merge(dict1, dict2)

        assert dict1["value"] == "updated"

    def test_deep_merge_with_lists(self) -> None:
        """Test that lists are overwritten, not merged."""
        builder = ConfigBuilder(SimpleConfig)

        dict1 = {"items": [1, 2, 3]}
        dict2 = {"items": [4, 5]}

        builder._deep_merge(dict1, dict2)

        assert dict1["items"] == [4, 5]

    def test_deep_merge_with_none_values(self) -> None:
        """Test merging with None values."""
        builder = ConfigBuilder(SimpleConfig)

        dict1 = {"key": "value"}
        dict2 = {"key": None}

        builder._deep_merge(dict1, dict2)

        assert dict1["key"] is None

    def test_deep_merge_preserves_unmatched_keys(self) -> None:
        """Test that unmatched keys are preserved."""
        builder = ConfigBuilder(SimpleConfig)

        dict1 = {"a": 1, "b": 2}
        dict2 = {"c": 3}

        builder._deep_merge(dict1, dict2)

        assert dict1["a"] == 1
        assert dict1["b"] == 2
        assert dict1["c"] == 3


class TestConfigBuilderSetMethod:
    """Test set method with dot notation."""

    def test_set_simple_key(self) -> None:
        """Test setting a simple key."""
        builder = ConfigBuilder(SimpleConfig)
        builder.set("app_name", "my_app")

        raw = builder.get_raw_data()
        assert raw["app_name"] == "my_app"

    def test_set_nested_key_with_dot_notation(self) -> None:
        """Test setting nested key using dot notation."""
        builder = ConfigBuilder(SimpleConfig)
        builder.set("database.host", "localhost")
        builder.set("database.port", 5432)

        raw = builder.get_raw_data()
        assert raw["database"]["host"] == "localhost"
        assert raw["database"]["port"] == 5432

    def test_set_deeply_nested_key(self) -> None:
        """Test setting deeply nested key."""
        builder = ConfigBuilder(SimpleConfig)
        builder.set("app.db.connection.host", "db.example.com")

        raw = builder.get_raw_data()
        assert raw["app"]["db"]["connection"]["host"] == "db.example.com"

    def test_set_overwrites_existing_value(self) -> None:
        """Test that set overwrites existing values."""
        builder = ConfigBuilder(SimpleConfig)
        builder.set("debug", False)
        builder.set("debug", True)

        raw = builder.get_raw_data()
        assert raw["debug"] is True

    def test_set_method_returns_self(self) -> None:
        """Test that set method returns self for chaining."""
        builder = ConfigBuilder(SimpleConfig)
        result = builder.set("key", "value")

        assert result is builder


class TestConfigBuilderFluentAPI:
    """Test fluent API chaining."""

    def test_chaining_all_methods(self, temp_dir: Path) -> None:
        """Test chaining multiple methods."""
        config_file = temp_dir / "config.json"
        config_file.write_text('{"app_name": "file_app"}')

        os.environ["FLUENT_DEBUG"] = "true"

        try:
            config: SimpleConfig = (
                ConfigBuilder(SimpleConfig)
                .from_file(config_file)
                .from_env(prefix="FLUENT_")
                .set("port", 7000)
                .build()
            )

            assert config.app_name == "file_app"
            assert config.debug is True
            assert config.port == 7000
        finally:
            del os.environ["FLUENT_DEBUG"]

    def test_multiple_from_dict_calls(self) -> None:
        """Test multiple from_dict calls with proper priority."""
        builder = ConfigBuilder(SimpleConfig)
        config: SimpleConfig = (
            builder.from_dict({"debug": False, "port": 8000})
            .from_dict({"debug": True})
            .from_dict({"port": 9000})
            .build()
        )

        assert config.debug is True
        assert config.port == 9000

    def test_get_raw_data(self, temp_dir: Path) -> None:
        """Test get_raw_data returns copy of internal data."""
        config_file = temp_dir / "config.json"
        config_file.write_text('{"port": 3000}')

        builder = ConfigBuilder(SimpleConfig).from_file(config_file)
        raw1 = builder.get_raw_data()
        raw2 = builder.get_raw_data()

        # Should be equal but different objects
        assert raw1 == raw2
        assert raw1 is not raw2

        # Modifying returned data shouldn't affect builder
        raw1["port"] = 9999
        raw3 = builder.get_raw_data()
        assert raw3["port"] == 3000
