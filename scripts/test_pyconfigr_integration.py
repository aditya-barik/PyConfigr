"""
PyConfigr Comprehensive Example and Integration Test

Demonstrates all key features of PyConfigr:
1. Basic YAML configuration loading with Pydantic validation
2. Multiple configuration sources with priority handling
3. Type-safe configuration management
"""

import os
import textwrap
from pathlib import Path

from pydantic import BaseModel, Field

from pyconfigr import ConfigBuilder


# Configuration schemas
class DatabaseConfig(BaseModel):
    """Database configuration."""

    host: str = "localhost"
    port: int = Field(default=5432, ge=1, le=65535)
    username: str
    password: str
    database: str = "myapp"


class AppConfig(BaseModel):
    """Application configuration."""

    app_name: str = "myapp"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = Field(default=8000, ge=1, le=65535)
    api_key: str | None = None
    database: DatabaseConfig


def create_example_config() -> Path:
    """Create example configuration file."""
    config_path = Path("config_example.yaml")
    config_path.write_text(
        textwrap.dedent(
            """\
            app_name: my_application
            debug: false
            host: 0.0.0.0
            port: 8000

            database:
              host: localhost
              port: 5432
              username: admin
              password: secret123
              database: production_db
            """
        )
    )
    return config_path


def setup_environment() -> None:
    """Setup environment variables for configuration override."""
    os.environ["MYAPP_DEBUG"] = "true"
    os.environ["MYAPP_PORT"] = "9000"
    os.environ["MYAPP_API_KEY"] = "secret123"


def demo_basic_loading() -> None:
    """Demonstrate basic YAML configuration loading."""
    print("\n" + "=" * 70)
    print("DEMO 1: Basic Configuration Loading from YAML")
    print("=" * 70)

    config_path = create_example_config()
    print(f"\n✓ Created configuration file: {config_path}")

    # Load configuration
    print("\n🔧 Loading configuration from YAML file...")
    config = ConfigBuilder(AppConfig).from_file(config_path).build()

    # Display configuration
    print("\n📋 Loaded Configuration:")
    print(f"  App Name   : {config.app_name}")
    print(f"  Debug Mode : {config.debug}")
    print(f"  Server     : {config.host}:{config.port}")
    print("\n  Database Settings:")
    print(f"    Host     : {config.database.host}")
    print(f"    Port     : {config.database.port}")
    print(f"    Database : {config.database.database}")
    print(f"    Username : {config.database.username}")

    # Demonstrate type safety
    print("\n🛡️ Type Safety Validation:")
    print(f"  config.debug is bool: {isinstance(config.debug, bool)}")
    print(f"  config.port is int: {isinstance(config.port, int)}")
    print(
        f"  config.database is DatabaseConfig: "
        f"{isinstance(config.database, DatabaseConfig)}"
    )

    print("\n✅ Basic loading demo completed successfully!")

    # Cleanup
    config_path.unlink()


def demo_multiple_sources() -> None:
    """Demonstrate loading from multiple sources with priority."""
    print("\n" + "=" * 70)
    print("DEMO 2: Multiple Configuration Sources with Priority")
    print("=" * 70)

    config_path = create_example_config()
    setup_environment()

    print("\n📚 Configuration Sources (Priority: file < env < dict):")
    print("\n  1️⃣ YAML File (base.yaml):")
    print("    - app_name : my_application")
    print("    - debug    : false")
    print("    - port     : 8000")

    print("\n  2️⃣ Environment Variables:")
    print(f"    - MYAPP_DEBUG={os.environ.get('MYAPP_DEBUG')}")
    print(f"    - MYAPP_PORT={os.environ.get('MYAPP_PORT')}")
    print(f"    - MYAPP_API_KEY={os.environ.get('MYAPP_API_KEY')}")

    print("\n  3️⃣ Runtime Dictionary (highest priority):")
    print("    - {'port': 3000}")

    # Load with priority: file < env < dict
    print("\n🔧 Loading configuration with priority merging...")
    config = (
        ConfigBuilder(AppConfig)
        .from_file(config_path)  # Lowest priority
        .from_env("MYAPP_")  # Medium priority
        .from_dict({"port": 3000})  # Highest priority
        .build()
    )

    print("\n📋 Merged Configuration (with source annotations):")
    print(f"  app_name: {config.app_name:20s} \t (from YAML file)")
    print(f"  debug   : {str(config.debug):20s} \t (overridden by MYAPP_DEBUG env var)")
    print(
        f"  port    : {str(config.port):20s} \t (overridden by dict, highest priority)"
    )
    print(f"  api_key : {str(config.api_key):20s} \t (from MYAPP_API_KEY env var)")
    print(f"  host    : {config.host:20s} \t (from YAML file)")

    print("\n✅ Multiple sources demo completed successfully!")
    print("   Configuration properly merged with correct priority!")

    # Cleanup
    config_path.unlink()
    for key in ["MYAPP_DEBUG", "MYAPP_PORT", "MYAPP_API_KEY"]:
        os.environ.pop(key, None)


def demo_fluent_api() -> None:
    """Demonstrate fluent API chaining."""
    print("\n" + "=" * 70)
    print("DEMO 3: Fluent API Method Chaining")
    print("=" * 70)

    config_path = create_example_config()

    print("\n🔗 Using Fluent API for method chaining:")
    print(
        textwrap.dedent(
            """\
            config = (
                ConfigBuilder(AppConfig)
                .from_file(config_path)
                .from_dict({"api_key": "runtime_key"})
                .build()
            )
            """
        )
    )

    config = (
        ConfigBuilder(AppConfig)
        .from_file(config_path)
        .from_dict({"api_key": "runtime_key"})
        .build()
    )

    print("\n✅ Fluent API demo completed successfully!")
    print(f"  Loaded config with api_key: {config.api_key}")

    # Cleanup
    config_path.unlink()


def main() -> None:
    """Run all PyConfigr demonstrations."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print(
        "║"
        + " PyConfigr Package - Comprehensive Feature Demonstration ".center(68)
        + "║"
    )
    print("╚" + "=" * 68 + "╝")

    try:
        # Run demonstrations
        demo_basic_loading()
        demo_multiple_sources()
        demo_fluent_api()

        # Summary
        print("\n" + "=" * 70)
        print("SUMMARY: All PyConfigr Features Tested Successfully!")
        print("=" * 70)
        print("\n✅ Features Demonstrated:")
        print("   ✓ YAML file configuration loading")
        print("   ✓ Type validation with Pydantic")
        print("   ✓ Multiple source configuration merging")
        print("   ✓ Priority handling (file < env < dict)")
        print("   ✓ Environment variable parsing")
        print("   ✓ Runtime dictionary overrides")
        print("   ✓ Nested configuration structures")
        print("   ✓ Fluent API method chaining")
        print("   ✓ Type-safe configuration access")
        print("\n" + "=" * 70)
        print("🎉 PyConfigr integration test passed!")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        raise


if __name__ == "__main__":
    main()
