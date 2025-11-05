# Release Process

`mcp-config` uses git tags for versioning via `setuptools-scm`, following [Semantic Versioning](https://semver.org/).

## Quick Release

```bash
# 1. Ensure main is up to date and tests pass
git checkout main && git pull && pytest tests/

# 2. Create and push tag (no 'v' prefix!)
git tag -a 0.2.0 -m "Release version 0.2.0"
git push origin 0.2.0

# 3. GitHub Actions automatically builds and creates release
# 4. Verify at: https://github.com/MarcusJellinghaus/mcp-config/releases
```

## Version Format

- **Stable**: `0.1.0`, `1.2.3` (MAJOR.MINOR.PATCH)
- **Pre-release**: `0.2.0-rc1`, `0.2.0-alpha1`, `0.2.0-beta1`
- **Development**: `0.2.0.dev12+g1a2b3c4` (automatic between tags)

**Important**: Use annotated tags (`-a`) without `v` prefix.

## Semantic Versioning

- **MAJOR (X.0.0)**: Breaking changes
- **MINOR (0.X.0)**: New features (backward-compatible)
- **PATCH (0.0.X)**: Bug fixes (backward-compatible)

## Automated Release Workflow

When you push a tag, GitHub Actions automatically:
1. Verifies version matches tag
2. Builds wheel and source distribution
3. Creates GitHub Release with artifacts
4. Adds release notes (from CHANGELOG.md if present)

## Check Version

```bash
# CLI
mcp-config --version

# Python
python -c "from mcp_config import __version__; print(__version__)"
```

## Pre-releases

```bash
# Test before stable release
git tag -a 0.2.0-rc1 -m "Release candidate 0.2.0-rc1"
git push origin 0.2.0-rc1
```

Pre-releases are automatically marked as such on GitHub.

## Publishing to PyPI

When ready:
1. Create PyPI API token at https://pypi.org/manage/account/token/
2. Add as GitHub secret: `PYPI_API_TOKEN`
3. Uncomment PyPI step in `.github/workflows/release.yml`

## Troubleshooting

### Version shows `0.1.0.dev0`
No tags exist. Create initial tag:
```bash
git tag -a 0.1.0 -m "Initial release"
git push origin 0.1.0
```

### Release workflow fails
- Check tag format (no `v` prefix: use `0.1.0` not `v0.1.0`)
- Verify CI tests pass before tagging
- Review error logs in GitHub Actions tab

### Move/delete a tag
```bash
git tag -d 0.2.0
git push origin :refs/tags/0.2.0
git tag -a 0.2.0 -m "Release version 0.2.0"
git push origin 0.2.0
```
**Warning**: Avoid moving released tags. Use patch version instead (e.g., `0.2.1`).

## Manual Release (Emergency Only)

If automation fails:
```bash
python -m pip install build
python -m build
# Upload dist/* files to GitHub Release manually
```

---

**Configuration files:**
- `.github/workflows/release.yml` - Release automation
- `pyproject.toml` - setuptools-scm settings
