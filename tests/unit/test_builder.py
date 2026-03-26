"""Test suite for ConfigBuilder."""

import os
from pathlib import Path
from unittest import mock

import pytest
from tests.conftest import ComplexConfig, SimpleConfig

from pyconfigr import ConfigBuilder
from pyconfigr.builder import _deep_merge
from pyconfigr.exceptions import (
    ConfigLoadError,
    ConfigNotFoundError,
    ConfigValidationError,
)


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
        """Test that get_raw_data() emits DeprecationWarning and returns
        the same result as peek().

        ``get_raw_data()`` is a deprecated alias for ``peek()`` as of v0.1.1.
        This test verifies both that the warning is emitted and that the
        return value is correct.

        Parameters
        ----------
        yaml_config_file : Path
            Fixture providing a temporary YAML config file.
        """
        builder = ConfigBuilder(ComplexConfig).from_file(yaml_config_file)

        with pytest.warns(DeprecationWarning, match="get_raw_data\\(\\) is deprecated"):
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


class TestConfigBuilderFromFile:
    """Tests for from_file extension and existence ordering."""

    def test_from_file_validates_extension_before_existence(
        self, temp_dir: Path
    ) -> None:
        """Test that extension is validated before checking file existence.

        A file with an unsupported extension that also does not exist should
        raise ValueError (unsupported extension), not ConfigNotFoundError
        (file missing).  The extension error is more actionable at development
        time.

        Parameters
        ----------
        temp_dir : Path
            Fixture providing a temporary directory.
        """
        missing_with_bad_ext = temp_dir / "config.xyz"
        # File does NOT exist — but extension is bad, so ValueError must come first

        with pytest.raises(ValueError, match="Unsupported file format"):
            ConfigBuilder(SimpleConfig).from_file(missing_with_bad_ext)

    def test_from_file_optional_bad_extension_still_raises(
        self, temp_dir: Path
    ) -> None:
        """Test that optional=True does not suppress unsupported-extension errors.

        ``optional`` silences missing-file errors only.  An unsupported extension
        is a programmer error and must always raise regardless of ``optional``.

        Parameters
        ----------
        temp_dir : Path
            Fixture providing a temporary directory.
        """
        missing_with_bad_ext = temp_dir / "config.xyz"

        with pytest.raises(ValueError, match="Unsupported file format"):
            ConfigBuilder(SimpleConfig).from_file(missing_with_bad_ext, optional=True)


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
        """Test error when file has unsupported extension.

        Extension is validated before existence check, so this raises
        ValueError even when the file exists.

        Parameters
        ----------
        temp_dir : Path
            Fixture providing a temporary directory.
        """
        unsupported_file = temp_dir / "config.unknown"
        unsupported_file.write_text("some content")

        builder = ConfigBuilder(SimpleConfig)

        with pytest.raises(ValueError, match="Unsupported file format"):
            builder.from_file(unsupported_file).build()

    def test_from_file_generic_exception_wrapping(self, temp_dir: Path) -> None:
        """Test that generic exceptions are wrapped in ConfigLoadError.

        Parameters
        ----------
        temp_dir : Path
            Fixture providing a temporary directory.
        """
        config_file = temp_dir / "config.json"
        config_file.write_text('{"debug": true}')

        builder = ConfigBuilder(SimpleConfig)

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
        """Test that ValueError from unsupported extension is propagated.

        Parameters
        ----------
        temp_dir : Path
            Fixture providing a temporary directory.
        """
        unsupported_file = temp_dir / "config.xyz"
        unsupported_file.write_text("content")

        builder = ConfigBuilder(SimpleConfig)

        with pytest.raises(ValueError):
            builder.from_file(unsupported_file).build()

    def test_from_file_propagates_config_load_error(self, temp_dir: Path) -> None:
        """Test that ConfigLoadError from loaders is propagated.

        Parameters
        ----------
        temp_dir : Path
            Fixture providing a temporary directory.
        """
        config_file = temp_dir / "config.json"
        config_file.write_text('{"debug": true}')

        builder = ConfigBuilder(SimpleConfig)

        with mock.patch("pyconfigr.builder.ConfigLoader.detect_and_load") as mock_load:
            mock_load.side_effect = ConfigLoadError("Parse error")

            with pytest.raises(ConfigLoadError, match="Parse error"):
                builder.from_file(config_file).build()


class TestConfigBuilderDeepMerge:
    """Test deep merge functionality.

    ``_deep_merge`` is a module-level function in ``pyconfigr.builder``.
    Tests import it directly to verify its logic in isolation, independently
    of ConfigBuilder construction.
    """

    def test_deep_merge_nested_dicts(self) -> None:
        """Test merging nested dictionaries."""
        target = {"nested": {"a": 1, "b": 2}}
        source = {"nested": {"b": 3, "c": 4}}

        _deep_merge(target, source)

        assert target["nested"]["a"] == 1
        assert target["nested"]["b"] == 3
        assert target["nested"]["c"] == 4

    def test_deep_merge_overwrites_non_dict(self) -> None:
        """Test that deep merge overwrites non-dict values."""
        target = {"value": "original"}
        source = {"value": "updated"}

        _deep_merge(target, source)

        assert target["value"] == "updated"

    def test_deep_merge_with_lists(self) -> None:
        """Test that lists are replaced, not merged.

        Lists represent complete values in config files (e.g. allowed_hosts)
        and must be replaced wholesale by a later source.
        """
        target = {"items": [1, 2, 3]}
        source = {"items": [4, 5]}

        _deep_merge(target, source)

        assert target["items"] == [4, 5]

    def test_deep_merge_with_none_values(self) -> None:
        """Test merging with None values."""
        target = {"key": "value"}
        source = {"key": None}

        _deep_merge(target, source)

        assert target["key"] is None

    def test_deep_merge_preserves_unmatched_keys(self) -> None:
        """Test that unmatched keys are preserved."""
        target = {"a": 1, "b": 2}
        source = {"c": 3}

        _deep_merge(target, source)

        assert target["a"] == 1
        assert target["b"] == 2
        assert target["c"] == 3

    def test_deep_merge_module_level_import(self) -> None:
        """Test that _deep_merge is importable and callable at module level.

        Confirms the function is accessible from pyconfigr.builder for any
        future sibling classes (e.g. RawConfigBuilder) that need to reuse it.
        """
        target: dict = {}
        _deep_merge(target, {"x": {"y": 1}})
        assert target == {"x": {"y": 1}}


class TestConfigBuilderSetMethod:
    """Test set method with dot notation."""

    def test_set_simple_key(self) -> None:
        """Test setting a simple key."""
        builder = ConfigBuilder(SimpleConfig)
        builder.set("app_name", "my_app")

        raw = builder.peek()
        assert raw["app_name"] == "my_app"

    def test_set_nested_key_with_dot_notation(self) -> None:
        """Test setting nested key using dot notation."""
        builder = ConfigBuilder(SimpleConfig)
        builder.set("database.host", "localhost")
        builder.set("database.port", 5432)

        raw = builder.peek()
        assert raw["database"]["host"] == "localhost"
        assert raw["database"]["port"] == 5432

    def test_set_deeply_nested_key(self) -> None:
        """Test setting deeply nested key."""
        builder = ConfigBuilder(SimpleConfig)
        builder.set("app.db.connection.host", "db.example.com")

        raw = builder.peek()
        assert raw["app"]["db"]["connection"]["host"] == "db.example.com"

    def test_set_overwrites_existing_value(self) -> None:
        """Test that set overwrites existing values."""
        builder = ConfigBuilder(SimpleConfig)
        builder.set("debug", False)
        builder.set("debug", True)

        raw = builder.peek()
        assert raw["debug"] is True

    def test_set_method_returns_self(self) -> None:
        """Test that set method returns self for chaining."""
        builder = ConfigBuilder(SimpleConfig)
        result = builder.set("key", "value")

        assert result is builder

    def test_set_raises_type_error_on_scalar_intermediate(self) -> None:
        """Test that set() raises TypeError with a clear message when a
        dot-notation path segment exists but is not a dict.

        The error message must include:
        - the full requested key path
        - the name of the offending intermediate segment
        - the actual type that was found
        """
        builder = ConfigBuilder(SimpleConfig)
        builder._data = {"database": "not-a-dict"}

        with pytest.raises(TypeError) as exc_info:
            builder.set("database.host", "localhost")

        message = str(exc_info.value)
        assert "database.host" in message  # full key path
        assert "database" in message  # offending segment
        assert "str" in message  # actual type found

    def test_set_raises_type_error_on_deeply_nested_scalar(self) -> None:
        """Test TypeError is raised at the correct depth for deep paths.

        Parameters
        ----------
        None
        """
        builder = ConfigBuilder(SimpleConfig)
        builder._data = {"a": {"b": "scalar"}}

        with pytest.raises(TypeError) as exc_info:
            builder.set("a.b.c", "value")

        message = str(exc_info.value)
        assert "a.b.c" in message
        assert "a.b" in message
        assert "str" in message


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
        """Test get_raw_data emits DeprecationWarning and returns a copy.

        Verifies that:
        - ``DeprecationWarning`` is emitted on every call
        - each call returns an independent copy (mutations do not bleed)
        - the returned data matches the builder's internal state

        Parameters
        ----------
        temp_dir : Path
            Fixture providing a temporary directory.
        """
        config_file = temp_dir / "config.json"
        config_file.write_text('{"port": 3000}')

        builder = ConfigBuilder(SimpleConfig).from_file(config_file)

        with pytest.warns(DeprecationWarning, match="get_raw_data\\(\\) is deprecated"):
            raw1 = builder.get_raw_data()

        with pytest.warns(DeprecationWarning):
            raw2 = builder.get_raw_data()

        assert raw1 == raw2
        assert raw1 is not raw2

        raw1["port"] = 9999

        with pytest.warns(DeprecationWarning):
            raw3 = builder.get_raw_data()

        assert raw3["port"] == 3000

    def test_peek_returns_copy(self, temp_dir: Path) -> None:
        """Test that peek() returns a copy equal to get_raw_data().

        ``peek()`` is the preferred name; ``get_raw_data()`` is its
        deprecated alias.  Both must return equal, independent copies.

        Parameters
        ----------
        temp_dir : Path
            Fixture providing a temporary directory.
        """
        config_file = temp_dir / "config.json"
        config_file.write_text('{"port": 4000}')

        builder = ConfigBuilder(SimpleConfig).from_file(config_file)

        peeked = builder.peek()

        with pytest.warns(DeprecationWarning):
            raw = builder.get_raw_data()

        assert peeked == raw
        assert peeked is not raw

    def test_peek_is_nondestructive(self, temp_dir: Path) -> None:
        """Test that mutating the dict returned by peek() does not affect
        the builder's internal state.

        Parameters
        ----------
        temp_dir : Path
            Fixture providing a temporary directory.
        """
        config_file = temp_dir / "config.json"
        config_file.write_text('{"port": 5000}')

        builder = ConfigBuilder(SimpleConfig).from_file(config_file)

        snapshot = builder.peek()
        snapshot["port"] = 99999

        assert builder.peek()["port"] == 5000
