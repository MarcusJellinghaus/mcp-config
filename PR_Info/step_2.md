# Step 2: IntelliJ GitHub Copilot Path Detection (TDD)

## LLM Prompt
```
Following TDD approach, implement IntelliJ GitHub Copilot path detection using verified Windows path and projected cross-platform paths. Write comprehensive tests FIRST, then implement. Follow existing ClientHandler pattern exactly - copy the approach from ClaudeDesktopHandler.get_config_path().
```

## WHERE
- **Files**:
  - `tests/test_config/test_intellij_handler.py` (new - **WRITE FIRST**)
  - `src/mcp_config/clients.py` (update - add IntelliJHandler skeleton after tests)

## TDD APPROACH (Tests First!)
### 1. Write Path Tests First (Red)
```python
# tests/test_config/test_intellij_handler.py - WRITE THESE FIRST
def test_windows_path_verified()
def test_macos_path_projected() 
def test_linux_path_projected()
def test_cross_platform_consistency()
def test_github_copilot_directory_structure()
def test_metadata_path_follows_pattern()
def test_integration_with_client_handler_interface()
```

### 2. Run Tests (Should Fail)
```bash
pytest tests/test_config/test_intellij_handler.py -v  # Should fail - no handler yet
```

### 3. Implement Minimum (Green)
```python
# src/mcp_config/clients.py - Add minimal IntelliJHandler to pass tests
class IntelliJHandler(ClientHandler):
    def get_config_path(self) -> Path:
        # Minimal implementation to pass path tests
```

## WHAT (TDD-Driven Paths)
```python
class IntelliJHandler(ClientHandler):
    def get_config_path(self) -> Path:
        """Get IntelliJ GitHub Copilot MCP config path."""
        # VERIFIED Windows: C:\Users\username\AppData\Local\github-copilot\intellij\mcp.json
        # PROJECTED macOS: ~/Library/Application Support/github-copilot/intellij/mcp.json
        # PROJECTED Linux: ~/.local/share/github-copilot/intellij/mcp.json
```

## TDD Test Plan (Write These FIRST!)
### Critical Path Tests
1. **Platform-specific path tests**:
   ```python
   @patch('os.name', 'nt')
   def test_windows_path_verified():
       handler = IntelliJHandler()
       path = handler.get_config_path()
       assert str(path).endswith(r'AppData\Local\github-copilot\intellij\mcp.json')
   
   @patch('platform.system', return_value='Darwin')
   def test_macos_path_projected():
       handler = IntelliJHandler()  
       path = handler.get_config_path()
       assert 'Library/Application Support/github-copilot/intellij/mcp.json' in str(path)
   
   def test_linux_path_projected():
       handler = IntelliJHandler()
       path = handler.get_config_path()
       assert '.local/share/github-copilot/intellij/mcp.json' in str(path)
   ```

2. **Cross-platform consistency tests**:
   - All platforms use `github-copilot/intellij/mcp.json` structure
   - Path construction follows same pattern as existing handlers
   - Home directory detection works correctly

3. **Integration tests**:
   - Handler implements ClientHandler interface correctly
   - get_config_path() returns Path object
   - get_metadata_path() follows existing pattern
   - Handler can be instantiated without errors

4. **Real-world validation tests**:
   - Windows path matches confirmed real user path
   - macOS path follows Apple app support conventions
   - Linux path follows XDG Base Directory specification

## HOW (Test-Driven Implementation)
### Implementation Pattern (Copy ClaudeDesktopHandler)
```python
def get_config_path(self) -> Path:
    """Get GitHub Copilot MCP config path - follows ClaudeDesktopHandler pattern."""
    home_str = str(Path.home())  # Same pattern as existing handlers
    
    if os.name == "nt":  # Windows - VERIFIED PATH
        return Path(home_str) / "AppData" / "Local" / "github-copilot" / "intellij" / "mcp.json"
    elif platform.system() == "Darwin":  # macOS - PROJECTED
        return Path(home_str) / "Library" / "Application Support" / "github-copilot" / "intellij" / "mcp.json"
    else:  # Linux - PROJECTED (XDG Base Directory)
        return Path(home_str) / ".local" / "share" / "github-copilot" / "intellij" / "mcp.json"
```

### Additional TDD Tests
```python
def test_handler_inheritance():
    """Test IntelliJHandler properly inherits from ClientHandler."""
    handler = IntelliJHandler()
    assert isinstance(handler, ClientHandler)

def test_metadata_path_pattern():
    """Test metadata path follows existing handler pattern."""
    handler = IntelliJHandler()
    config_path = handler.get_config_path()
    metadata_path = handler.get_metadata_path()
    assert metadata_path.name == ".mcp-config-metadata.json"
    assert metadata_path.parent == config_path.parent

def test_constants_match_existing_pattern():
    """Test class constants follow existing handler patterns."""
    assert IntelliJHandler.MANAGED_SERVER_MARKER == "mcp-config-managed"
    assert IntelliJHandler.METADATA_FILE == ".mcp-config-metadata.json"
```

## TDD Workflow
```bash
# 1. Write failing path tests
pytest tests/test_config/test_intellij_handler.py::test_windows_path_verified -v  # RED

# 2. Add minimal IntelliJHandler class
# Edit src/mcp_config/clients.py

# 3. Run tests until green  
pytest tests/test_config/test_intellij_handler.py -v  # GREEN

# 4. Add more platform tests
pytest tests/test_config/test_intellij_handler.py::test_macos_path_projected -v

# 5. Refactor while keeping tests green
```

## DATA (Test-Driven Validation)
### Verified Path Structure
```python
# Test data based on research findings
EXPECTED_PATHS = {
    "windows": "AppData/Local/github-copilot/intellij/mcp.json",    # VERIFIED
    "macos": "Library/Application Support/github-copilot/intellij/mcp.json",  # PROJECTED  
    "linux": ".local/share/github-copilot/intellij/mcp.json"       # PROJECTED
}
```

## Comments (TDD Benefits)
- **Why test paths first**: Ensures cross-platform compatibility before implementation
- **Why mock platforms**: Tests work on any development OS
- **Why verify Windows**: Confirmed real-world path must be preserved
- **Why test integration**: Handler must work with existing ClientHandler interface
