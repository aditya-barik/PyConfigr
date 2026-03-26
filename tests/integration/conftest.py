"""
Shared fixtures and Pydantic schemas for the integration test suite.

All integration tests operate against realistic schemas that represent
actual application configuration — not minimal stubs.
"""

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import pytest
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Pydantic schemas — reused across all integration test files
# ---------------------------------------------------------------------------


class ServerConfig(BaseModel):
    """HTTP server configuration."""

    host: str = "0.0.0.0"
    port: int = Field(default=8000, ge=1, le=65535)
    workers: int = Field(default=4, ge=1)
    debug: bool = False


class DatabaseConfig(BaseModel):
    """Relational database configuration."""

    host: str = "localhost"
    port: int = Field(default=5432, ge=1, le=65535)
    name: str
    username: str
    password: str


class CacheConfig(BaseModel):
    """Cache / Redis configuration."""

    host: str = "localhost"
    port: int = Field(default=6379, ge=1, le=65535)
    ttl_seconds: int = Field(default=3600, ge=0)
    enabled: bool = True


class AllTypesConfig(BaseModel):
    """Schema that exercises every primitive type Pydantic supports."""

    name: str
    count: int
    ratio: float
    active: bool
    tags: list[str]
    metadata: dict[str, Any]
    nullable: str | None = None


class AppConfig(BaseModel):
    """Top-level application config — the primary schema for multi-source tests."""

    app_name: str = "myapp"
    version: str = "0.1.0"
    server: ServerConfig = Field(default_factory=ServerConfig)
    database: DatabaseConfig
    cache: CacheConfig = Field(default_factory=CacheConfig)


class SimpleConfig(BaseModel):
    """Minimal schema for tests that do not need nested structure."""

    name: str = "default"
    debug: bool = False
    port: int = 8000
    api_key: str | None = None


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def cfg_dir(tmp_path: Path) -> Path:
    """Return a temporary directory for config files."""
    return tmp_path


@contextmanager
def env_vars(**kwargs: str):
    """Context manager that sets env vars and cleans them up on exit."""
    set_keys = []
    for key, value in kwargs.items():
        os.environ[key] = value
        set_keys.append(key)
    try:
        yield
    finally:
        for key in set_keys:
            os.environ.pop(key, None)
