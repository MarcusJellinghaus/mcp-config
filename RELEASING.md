# Release Process

This document describes how to create releases for `mcp-config`.

## Overview

`mcp-config` uses **git tags** for versioning via `setuptools-scm`. The version is automatically derived from git tags following [Semantic Versioning](https://semver.org/).

## Version Format

- **Stable releases**: `X.Y.Z` (e.g., `0.1.0`, `1.2.3`)
- **Pre-releases**: `X.Y.Z-rc1`, `X.Y.Z-alpha1`, `X.Y.Z-beta1`
- **Development**: Automatically set to `X.Y.Z.devN` between tags

**Important**: Tags should **NOT** include a `v` prefix (use `0.1.0`, not `v0.1.0`).

## Semantic Versioning Guidelines

- **Major version (X.0.0)**: Breaking changes, incompatible API changes
- **Minor version (0.X.0)**: New features, backward-compatible
- **Patch version (0.0.X)**: Bug fixes, backward-compatible

## Creating a Release

### Prerequisites

1. Ensure you're on the `main` branch (or your default branch)
2. All changes are committed and pushed
3. CI tests are passing
4. You have push access to create tags

### Step-by-Step Process

#### 1. Decide on the version number

Following semantic versioning, determine whether this is a major, minor, or patch release.

```bash
# Example versions:
# - First release: 0.1.0
# - Bug fix: 0.1.1
# - New feature: 0.2.0
# - Breaking change: 1.0.0
```

#### 2. Update CHANGELOG (Optional but Recommended)

If you maintain a `CHANGELOG.md`, add an entry for the new version:

```markdown
## [0.2.0] - 2025-11-05

### Added
- New feature X
- Support for Y

### Fixed
- Bug in Z

### Changed
- Improved performance of W
```

Commit the changelog:
```bash
git add CHANGELOG.md
git commit -m "docs: Update CHANGELOG for version 0.2.0"
git push
```

#### 3. Create and push the git tag

```bash
# Create an annotated tag
git tag -a 0.2.0 -m "Release version 0.2.0"

# Push the tag to GitHub
git push origin 0.2.0
```

**Important**: Use annotated tags (`-a`) for releases. Lightweight tags may not work correctly with setuptools-scm.

#### 4. Automated release

Once the tag is pushed, GitHub Actions will automatically:
1. ✅ Verify the version matches the tag
2. 🔨 Build the package (wheel and source distribution)
3. 📦 Create a GitHub Release with the built artifacts
4. 📝 Add release notes (from CHANGELOG if available)

#### 5. Verify the release

1. Check the [GitHub Actions](../../actions) tab for workflow status
2. Verify the release appears in the [Releases](../../releases) page
3. Test installation from the release:
   ```bash
   pip install git+https://github.com/MarcusJellinghaus/mcp-config.git@0.2.0
   ```

## Publishing to PyPI (Future)

When ready to publish to PyPI:

1. Create a PyPI API token at https://pypi.org/manage/account/token/
2. Add it as a GitHub secret named `PYPI_API_TOKEN`
3. Uncomment the PyPI publishing step in `.github/workflows/release.yml`
4. Future tag pushes will automatically publish to PyPI

## Pre-releases

For testing before a stable release:

```bash
# Release candidate
git tag -a 0.2.0-rc1 -m "Release candidate 0.2.0-rc1"
git push origin 0.2.0-rc1

# Alpha or beta releases
git tag -a 0.2.0-alpha1 -m "Alpha release 0.2.0-alpha1"
git tag -a 0.2.0-beta1 -m "Beta release 0.2.0-beta1"
```

Pre-releases are automatically marked as "pre-release" in GitHub.

## Checking Current Version

### In Development

```bash
# Install in editable mode
pip install -e .

# Check version
python -c "from mcp_config import __version__; print(__version__)"
```

Between tags, the version will be something like `0.2.0.dev12+g1a2b3c4`, where:
- `0.2.0` is the next version
- `dev12` indicates 12 commits since last tag
- `g1a2b3c4` is the git commit hash

### Installed Package

```bash
# After installation
mcp-config --version
```

## Troubleshooting

### Version shows as `0.1.0.dev0`

This is the fallback version when:
- No git tags exist
- Package is not installed properly
- Running outside a git repository

**Solution**: Create the initial tag:
```bash
git tag -a 0.1.0 -m "Initial release"
git push origin 0.1.0
```

### Release workflow fails

Common issues:
1. **Version mismatch**: Ensure tag format is correct (no `v` prefix)
2. **Shallow clone**: Workflow uses `fetch-depth: 0` to get full history
3. **Permissions**: Workflow needs `contents: write` permission

Check the Actions tab for detailed error logs.

### Tag already exists

If you need to move a tag:
```bash
# Delete local tag
git tag -d 0.2.0

# Delete remote tag
git push origin :refs/tags/0.2.0

# Create new tag
git tag -a 0.2.0 -m "Release version 0.2.0"
git push origin 0.2.0
```

**Warning**: Moving tags after release is not recommended. Consider creating a patch release instead (e.g., `0.2.1`).

## Manual Release (Emergency)

If automated release fails, you can create a release manually:

```bash
# Build the package locally
python -m pip install build
python -m build

# This creates files in dist/:
# - mcp_config-X.Y.Z-py3-none-any.whl
# - mcp_config-X.Y.Z.tar.gz
```

Then create a GitHub release manually and upload the files from `dist/`.

## Best Practices

1. **Always test before releasing**: Run full test suite locally
2. **Use meaningful commit messages**: They may appear in release notes
3. **Document breaking changes**: Update README and documentation
4. **Keep CHANGELOG updated**: Makes release notes easier
5. **Use semantic versioning**: Helps users understand impact
6. **Test the release**: Install and verify after publishing

## Example Release Timeline

```bash
# 1. Make sure you're up to date
git checkout main
git pull origin main

# 2. Verify tests pass
pytest tests/

# 3. Update changelog (if applicable)
# Edit CHANGELOG.md
git add CHANGELOG.md
git commit -m "docs: Update CHANGELOG for 0.2.0"
git push

# 4. Create and push tag
git tag -a 0.2.0 -m "Release version 0.2.0"
git push origin 0.2.0

# 5. Wait for GitHub Actions to complete
# 6. Verify release on GitHub
# 7. Test installation
pip install git+https://github.com/MarcusJellinghaus/mcp-config.git@0.2.0
```

## Related Files

- `.github/workflows/release.yml` - Automated release workflow
- `pyproject.toml` - Package configuration and setuptools-scm settings
- `src/mcp_config/__init__.py` - Version import and fallback logic
