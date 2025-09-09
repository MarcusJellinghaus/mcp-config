# Step 3: IntelliJ Handler + Universal Comment Support (TDD + KISS)

## LLM Prompt
```
Following TDD approach, implement complete IntelliJ GitHub Copilot handler AND update all existing handlers (ClaudeDesktopHandler, VSCodeHandler) to use universal JSON comment utilities from Step 1. Write comprehensive tests FIRST, then implement. Keep it simple - same pattern for all handlers, minimal changes to existing code.
```

## WHERE
- **Files**:
  - `tests/test_config/test_intellij_handler.py` (expand - **WRITE TESTS FIRST**)
  - `tests/test_config/test_universal_comments.py` (new - **WRITE TESTS FIRST**)
  - `src/mcp_config/clients.py` (update existing + add IntelliJHandler after tests)

## TDD APPROACH (Tests Drive Design!)
### 1. Write Comprehensive Tests First (Red)
```python
# tests/test_config/test_universal_comments.py - WRITE FIRST
def test_claude_desktop_preserves_comments()
def test_vscode_preserves_comments()  
def test_intellij_preserves_comments()
def test_cross_client_comment_consistency()
def test_round_trip_comment_integrity_all_clients()

# tests/test_config/test_intellij_handler.py - EXPAND
def test_intellij_config_format_uses_servers_section()
def test_intellij_setup_server_workflow()
def test_intellij_remove_server_workflow()
def test_intellij_metadata_separation()
def test_intellij_follows_vscode_pattern()
```

### 2. Run Tests (Should Fail)
```bash
pytest tests/test_config/test_universal_comments.py -v  # RED - no universal support yet
pytest tests/test_config/test_intellij_handler.py -v    # RED - incomplete handler
```

### 3. Implement Universal Changes (Green)
- Update all existing handlers to use universal JSON utils
- Complete IntelliJ handler implementation
- Make all tests pass

## WHAT (TDD-Driven Universal Pattern)
### Universal Handler Pattern (Test-Driven)
```python
# Same pattern for ClaudeDesktopHandler, VSCodeHandler, IntelliJHandler
class SomeHandler(ClientHandler):
    def load_config(self) -> dict[str, Any]:
        """Load with universal comment preservation - TESTED FIRST."""
        from mcp_config.json_utils import load_json_with_comments
        config_path = self.get_config_path()
        data, model = load_json_with_comments(config_path)
        self._comment_model = model  # Store for later preservation
        
        # Existing logic for default structure (unchanged)
        if "servers" not in data:  # or "mcpServers" for Claude Desktop
            data["servers"] = {}  # or "mcpServers"
        return data
    
    def save_config(self, config: dict[str, Any]) -> None:
        """Save with universal comment preservation - TESTED FIRST."""
        from mcp_config.json_utils import save_json_with_comments
        config_path = self.get_config_path()
        model = getattr(self, '_comment_model', None)
        save_json_with_comments(config_path, config, model)
```

## TDD Test Plan (Write These FIRST!)
### Universal Comment Tests
1. **Cross-client comment preservation**:
   ```python
   @pytest.mark.parametrize("client_type", ["claude-desktop", "vscode-workspace", "intellij"])
   def test_universal_comment_preservation(client_type):
       # Test that ALL handlers preserve comments
       
   def test_round_trip_integrity_all_clients():
       # Load config → modify → save → reload → verify comments preserved
       # Test with Claude Desktop, VSCode, and IntelliJ formats
   ```

2. **IntelliJ-specific tests**:
   ```python
   def test_intellij_uses_servers_section():
       handler = IntelliJHandler()
       config = handler.load_config()
       assert "servers" in config  # NOT "mcpServers"
   
   def test_intellij_server_setup_with_comments():
       # Test setting up server preserves existing comments
       
   def test_intellij_metadata_separation():
       # Test metadata stored separately, not in main config
   ```

3. **Backward compatibility tests**:
   ```python
   def test_existing_claude_desktop_configs_still_work():
       # Ensure no breaking changes to existing functionality
       
   def test_existing_vscode_configs_enhanced():
       # VSCode configs get automatic comment support
   ```

4. **Integration tests**:
   ```python
   def test_all_handlers_use_same_json_utilities():
       # Verify all handlers use load_json_with_comments/save_json_with_comments
       
   def test_comment_model_stored_consistently():
       # All handlers store _comment_model for preservation
   ```

### IntelliJ Handler Tests (Comprehensive)
```python
def test_intellij_follows_vscode_pattern():
    """IntelliJ should behave exactly like VSCode handler."""
    vscode_handler = VSCodeHandler()
    intellij_handler = IntelliJHandler()
    
    # Same config section
    assert intellij_handler.CONFIG_SECTION == "servers"
    assert vscode_handler.CONFIG_SECTION == "servers"
    
    # Same metadata approach
    assert intellij_handler.METADATA_FILE == vscode_handler.METADATA_FILE

def test_intellij_server_lifecycle():
    """Test complete server setup/remove lifecycle with comments."""
    handler = IntelliJHandler()
    
    # Test setup preserves comments
    # Test removal preserves comments
    # Test list operations work correctly

def test_intellij_config_validation():
    """Test IntelliJ config validation with comments."""
    handler = IntelliJHandler()
    # Test validation works with JSONC format
```

## HOW (Test-Driven Implementation)
### Implementation Steps (After Tests)
1. **Update existing handlers** (minimal changes to pass tests):
   ```python
   # ClaudeDesktopHandler - change load_config/save_config methods
   # VSCodeHandler - change load_config/save_config methods  
   ```

2. **Complete IntelliJHandler** (following VSCode pattern):
   ```python
   class IntelliJHandler(ClientHandler):
       # Copy exact pattern from VSCodeHandler
       # Use universal JSON utilities
       # "servers" config section (like VSCode)
   ```

3. **Registry update**:
   ```python
   CLIENT_HANDLERS["intellij"] = IntelliJHandler
   ```

## TDD Workflow
```bash
# 1. Write comprehensive failing tests
pytest tests/test_config/test_universal_comments.py -v  # RED
pytest tests/test_config/test_intellij_handler.py -v    # RED

# 2. Update ClaudeDesktopHandler to use universal JSON
# Edit src/mcp_config/clients.py
pytest tests/test_config/test_universal_comments.py::test_claude_desktop_preserves_comments -v

# 3. Update VSCodeHandler to use universal JSON  
pytest tests/test_config/test_universal_comments.py::test_vscode_preserves_comments -v

# 4. Implement complete IntelliJHandler
pytest tests/test_config/test_intellij_handler.py -v  # GREEN

# 5. Verify all tests pass
pytest tests/test_config/test_universal_comments.py -v  # ALL GREEN
```

## Config Format (Test-Driven)
```javascript
// IntelliJ GitHub Copilot mcp.json - TEST VALIDATES THIS FORMAT
{
    // Comments preserved automatically - TESTED!
    "servers": {
        "mcp-code-checker": {
            "command": "python",
            "args": ["-m", "mcp_code_checker"],
            "env": {"PROJECT_ROOT": "/path/to/project"}
        }
        /* Block comments work too - TESTED! */
    }
}
```

## Comments (TDD Benefits)
- **Why test universal first**: Ensures all handlers get consistent enhancement
- **Why test IntelliJ = VSCode**: Validates same behavior, easier maintenance
- **Why test backward compatibility**: Existing users must not be broken
- **Why comprehensive test coverage**: Universal change affects all clients
