# pyproject.toml Update Summary

## Overview
Updated the `pyproject.toml` file to properly separate runtime dependencies from development dependencies according to Python packaging best practices.

## Changes Made

### 1. Dependency Reorganization
**Moved from main dependencies to dev optional-dependencies:**
- `pylint>=3.3.3`
- `pytest>=8.3.5`
- `pytest-json-report>=1.5.0`
- `pytest-asyncio>=0.25.3`
- `mypy>=1.9.0`

**Kept as runtime dependencies:**
- `pathspec>=0.12.1`
- `mcp>=1.3.0`
- `mcp[server]>=1.3.0`
- `mcp[cli]>=1.3.0`
- `structlog>=24.5.0`
- `python-json-logger>=3.2.1`

### 2. Development Dependencies Structure
The `[project.optional-dependencies]` dev section now includes:
- Code formatting: `black>=24.10.0`, `isort>=5.13.2`
- Testing: `pytest>=8.3.5`, `pytest-json-report>=1.5.0`, `pytest-asyncio>=0.25.3`
- Code quality: `pylint>=3.3.3`, `mypy>=1.9.0`

## Benefits

### Production Benefits
- Lighter production installs (no testing/linting tools)
- Faster installation in production environments
- Cleaner dependency resolution

### Development Benefits
- Single command installation: `pip install -e ".[dev]"`
- All required development tools included
- Maintains strict mypy configuration

### Project Structure Compliance
- Aligns with Python 3.11+ guidelines
- Follows DRY principle for dependency management
- Supports the established `src/` and `tests/` folder structure
- Compatible with the quality assurance process (pylint → pytest → mypy)

## Installation Commands

### For Production
```bash
pip install .
```

### For Development
```bash
pip install -e ".[dev]"
```

## Tool Configurations Preserved
- mypy strict settings maintained
- pytest configuration with asyncio support
- black and isort formatting settings
- All custom markers and paths preserved

## Next Steps
A new start is required to use the updated pyproject.toml configuration.
