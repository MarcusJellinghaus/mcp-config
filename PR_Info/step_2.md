# Step 2: IntelliJ Path Detection

## LLM Prompt
```
Referring to the Summary: IntelliJ MCP Client Support with JSON Comments, implement Step 2: Implement IntelliJ path detection directly in the IntelliJHandler class using the get_config_path() method, following the same pattern as existing client handlers. Write tests first following TDD approach.
```

## WHERE
- **Files**:
  - `src/mcp_config/clients.py` (update - add IntelliJHandler class)
  - `tests/test_config/test_intellij_handler.py` (new - path testing)

## WHAT
### Main Class Method
```python
class IntelliJHandler(ClientHandler):
    def get_config_path(self) -> Path:
        """Get IntelliJ MCP config path using existing platform detection pattern."""
        # Follow same pattern as ClaudeDesktopHandler and VSCodeHandler
```

### Path Structure
```python
# Windows: %LOCALAPPDATA%\github-copilot\intellij\mcp.json
# macOS: ~/Library/Application Support/github-copilot/intellij/mcp.json  
# Linux: ~/.local/share/github-copilot/intellij/mcp.json
```

## HOW
### Integration Points
- **Follow Existing Pattern**: Use same approach as ClaudeDesktopHandler.get_config_path()
- **Platform Detection**: Use `os.name` and `platform.system()` directly
- **Path Construction**: Use `Path.home()` and path concatenation

### Implementation Pattern
```python
def get_config_path(self) -> Path:
    home_str = str(Path.home())
    if os.name == "nt":  # Windows
        return Path(home_str) / "AppData" / "Local" / "github-copilot" / "intellij" / "mcp.json"
    elif platform.system() == "Darwin":  # macOS
        return Path(home_str) / "Library" / "Application Support" / "github-copilot" / "intellij" / "mcp.json"
    else:  # Linux
        return Path(home_str) / ".local" / "share" / "github-copilot" / "intellij" / "mcp.json"
```

## ALGORITHM
```
1. Get user home directory using Path.home()
2. Detect platform using os.name and platform.system()
3. Construct platform-specific path to github-copilot/intellij/
4. Append "mcp.json" for full config path
5. Return complete Path object
```

## DATA
### Return Values
- `get_config_path()`: `Path` - Full path to IntelliJ mcp.json

### Path Patterns
```python
# Windows: C:\Users\username\AppData\Local\github-copilot\intellij\mcp.json
# macOS: ~/Library/Application Support/github-copilot/intellij/mcp.json  
# Linux: ~/.local/share/github-copilot/intellij/mcp.json
```

## Tests to Write First
1. **Test Windows path detection** with mocked os.name
2. **Test macOS path detection** with mocked platform.system()
3. **Test Linux path detection** with mocked platform  
4. **Test path construction** with various home directories
5. **Test integration** with existing ClientHandler pattern
6. **Test metadata path** (get_metadata_path method)
