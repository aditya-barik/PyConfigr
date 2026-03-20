# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### 🐛 Bug Fixes

- **`from_file` extension ordering** (`builder.py`) — Extension is now validated *before* checking file existence. Writing `.from_file("config.xyz")` before the file exists now raises `ValueError: Unsupported file format` immediately, not a misleading `ConfigNotFoundError` after the file is created.
- **`set()` error message** (`builder.py`) — Calling `set()` with a dot-notation path where an intermediate segment is already a scalar now raises `TypeError` with a message naming the full key path, the offending segment, its actual type, and a concrete resolution suggestion.
- **`ENVLoader` double-underscore nesting** (`loaders/env.py`) — Double underscores in environment variable names are now expanded into nested dicts: `MYAPP__DATABASE__HOST=localhost` → `{"database": {"host": "localhost"}}`. Single underscores remain part of the key name. Pass `nested=False` to opt out.
- **`ENVLoader` integer parsing** (`loaders/env.py`) — Integer values such as `"42"` were incorrectly parsed as `42.0` (float) because `float()` was attempted before `int()`. Parse order corrected.
- **`ConfigLoader` test isolation** (`loaders/manager.py`) — `ConfigLoader.reset()` restores the registries to their post-import state, preventing tests that register custom loaders from polluting subsequent tests.
- **Broken documentation examples** (`__init__.py`) — Module docstring examples corrected to use `from_file()` consistently. References to non-existent `from_yaml()` and `from_json()` methods removed.

### ✨ New Features

- **`ConfigBuilder.peek()`** (`builder.py`) — Returns a copy of the current assembled data without triggering Pydantic validation. Useful for inspecting merged state mid-chain. `get_raw_data()` retained as a deprecated alias that emits `DeprecationWarning`.
- **`from_env(nested=True)` parameter** (`builder.py`, `loaders/env.py`) — Controls whether double-underscore keys are expanded into nested dicts. Defaults to `True`.
- **`ConfigLoader.validate_extension()`** (`loaders/manager.py`) — Validates a file extension against registered loaders and returns the loader-type name. Extracted from `detect_and_load` for direct use.
- **`ConfigLoader.reset()`** (`loaders/manager.py`) — Restores registries to built-in state. Intended for test teardown after custom loader registration.

### 🔄 Changed

- **`_deep_merge` moved to module level** (`builder.py`) — Was an instance method that never used `self`. Now a module-level function importable by future sibling classes.
- **`ConfigBuilder._config_class` made private** (`builder.py`) — Attribute renamed from `config_class` to `_config_class`. It was never part of the documented public API. *Migration: change `builder.config_class` to `builder._config_class`.*
- **`from_env()` keyword-only parameters** (`builder.py`) — `lowercase`, `strip_prefix`, and `nested` are now keyword-only. *Migration: `from_env("P", True, False)` → `from_env("P", lowercase=True, strip_prefix=False)`.*
- **`get_raw_data()` emits `DeprecationWarning`** (`builder.py`) — Now warns on every call with `stacklevel=2`. Use `peek()` instead.
- **`list_loaders()` and `list_extensions()` return sorted results** (`loaders/manager.py`) — Deterministic output regardless of registration order.

### 🤖 CI/CD

- Added `pr-lifecycle.yml` — 3-job workflow managing PR labelling, issue sync, and closure handling
- Added `sync-labels.yml` — automated label sync triggered on config change or manual dispatch
- Added `.github/config/pr-labeling.json` for config-driven branch conventions
- Added `.github/config/labels.json` as single versioned source of truth for all labels
- Added `CONTRIBUTING.md`
- Updated `actions/checkout` to `@v5` across all workflows

---

## [0.1.0] - 2026-02-06

### 🎉 Initial Release

PyConfigr is a lightweight, type-safe configuration management library designed for modern Python applications. This initial release brings together multiple years of configuration management best practices into a simple, elegant API.

### ✨ Core Features Added

#### Multi-Format Configuration Loading
- **YAML support** via PyYAML for human-readable configuration files
- **JSON support** using Python's built-in `json` module
- **TOML support** via tomllib (Python 3.11+) or tomli (Python < 3.11)
- **Environment variable loading** with customizable prefix support
- **Dictionary-based configuration** for runtime overrides
- **Automatic format detection** based on file extensions

#### ConfigBuilder Class
- **Fluent API** for chainable, readable configuration building
  - `.from_file()` - Load from YAML, JSON, or TOML files
  - `.from_env()` - Load from environment variables with prefix
  - `.from_dict()` - Load from Python dictionaries
  - `.set()` - Set individual configuration values
  - `.build()` - Validate and build final configuration
- **Generic type support** (`ConfigBuilder[T]`) for proper type inference
- **Full type safety** with MyPy strict mode compliance
- **Method chaining** for elegant configuration composition

#### Robust Validation & Error Handling
- **Pydantic integration** for powerful, declarative validation
- **Custom exception hierarchy**:
  - `ConfigError` - Base exception for all configuration errors
  - `ConfigLoadError` - Errors during configuration file loading
  - `ConfigNotFoundError` - Configuration file not found
  - `ConfigValidationError` - Pydantic validation errors with detailed context
- **Detailed error messages** that help developers quickly identify and fix issues
- **Graceful fallbacks** for optional configuration files

#### Loader Infrastructure
- **Abstract `BaseConfigLoader`** for future extensibility
- **Environment variable loader** with prefix support and nested key handling
- **Format auto-detection** based on file extensions
- **Loader manager** for intelligent format detection and caching
- **Error recovery** with comprehensive exception handling

#### Type Safety & Developer Experience
- **Full type hints** throughout the entire codebase
- **Generic `ConfigBuilder[T]`** for type-safe configuration without casting
- **MyPy strict mode** compliance with zero type errors
- **Python 3.10+ syntax** including modern type union (`|`) syntax
- **IDE autocomplete support** for configuration fields

### 📊 Quality & Testing

#### Comprehensive Test Suite
- **105 tests** covering all core functionality
- **~98% code coverage** (only unavoidable tomli import error lines uncovered)
- **Test organization** matching source code structure
  - `tests/loaders/` - Individual loader testing
  - `tests/test_builder.py` - ConfigBuilder and fluent API testing
  - `tests/test_exceptions.py` - Exception handling and error cases

#### Type Checking & Linting
- **MyPy strict mode** - Zero type errors
- **Ruff** with comprehensive linting rules
- **Code formatting** with automatic style enforcement
- **Branch coverage** enabled for thorough testing

#### CI/CD Infrastructure
- **GitHub Actions workflow** for multi-version testing
- **Matrix strategy** testing Python 3.10, 3.11, 3.12, 3.13, and 3.14
- **Automated test reporting** with markdown and JSON outputs
- **Coverage tracking** with detailed reports per Python version
- **Artifact retention** for build verification

### 📚 Documentation

#### README & Examples
- **Comprehensive README** with quick start guide
- **Multiple usage patterns** demonstrating real-world scenarios
- **Best practices guide** for secure and maintainable configuration
- **Security guidelines** for handling sensitive data
- **Example scripts** in `scripts/` directory showing all features

#### Configuration Examples
- **Basic YAML loading** with type validation
- **Multiple source merging** with priority handling
- **Nested configuration structures** using Pydantic models
- **Environment variable overrides** with prefix support
- **Production-like scenarios** for API services and applications

#### Project Documentation
- **CHANGELOG** tracking all changes
- **Python version testing plan** with multi-version strategies
- **Inline code documentation** with docstrings on all public APIs
- **Type hints** serving as inline API documentation

### 🏗️ Project Structure

```
PyConfigr/
├── .github/                      # GitHub configuration
│   └── workflows/                # CI/CD workflows
├── scripts/                      # Integration test scripts
├── src/pyconfigr/                # Main package
│   ├── __init__.py               # Public API exports
│   ├── builder.py                # ConfigBuilder[T] class
│   ├── exceptions.py             # Custom exceptions
│   ├── py.typed                  # Type hints marker (PEP 561)
│   └── loaders/                  # Loader implementations
│       ├── __init__.py
│       ├── base.py               # BaseConfigLoader ABC
│       ├── manager.py            # LoaderManager
│       ├── env.py                # Environment variable loader
│       ├── json.py               # JSON file loader
│       ├── toml.py               # TOML file loader
│       └── yaml.py               # YAML file loader
├── tests/                        # Test suite (105 tests)
├── CHANGELOG.md                  # This file
├── LICENSE                       # MIT License
├── README.md                     # User documentation
├── pyproject.toml                # Project configuration
└── .gitignore                    # Ignore-list for version control

```

### 🧠 Design Philosophy

PyConfigr is built on several key principles:

1. **Simplicity over magic** – Explicit configuration loading beats implicit auto-discovery
2. **Type safety first** – Full type hints enable IDE support and catch errors early
3. **Standards compliance** – Follows PEP 440 (versioning) and PEP 621 (project metadata)
4. **Minimal dependencies** – Only Pydantic required; YAML and TOML are optional
5. **Fail fast** – Validation errors are raised at build time, not runtime
6. **Priority-based merging** – Clear, predictable configuration precedence

### 🔄 Configuration Priority

PyConfigr implements a simple, intuitive configuration priority system:

```
File → Environment Variables → Dict → Explicit .set() method
↑                                     ↑
Low                                   High
```

This matches how most systems expect configuration to work and makes it easy to understand which source will win in any given situation.

### 📦 Dependencies

**Core (required):**
- `pydantic >= 2.0.0` - Configuration validation and type checking
- `pyyaml >= 6.0` - YAML file support

**Optional:**
- `tomli >= 2.0.0` - TOML support (Python < 3.11; built-in for 3.11+)

**Development:**
- `pytest >= 9.0.0` - Testing framework
- `pytest-cov >= 7.0.0` - Coverage reporting
- `mypy >= 1.10.0` - Static type checking
- `ruff >= 0.4.0` - Linting and formatting

### ✅ Known Limitations

- **YAML features** - Limited to features supported by PyYAML
- **Circular references** - Not supported in configuration validation (expected for configs)
- **Very large files** - Performance not optimized for multi-hundred-MB configuration files
- **Real-time reloading** - Configuration is loaded once at startup (planned for future)

### 🎯 Version Management

- **Version**: 0.1.0 (Initial release)
- **Python compatibility**: 3.10, 3.11, 3.12, 3.13, 3.14
- **API stability**: This is an early release; minor breaking changes may occur before v1.0.0
- **Versioning**: Follows [Semantic Versioning](https://semver.org/) (MAJOR.MINOR.PATCH)

### 🙏 Thanks

Special thanks to:
- The **Pydantic** team for an exceptional validation library
- The **PyYAML** and **tomli** maintainers for format support
- All contributors and early adopters providing feedback

---

## Comparison with Other Tools

If you're currently using alternative tools:
- **python-dotenv + manual merging** - PyConfigr provides cleaner API and type safety
- **configparser** - PyConfigr supports multiple formats with validation
- **hydra** - PyConfigr is simpler for most application needs
- **dynaconf** - PyConfigr has zero-configuration setup, no need for environment prefixes

Each has different strengths. Choose based on your project's specific needs.

---

[0.1.0]: https://github.com/aditya-barik/PyConfigr/releases/tag/v0.1.0
