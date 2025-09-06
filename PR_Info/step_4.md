# Step 4: CLI Integration and Help System

## LLM Prompt
```
Referring to the Summary: IntelliJ MCP Client Support with JSON Comments, implement Step 4: Integrate IntelliJ client into the CLI system and help documentation. Update client validation, help text, and ensure all commands work with the new client. Follow TDD approach.
```

## WHERE
- **Files**:
  - `src/mcp_config/main.py` (update client validation)
  - `src/mcp_config/help_system.py` (update help text)
  - `src/mcp_config/cli_utils.py` (update validation)
  - `tests/test_config/test_cli_intellij.py` (new)
  - `USER_GUIDE.md` (update)

## WHAT
### CLI Updates
```python
# In cli_utils.py
VALID_CLIENTS = [
    "claude-desktop", 
    "vscode-workspace", 
    "vscode-user",
    "intellij"  # Add this
]

def validate_client(client: str) -> bool
def get_client_help_text() -> str
```

### Help System Updates
```python
# In help_system.py  
def get_client_documentation(client: str) -> str
def get_intellij_help() -> str
```

## HOW
### Integration Points
- **Client Validation**: Update `validate_client()` to include "intellij"
- **Help System**: Add IntelliJ-specific help text and examples
- **Error Messages**: Update error messages to mention IntelliJ option
- **Command Examples**: Add IntelliJ examples to help output

### Help Text Structure
```python
INTELLIJ_HELP = """
IntelliJ/PyCharm MCP Client (intellij)
Config: %LOCALAPPDATA%\\github-copilot\\intellij\\mcp.json
Features: JSON comments support, cross-platform paths
Use for: IntelliJ IDEA, PyCharm, other JetBrains IDEs
"""
```

## ALGORITHM
```
1. Add "intellij" to VALID_CLIENTS list
2. Update help text generation to include IntelliJ
3. Add IntelliJ-specific documentation and examples  
4. Update error messages for unknown clients
5. Ensure all CLI commands work with new client
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

### Help Examples
```bash
# Examples to add to help text
mcp-config setup mcp-code-checker "My Project" --client intellij --project-dir .
mcp-config list --client intellij
mcp-config remove "server-name" --client intellij
```

## Tests to Write First
1. **Test client validation** accepts "intellij"
2. **Test help text generation** includes IntelliJ
3. **Test CLI commands** work with IntelliJ client
4. **Test error messages** for invalid clients
5. **Test setup command** with IntelliJ client
6. **Test list command** with IntelliJ client  
7. **Test remove command** with IntelliJ client
8. **Test help command** shows IntelliJ documentation
9. **Test validation command** works with IntelliJ configs
10. **Test client-specific help** output formatting
