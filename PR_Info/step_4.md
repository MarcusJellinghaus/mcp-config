# Step 4: CLI Integration, Testing & Documentation

## LLM Prompt
```
Referring to the Summary: IntelliJ MCP Client Support with JSON Comments, implement Step 4: Integrate IntelliJ client into the CLI system, create comprehensive tests, and update documentation. Update client validation, help text, ensure all commands work with the new client, and document JetBrains IDE support. Follow TDD approach.
```

## WHERE
- **Files**:
  - `src/mcp_config/cli_utils.py` (update SUPPORTED_CLIENTS)
  - `src/mcp_config/help_system.py` (update help text)
  - `tests/test_config/test_intellij_integration.py` (new - comprehensive testing)
  - `README.md` (update supported clients)
  - `USER_GUIDE.md` (update with JetBrains documentation)
  - `pyproject.toml` (add json-five dependency)

## WHAT
### CLI Updates
```python
# In cli_utils.py
SUPPORTED_CLIENTS = [
    "claude-desktop", 
    "vscode-workspace", 
    "vscode-user",
    "intellij"  # Add this
]
```

### Integration Testing
```python
# Comprehensive end-to-end tests
def test_intellij_setup_workflow()
def test_intellij_comment_preservation()
def test_intellij_cli_integration()
def test_cross_platform_paths()
```

### Documentation Updates
```python
# Help text for IntelliJ support
INTELLIJ_HELP = """
IntelliJ/PyCharm MCP Client (intellij)
Config: github-copilot/intellij/mcp.json
Features: JSON comments support, JetBrains IDEs
Supports: IntelliJ IDEA, PyCharm, WebStorm, GoLand, etc.
"""
```

## HOW
### Integration Points
- **Client Registry**: Add "intellij" to SUPPORTED_CLIENTS list
- **Help System**: Add IntelliJ-specific help text and examples
- **Testing**: Mock-based integration testing (no real IntelliJ needed)
- **Documentation**: Update README and USER_GUIDE with JetBrains info

### Testing Strategy
- **Mock Configs**: Create realistic JSONC test scenarios
- **Cross-Platform**: Mock os.name and platform.system() for path testing
- **Integration**: End-to-end CLI workflow testing
- **Comment Preservation**: Verify round-trip integrity

## ALGORITHM
```
1. Add "intellij" to SUPPORTED_CLIENTS list in cli_utils.py
2. Update CLIENT_HANDLERS registry in clients.py
3. Add comprehensive integration tests with mock scenarios
4. Update help text and documentation
5. Test all CLI commands with IntelliJ client
6. Verify comment preservation in end-to-end tests
```

## DATA
### Client Information
```python
CLIENT_INFO = {
    "intellij": {
        "name": "IntelliJ/PyCharm",
        "config_file": "mcp.json",
        "config_section": "servers", 
        "features": ["comments", "cross-platform"],
        "description": "JetBrains IDEs with GitHub Copilot"
    }
}
```

### CLI Examples
```bash
# Examples for IntelliJ client
mcp-config setup mcp-code-checker "My Project" --client intellij --project-dir .
mcp-config list --client intellij --detailed
mcp-config remove "server-name" --client intellij
mcp-config validate --client intellij
```

## Tests to Write First
1. **Test CLI integration** - all commands work with "intellij" client
2. **Test comment preservation** - end-to-end JSONC round-trip
3. **Test cross-platform paths** - mock different OS environments
4. **Test setup workflow** - create realistic IntelliJ configs
5. **Test remove workflow** - verify metadata handling
6. **Test list functionality** - managed vs all servers
7. **Test validation** - JSONC format validation
8. **Test help text** - includes JetBrains documentation
9. **Test error handling** - malformed JSONC scenarios
10. **Test backup functionality** - existing backup system works
