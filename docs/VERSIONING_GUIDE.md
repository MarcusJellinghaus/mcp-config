# GitHub Tag-Based Versioning Guide

This guide explains how to implement automated versioning using Git tags in Python projects with `setuptools-scm`.

## Design Decisions

This implementation is based on the following decisions:

### 1. **Tag Format: No "v" Prefix**
- **Decision:** Use `0.1.0` instead of `v0.1.0`
- **Rationale:** Simpler, cleaner, and directly usable as Python version string
- **Example:** `git tag 0.1.0`

### 2. **CLI Version Display**
- **Decision:** Add `--version` flag to show current version
- **Rationale:** Standard CLI convention for showing version information
- **Example:** `mcp-config --version` → `mcp-config 0.1.0`

### 3. **Fallback Version**
- **Decision:** Use `0.1.0.dev0` when no tags exist
- **Rationale:** Clearly indicates development state before first release
- **Example:** On fresh clone without tags: `0.1.0.dev0`

### 4. **Implementation Tool**
- **Decision:** Use `setuptools-scm` (not manual implementation)
- **Rationale:**
  - Industry standard
  - Automatic handling of development versions
  - Minimal maintenance
  - Handles edge cases automatically

## How It Works

`setuptools-scm` automatically determines your package version from Git:

| Git State | Version Output | Example |
|-----------|---------------|---------|
| On tagged commit | Exact tag version | `0.1.0` |
| After tag with changes | Next dev version | `0.1.1.dev0` |
| No tags exist | Fallback version | `0.1.0.dev0` |
| N commits after tag | Dev with distance | `0.1.1.dev3` |

## Implementation Steps

### Step 1: Update `pyproject.toml` Project Section

Remove the hardcoded version and make it dynamic:

```toml
[project]
name = "your-project-name"
dynamic = ["version"]  # ← Add this, remove: version = "x.y.z"
authors = [
    {name = "Your Name", email = "your@email.com"},
]
# ... rest of your configuration
```

### Step 2: Add setuptools-scm to Build Dependencies

Update the `[build-system]` section:

```toml
[build-system]
requires = ["setuptools>=61.0", "setuptools-scm>=8.0"]  # ← Add setuptools-scm
build-backend = "setuptools.build_meta"
```

### Step 3: Configure setuptools-scm

Add this section at the end of `pyproject.toml`:

```toml
[tool.setuptools_scm]
version_scheme = "guess-next-dev"
local_scheme = "no-local-version"
tag_regex = "^(?P<prefix>)?(?P<version>[0-9]+\\.[0-9]+\\.[0-9]+)(?P<suffix>.*)?$"
fallback_version = "0.1.0.dev0"
```

**Configuration explanation:**
- `version_scheme = "guess-next-dev"`: Automatically increments patch version for dev builds
- `local_scheme = "no-local-version"`: Cleaner version strings (no git hash suffix)
- `tag_regex`: Accepts tags with or without "v" prefix (but we'll use without)
- `fallback_version`: Used when no tags exist in the repository

### Step 4: Add `__version__` to Your Package

In your main package's `__init__.py` (e.g., `src/your_package/__init__.py`):

```python
# Version - managed by setuptools-scm
try:
    from importlib.metadata import version
    __version__ = version("your-package-name")  # ← Use your actual package name
except Exception:
    __version__ = "0.1.0.dev0"
```

**Important:** Replace `"your-package-name"` with the exact name from `pyproject.toml` `[project]` section.

### Step 5: Add `--version` Flag to CLI (Optional)

If you have a CLI application, add version display to your argument parser.

In your CLI setup file (e.g., `cli_utils.py` or `main.py`):

```python
import argparse
from your_package import __version__

def create_parser():
    parser = argparse.ArgumentParser(
        prog="your-cli",
        description="Your CLI description",
    )

    # Add version argument
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    # ... rest of your parser setup
    return parser
```

### Step 6: Create Your First Tag and Commit

```bash
# Stage the changes
git add pyproject.toml src/your_package/__init__.py

# Commit the versioning implementation
git commit -m "Add GitHub tag-based versioning with setuptools-scm

- Remove hardcoded version from pyproject.toml
- Add setuptools-scm for dynamic versioning from git tags
- Configure tag format without 'v' prefix
- Set fallback version to 0.1.0.dev0 when no tags exist
- Add __version__ variable to package __init__.py
- Add --version CLI flag to display current version

Version is now automatically managed through git tags."

# Create the first version tag (no 'v' prefix)
git tag 0.1.0

# Push to remote
git push origin your-branch
git push origin 0.1.0
```

### Step 7: Test the Implementation

```bash
# Install in editable mode
pip install -e .

# Test CLI version display (if applicable)
your-cli --version
# Expected output: your-cli 0.1.0

# Test programmatic version access
python -c "from your_package import __version__; print(__version__)"
# Expected output: 0.1.0

# Test with no tags (optional - in a test clone)
git clone <repo-url> test-clone
cd test-clone
pip install -e .
your-cli --version
# Expected output: your-cli 0.1.0.dev0
```

## Usage: Creating New Releases

### For Patch Releases (Bug Fixes)

```bash
# Make your bug fixes and commit them
git add .
git commit -m "Fix bug in feature X"

# Tag the new version
git tag 0.1.1

# Push
git push origin main  # or your branch
git push origin 0.1.1

# Reinstall to see new version
pip install -e .
your-cli --version  # Shows: your-cli 0.1.1
```

### For Minor Releases (New Features)

```bash
# Make your changes and commit them
git add .
git commit -m "Add new feature Y"

# Tag the new version
git tag 0.2.0

# Push
git push origin main
git push origin 0.2.0
```

### For Major Releases (Breaking Changes)

```bash
# Make your changes and commit them
git add .
git commit -m "BREAKING: Change API interface"

# Tag the new version
git tag 1.0.0

# Push
git push origin main
git push origin 1.0.0
```

## Development Versions

Between releases, setuptools-scm automatically generates development versions:

```bash
# After tagging 0.1.0, make some changes
git commit -m "Work in progress"

# Check version
pip install -e .
your-cli --version
# Output: your-cli 0.1.1.dev1

# After more commits
git commit -m "More work"
your-cli --version  # (after pip install -e .)
# Output: your-cli 0.1.1.dev2
```

## Semantic Versioning

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR** version (1.0.0 → 2.0.0): Incompatible API changes
- **MINOR** version (0.1.0 → 0.2.0): Add functionality (backwards-compatible)
- **PATCH** version (0.1.0 → 0.1.1): Bug fixes (backwards-compatible)

## Troubleshooting

### Version shows as `0.1.0.dev0` even with tags

**Cause:** Package not reinstalled after tagging

**Solution:**
```bash
pip install -e . --force-reinstall --no-deps
```

### Version shows with git hash suffix (e.g., `0.1.0+g1234567`)

**Cause:** `local_scheme` not set correctly

**Solution:** Verify `pyproject.toml` has:
```toml
[tool.setuptools_scm]
local_scheme = "no-local-version"
```

### CLI shows old version after tagging

**Cause:** Package not reinstalled

**Solution:**
```bash
pip install -e .
```

### ImportError: No module named 'setuptools_scm'

**Cause:** Build dependency not installed

**Solution:**
```bash
pip install setuptools-scm>=8.0
```

## Integration with CI/CD

### GitHub Actions

Your CI/CD workflow automatically gets the version from tags:

```yaml
name: Build and Publish

on:
  push:
    tags:
      - '[0-9]+.[0-9]+.[0-9]+'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # ← Important: fetch all history and tags

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Build package
        run: |
          pip install build
          python -m build

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}
```

**Key point:** Use `fetch-depth: 0` to ensure all tags are available.

## Benefits

✅ **Single Source of Truth:** Git tags are the only version source
✅ **No Manual Updates:** No need to edit version numbers in code
✅ **Automatic Dev Versions:** Clear distinction between releases and development
✅ **Standard Practice:** Uses industry-standard tool (setuptools-scm)
✅ **CI/CD Friendly:** Automatic version detection in pipelines
✅ **Semantic Versioning:** Easy to follow SemVer conventions

## Examples from This Project

This project (`mcp-config`) uses this exact approach:

- **Configuration:** See `pyproject.toml:3` (dynamic version) and `pyproject.toml:106-110` (setuptools-scm config)
- **Version Variable:** See `src/mcp_config/__init__.py:9-14`
- **CLI Integration:** See `src/mcp_config/cli_utils.py:227-232`
- **Current Tag:** `0.1.0` (without "v" prefix)

Test it yourself:
```bash
mcp-config --version
# Output: mcp-config 0.1.0
```

## References

- [setuptools-scm Documentation](https://setuptools-scm.readthedocs.io/)
- [Semantic Versioning Specification](https://semver.org/)
- [PEP 440 – Version Identification](https://peps.python.org/pep-0440/)

---

**Last Updated:** 2025-11-05
**Project:** mcp-config
**Author:** Marcus Jellinghaus
