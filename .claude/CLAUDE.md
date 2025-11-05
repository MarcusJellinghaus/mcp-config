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

## 📝 Pull Request Workflow

**BEFORE creating or updating ANY pull request:**
1. Run code formatting: `bash tools/format_all.sh`
2. Review and commit any formatting changes
3. Then proceed with PR creation/update
