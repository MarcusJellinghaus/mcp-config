# Summary: IntelliJ MCP Client Support

## Overview
Add IntelliJ/PyCharm GitHub Copilot MCP client support to complement existing Claude Desktop and VSCode clients.

## Goals
1. **Add IntelliJ Client**: Support GitHub Copilot MCP at `%LOCALAPPDATA%\github-copilot\intellij\mcp.json`
2. **KISS Principle**: Minimal complexity, consistent behavior
3. **Cross-Platform**: Support Windows, macOS, and Linux

## Key Requirements
- **Standard JSON**: Use built-in JSON library (no additional dependencies)
- **Verified IntelliJ Paths**: Windows path confirmed, macOS/Linux paths projected
- **Config Format**: IntelliJ uses `servers` section (like VSCode), not `mcpServers`
- **Consistent Patterns**: Follow existing `ClientHandler` pattern everywhere
- **Zero Breaking Changes**: All existing functionality preserved

## Technical Approach (KISS)
- **No New Dependencies**: Use standard library JSON handling
- **Pattern Consistency**: All handlers use same load/save logic
- **Minimal Changes**: Add IntelliJ handler following VSCode pattern
- **Simple Error Handling**: Fail with clear messages when GitHub Copilot not installed

## Research Findings
- **IntelliJ**: GitHub Copilot stores MCP config in `github-copilot/intellij/mcp.json`
- **VSCode**: Uses `servers` section in config
- **Claude Desktop**: Uses `mcpServers` section

## Success Criteria
1. **Compatible**: All existing functionality works unchanged
2. **Consistent**: Same behavior and user experience everywhere
3. **Maintainable**: Simple codebase, easy to add new clients
4. **Functional**: IntelliJ setup/list/remove operations work correctly

## Non-Goals
- JSON comment support (adds complexity)
- Additional dependencies
- Client-specific handling logic beyond path differences
- Breaking changes to existing APIs
