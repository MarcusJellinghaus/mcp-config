# Summary: IntelliJ MCP Client Support with JSON Comments

## Overview
Add support for IntelliJ/PyCharm as an MCP client with JSON comments (JSONC) support, ensuring comments are preserved during configuration file modifications.

## Goals
1. **Add IntelliJ Client Support**: Support IntelliJ/PyCharm MCP configuration at `%LOCALAPPDATA%\github-copilot\intellij\mcp.json`
2. **Preserve Comments**: Ensure editing config files doesn't remove existing comments
3. **Minimal Changes**: Follow existing patterns and maintain backward compatibility
4. **Cross-Platform**: Support Windows, macOS, and Linux

## Key Requirements
- **Comment Preservation**: Use `json-five` library for round-trip comment preservation
- **Client Pattern**: Follow existing `ClientHandler` pattern (similar to VSCode)
- **Path Detection**: Cross-platform IntelliJ config path detection
- **Config Format**: Similar to VSCode with `servers` section
- **Metadata Separation**: Use same `.mcp-config-metadata.json` pattern

## Technical Approach
- **Library Choice**: `json-five` as required dependency for comment-preserving JSON parsing
- **Simple Implementation**: Direct usage of `json-five` without fallbacks or complexity
- **Handler Pattern**: Follow existing `ClientHandler` pattern with `get_config_path()` method
- **Test-Driven**: Write tests first for comment preservation and IntelliJ handler

## Success Criteria
1. IntelliJ configs can be read/written with comments preserved
2. All existing functionality works unchanged
3. New `intellij` client option in CLI
4. Comprehensive test coverage
5. Updated documentation

## Non-Goals
- Changing existing Claude Desktop or VSCode behavior
- Adding comment support to other clients (optional future enhancement)
- Complex comment formatting or validation
- Optional dependencies or fallback mechanisms
