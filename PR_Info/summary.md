# Summary: Universal JSON Comments + IntelliJ MCP Client Support

## Overview
Add IntelliJ/PyCharm GitHub Copilot MCP client support with **universal JSON comment preservation** across all MCP clients (Claude Desktop, VSCode, IntelliJ).

## Goals
1. **Universal Comment Support**: All MCP config files preserve comments automatically
2. **Add IntelliJ Client**: Support GitHub Copilot MCP at `%LOCALAPPDATA%\github-copilot\intellij\mcp.json`
3. **KISS Principle**: Single dependency, consistent behavior, minimal complexity
4. **Cross-Platform**: Support Windows, macOS, and Linux

## Key Requirements
- **Single JSON Handler**: Use `json-five` library for ALL clients (required dependency)
- **Verified IntelliJ Paths**: Windows path confirmed, macOS/Linux paths projected
- **Config Format**: IntelliJ uses `servers` section (like VSCode), not `mcpServers`
- **Consistent Patterns**: Follow existing `ClientHandler` pattern everywhere
- **Zero Breaking Changes**: All existing functionality preserved

## Technical Approach (KISS)
- **One Dependency**: `json-five` as required dependency (no fallbacks, no complexity)
- **One JSON Handler**: Universal comment-preserving utilities for all clients  
- **Pattern Consistency**: All handlers use same load/save comment logic
- **Minimal Changes**: Update existing handlers with 5-line changes
- **Simple Error Handling**: Fail with clear messages when GitHub Copilot not installed

## Research Findings
- **IntelliJ**: GitHub Copilot stores MCP config in `github-copilot/intellij/mcp.json`
- **VSCode**: Already supports JSONC natively, our enhancement maintains consistency
- **Claude Desktop**: Currently standard JSON, enhanced to support comments
- **json-five API**: Confirmed ModelLoader/ModelDumper needed for comment preservation

## Success Criteria
1. **Universal**: Comments preserved in ALL client configs (Claude Desktop, VSCode, IntelliJ)
2. **Simple**: One codebase path for JSON handling across all clients
3. **Compatible**: All existing functionality works unchanged
4. **Consistent**: Same behavior and user experience everywhere
5. **Maintainable**: Single JSON handler to maintain, easy to add new clients

## Non-Goals
- Multiple JSON handling approaches (complexity)
- Optional dependencies or fallback mechanisms
- Client-specific comment handling logic
- Breaking changes to existing APIs
