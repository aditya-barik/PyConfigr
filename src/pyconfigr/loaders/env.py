"""Environment variable configuration loader."""

import os
from typing import Any

from .base import BaseLoader


class ENVLoader(BaseLoader):
    """
    Load configuration from environment variables.

    Provides flexible filtering by prefix, optional key normalization,
    and intelligent value parsing (booleans, numbers, None, strings).

    Examples
    --------
    >>> loader = ENVLoader()
    >>> # With MYAPP_DEBUG=true, MYAPP_PORT=8000
    >>> config = loader(prefix="MYAPP_")
    >>> config
    {'debug': True, 'port': 8000}

    >>> # Without stripping prefix
    >>> config = loader(prefix="MYAPP_", strip_prefix=False)
    >>> config
    {'myapp_debug': True, 'myapp_port': 8000}

    >>> # No prefix filtering
    >>> config = loader()
    >>> # Returns all environment variables with parsed values
    """

    def __call__(
        self, prefix: str = "", lowercase: bool = True, strip_prefix: bool = True
    ) -> dict[str, Any]:
        """
        Load configuration from environment variables.

        Parameters
        ----------
        prefix : str, optional
            Only load variables starting with this prefix (e.g., "MYAPP_")
            Default is empty string.
        lowercase : bool, optional
            Convert keys to lowercase. Default is True.
        strip_prefix : bool, optional
            Remove prefix from keys. Default is True.

        Returns
        -------
        dict[str, Any]
            Dictionary containing configuration from environment variables.
        """
        config: dict[str, Any] = {}

        for key, value in os.environ.items():
            # Filter by prefix if specified
            if prefix and not key.startswith(prefix):
                continue

            # Process the key
            config_key = key
            if strip_prefix and prefix:
                config_key = key[len(prefix) :]
            if lowercase:
                config_key = config_key.lower()

            # Parse value to appropriate Python type
            config[config_key] = self._parse_value(value)

        return config

    @staticmethod
    def _parse_value(value: str) -> Any:
        """
        Parse string value to appropriate Python type.

        Handles booleans ("true", "false", "yes", "no", "1", "0", "on", "off"),
        integers ("123"), floats ("123.45"), None ("null", "none", ""),
        and strings (everything else).

        Parameters
        ----------
        value : str
            String value to parse.

        Returns
        -------
        Any
            Parsed value with appropriate type.
        """
        # Handle boolean
        if value.lower() in ("true", "yes", "1", "on"):
            return True
        if value.lower() in ("false", "no", "0", "off"):
            return False

        # Handle None
        if value.lower() in ("null", "none", ""):
            return None

        # Try integer
        try:
            return int(value)
        except ValueError:
            pass

        # Try float
        try:
            return float(value)
        except ValueError:
            pass

        # Return as string
        return value
