# Step 1: IntelliJ Handler Path Detection (TDD)

## LLM Prompt
```
Following TDD approach, implement IntelliJ GitHub Copilot path detection with cross-platform support. Write comprehensive tests FIRST, then implement. Focus on accurate path detection across Windows, macOS, and Linux.
```

## WHERE
- **Files**: 
  - `tests/test_config/test_intellij_paths.py` (new - **WRITE FIRST**)
  - `src/mcp_config/clients.py` (update - add IntelliJHandler after tests)

## TDD APPROACH (Tests First!)
### 1. Write Tests First (Red)
```python
# tests/test_config/test_intellij_paths.py - WRITE THESE FIRST
def test_windows_path_verified()
def test_macos_path_projected() 
def test_linux_path_projected()
def test_cross_platform_consistency()
def test_github_copilot_directory_structure()
def test_metadata_path_follows_pattern()
def test_error_handling_missing_github_copilot()
```

### 2. Run Tests (Should Fail)
```bash
pytest tests/test_config/test_intellij_paths.py  # Should fail - no implementation yet
```

### 3. Implement Minimum (Green)
```python
# src/mcp_config/clients.py - Add minimal IntelliJHandler to pass tests
class IntelliJHandler(ClientHandler):
    def get_config_path(self) -> Path:
        # Minimal implementation to pass tests
```

### 4. Refactor (Clean)
- Optimize implementation while keeping tests green

## WHAT (TDD-Driven Paths)
```python
class IntelliJHandler(ClientHandler):
    def get_config_path(self) -> Path:
        """Get IntelliJ GitHub Copilot MCP config path."""
        # VERIFIED Windows: C:\Users\username\AppData\Local\github-copilot\intellij\mcp.json
        # PROJECTED macOS: ~/Library/Application Support/github-copilot/intellij/mcp.json
        # PROJECTED Linux: ~/.local/share/github-copilot/intellij/mcp.json
```

## HOW (Test-Driven Implementation)
### Implementation Pattern (Follow existing handlers)
```python
def get_config_path(self) -> Path:
    """Get GitHub Copilot MCP config path - follows existing handler pattern."""
    home_str = str(Path.home())  # Same pattern as existing handlers
    
    config_path = None
    if os.name == "nt":  # Windows - VERIFIED PATH
        config_path = Path(home_str) / "AppData" / "Local" / "github-copilot" / "intellij" / "mcp.json"
    elif platform.system() == "Darwin":  # macOS - PROJECTED
        config_path = Path(home_str) / "Library" / "Application Support" / "github-copilot" / "intellij" / "mcp.json"
    else:  # Linux - PROJECTED (XDG Base Directory)
        config_path = Path(home_str) / ".local" / "share" / "github-copilot" / "intellij" / "mcp.json"
    
    # Error handling: Check if GitHub Copilot directory exists
    if not config_path.parent.exists():
        raise FileNotFoundError(
            f"GitHub Copilot for IntelliJ not found. Expected config directory: "
            f"{config_path.parent} does not exist. Please install GitHub Copilot for IntelliJ first."
        )
    
    return config_path
```

## TDD Test Plan (Write These FIRST!)
### Critical Test Cases
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

4. **Error handling tests**:
   - Clear error when GitHub Copilot directory missing
   - Error message includes expected path location

## TDD Workflow
```bash
# 1. Write failing tests
pytest tests/test_config/test_intellij_paths.py -v  # RED

# 2. Implement minimal code to pass
# Edit src/mcp_config/clients.py

# 3. Run tests until green
pytest tests/test_config/test_intellij_paths.py -v  # GREEN

# 4. Refactor while keeping tests green
# Improve implementation, tests stay green

# 5. Add more tests for edge cases
# Repeat cycle
```

## Comments (TDD Benefits)
- **Why tests first**: Ensures cross-platform compatibility before implementation
- **Why mock platforms**: Tests work on any development OS
- **Why verify Windows**: Confirmed real-world path must be preserved
- **Why test integration**: Handler must work with existing ClientHandler interface
- **Why error handling**: Clear user guidance when GitHub Copilot not installed
