"""Test suite for environment variable loader."""

import os

from pyconfigr.loaders import ENVLoader


class TestENVLoader:
    """Tests for ENVLoader class."""

    def test_load_env_with_prefix(self) -> None:
        """Test loading environment variables with prefix.

        Sets test environment variables with TESTAPP_ prefix and verifies
        they are loaded correctly with type parsing.
        """
        os.environ["TESTAPP_DEBUG"] = "true"
        os.environ["TESTAPP_PORT"] = "9000"
        os.environ["TESTAPP_DATABASE_HOST"] = "localhost"

        try:
            loader = ENVLoader()
            config = loader(prefix="TESTAPP_")

            assert config["debug"] is True
            assert config["port"] == 9000
            assert config["database_host"] == "localhost"
        finally:
            del os.environ["TESTAPP_DEBUG"]
            del os.environ["TESTAPP_PORT"]
            del os.environ["TESTAPP_DATABASE_HOST"]

    def test_load_env_without_prefix(self) -> None:
        """Test loading all environment variables.

        Verifies that environment variables can be loaded without
        requiring a specific prefix.
        """
        os.environ["PYCONFIGR_TEST_VAR"] = "test_value"

        try:
            loader = ENVLoader()
            config = loader()

            assert "pyconfigr_test_var" in config
            assert config["pyconfigr_test_var"] == "test_value"
        finally:
            del os.environ["PYCONFIGR_TEST_VAR"]

    def test_env_no_strip_prefix(self) -> None:
        """Test keeping prefix in keys.

        Verifies that when strip_prefix=False, the prefix is retained
        in the configuration keys.
        """
        os.environ["APP_DEBUG"] = "true"

        try:
            loader = ENVLoader()
            config = loader(prefix="APP_", strip_prefix=False)

            assert "app_debug" in config
            assert config["app_debug"] is True
        finally:
            del os.environ["APP_DEBUG"]

    def test_env_no_lowercase(self) -> None:
        """Test keeping original case in keys.

        Verifies that when lowercase=False, the original case of
        environment variable names is preserved.
        """
        os.environ["DEBUG"] = "true"

        try:
            loader = ENVLoader()
            config = loader(lowercase=False)

            assert "DEBUG" in config
        finally:
            del os.environ["DEBUG"]

    def test_env_value_parsing(self) -> None:
        """Test intelligent value type parsing.

        Verifies that environment variable values are parsed into
        appropriate Python types (bool, int, float, None, str).
        """
        os.environ["TEST_BOOL_TRUE"] = "true"
        os.environ["TEST_BOOL_FALSE"] = "false"
        os.environ["TEST_INT"] = "42"
        os.environ["TEST_FLOAT"] = "3.14"
        os.environ["TEST_NONE"] = "null"
        os.environ["TEST_STRING"] = "hello"

        try:
            loader = ENVLoader()
            config = loader(prefix="TEST_")

            assert config["bool_true"] is True
            assert config["bool_false"] is False
            assert config["int"] == 42
            assert config["float"] == 3.14
            assert config["none"] is None
            assert config["string"] == "hello"
        finally:
            for key in [
                "TEST_BOOL_TRUE",
                "TEST_BOOL_FALSE",
                "TEST_INT",
                "TEST_FLOAT",
                "TEST_NONE",
                "TEST_STRING",
            ]:
                del os.environ[key]
