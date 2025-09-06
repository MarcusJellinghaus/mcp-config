# Step 2: IntelliJ Path Detection

## LLM Prompt
```
Referring to the Summary: IntelliJ MCP Client Support with JSON Comments, implement Step 2: Add IntelliJ-specific path detection to the paths.py module. Support cross-platform detection of IntelliJ MCP config locations following the existing pattern. Write tests first following TDD approach.
```

## WHERE
- **Files**:
  - `src/mcp_config/paths.py` (update)
  - `tests/test_config/test_paths.py` (update)

## WHAT
### Main Functions
```python
def get_intellij_config_path() -> Path
def get_intellij_config_dir() -> Path
def validate_intellij_path(path: Path) -> tuple[bool, Optional[str]]
```

### Constants to Add
```python
class PathConstants:
    # Add to existing class
    INTELLIJ_CONFIG_PATHS = {
        "win32": "AppData/Local/github-copilot/intellij",
        "darwin": "Library/Application Support/github-copilot/intellij", 
        "linux": ".local/share/github-copilot/intellij"
    }
```

## HOW
### Integration Points
- **Import Pattern**: Follow existing `get_platform_info()` usage
- **Path Construction**: Use `normalize_path()` for consistency
- **Validation**: Leverage existing `validate_path()` function

### Platform Detection
```python
# Follow existing pattern in paths.py
platform_info = get_platform_info()
if platform_info["is_windows"]:
    # Windows logic
elif platform_info["is_macos"]:
    # macOS logic  
else:
    # Linux logic
```

## ALGORITHM
```
1. Get platform information using existing utilities
2. Construct base path from INTELLIJ_CONFIG_PATHS
3. Resolve relative to user home directory
4. Append "mcp.json" for full config path
5. Apply path normalization and validation
```

## DATA
### Return Values
- `get_intellij_config_path()`: `Path` - Full path to mcp.json
- `get_intellij_config_dir()`: `Path` - Directory containing config
- `validate_intellij_path()`: `tuple[bool, Optional[str]]` - Validation result

### Path Patterns
```python
# Windows: C:\Users\username\AppData\Local\github-copilot\intellij\mcp.json
# macOS: ~/Library/Application Support/github-copilot/intellij/mcp.json  
# Linux: ~/.local/share/github-copilot/intellij/mcp.json
```

## Tests to Write First
1. **Test Windows path detection** with mocked environment
2. **Test macOS path detection** with mocked platform
3. **Test Linux path detection** with mocked system
4. **Test path validation** for valid/invalid paths
5. **Test error handling** for unsupported platforms
6. **Test path normalization** edge cases
