--- This file is used by Claude Code - similar to a system prompt. ---

## 🔧 MCP Tool Priority

**ALWAYS use MCP filesystem tools FIRST for ALL file operations:**
- `mcp__filesystem__read_file` - Read ANY file (AutoRunner or targets)
- `mcp__filesystem__save_file` - Write ANY file
- `mcp__filesystem__edit_file` - Edit ANY file
- `mcp__filesystem__list_directory` - List directories
- `mcp__filesystem__get_reference_projects` - List reference projects
- `mcp__filesystem__read_reference_file` - Read reference files

**Other MCP tools:**
- `mcp__code-checker__*` - Code quality checks (pylint, pytest, mypy)

**Standard tools ONLY for:**
- Git operations
- Running batch scripts

## 📦 Development Environment

**Before running any dev tools (formatters, linters, tests):**
- Check `pyproject.toml` for required dev dependencies
- Install dev dependencies: `pip install -e ".[dev]"`
- This ensures tools like `black`, `isort`, `pylint`, `pytest`, and `mypy` are available

**Tool configurations are defined in `pyproject.toml`:**
- `[tool.black]` - Black formatter settings
- `[tool.isort]` - Import sorting settings (profile=black, float_to_top=true)
- `[tool.mypy]` - Type checking settings
- `[tool.pytest.ini_options]` - Test configuration

## 📝 Pull Request Workflow

**BEFORE creating or updating ANY pull request:**
1. Ensure dev dependencies are installed: `pip install -e ".[dev]"`
2. Run code formatting: `bash tools/format_all.sh`
3. Review and commit any formatting changes
4. Then proceed with PR creation/update
