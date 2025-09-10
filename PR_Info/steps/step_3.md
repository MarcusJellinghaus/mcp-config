# Step 3: Complete IntelliJ Handler (TDD)

## LLM Prompt
```
Following TDD approach, implement complete IntelliJ GitHub Copilot handler with all CRUD operations (setup, list, remove). Write comprehensive tests FIRST, then implement. Follow VSCodeHandler pattern exactly since both use 'servers' config format and standard JSON.
```

## WHERE
- **Files**:
  - `tests/test_config/test_intellij_handler.py` (expand - **WRITE TESTS FIRST**)
  - `src/mcp_config/clients.py` (complete IntelliJHandler implementation after tests)

## TDD APPROACH (Tests Drive Design!)
### 1. Write Comprehensive Tests First (Red)
```python
# tests/test_config/test_intellij_handler.py - EXPAND
def test_intellij_config_format_uses_servers_section()
def test_intellij_setup_server_workflow()
def test_intellij_remove_server_workflow()
def test_intellij_list_servers_workflow()
def test_intellij_metadata_separation()
def test_intellij_follows_vscode_pattern()
def test_intellij_standard_json_handling()
```

### 2. Run Tests (Should Fail)
```bash
pytest tests/test_config/test_intellij_handler.py -v    # RED - incomplete handler
```

### 3. Implement Complete Handler (Green)
- Complete IntelliJ handler implementation
- Make all tests pass

## WHAT (TDD-Driven Handler Pattern)
### Complete Handler Pattern (Test-Driven)
```python
# IntelliJHandler following VSCodeHandler pattern exactly
class IntelliJHandler(ClientHandler):
    CONFIG_SECTION = "servers"  # Same as VSCode
    
    def load_config(self) -> dict[str, Any]:
        """Load config with standard JSON handling."""
        config_path = self.get_config_path()
        if not config_path.exists():
            return {"servers": {}}
        
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Ensure servers section exists
        if "servers" not in data:
            data["servers"] = {}
        return data
    
    def save_config(self, config: dict[str, Any]) -> None:
        """Save config with standard JSON formatting."""
        config_path = self.get_config_path()
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
            f.write('\n')
```

## TDD Test Plan (Write These FIRST!)
### IntelliJ Handler Tests
1. **Core functionality tests**:
   ```python
   def test_intellij_uses_servers_section():
       handler = IntelliJHandler()
       config = handler.load_config()
       assert "servers" in config  # Same as VSCode
   
   def test_intellij_server_setup_workflow():
       # Test complete setup workflow
       
   def test_intellij_metadata_separation():
       # Test metadata stored separately, not in main config
   ```

2. **JSON handling tests**:
   ```python
   def test_intellij_standard_json_handling():
       # Test standard JSON load/save without comments
       
   def test_intellij_config_validation():
       # Test config validation works correctly
   ```

3. **Integration tests**:
   ```python
   def test_intellij_follows_vscode_pattern():
       # Verify IntelliJ handler behaves like VSCode handler
       
   def test_intellij_handler_interface():
       # Test handler implements ClientHandler interface correctly
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
pytest tests/test_config/test_intellij_handler.py -v    # RED

# 2. Implement complete IntelliJHandler
# Edit src/mcp_config/clients.py
pytest tests/test_config/test_intellij_handler.py -v  # GREEN

# 3. Add to client registry
# Update CLIENT_HANDLERS mapping

# 4. Verify all tests pass
pytest tests/test_config/test_intellij_handler.py -v  # ALL GREEN
```

## Config Format (Test-Driven)
```json
{
    "servers": {
        "mcp-code-checker": {
            "command": "python",
            "args": ["-m", "mcp_code_checker"],
            "env": {"PROJECT_ROOT": "/path/to/project"}
        }
    }
}
```

## Comments (TDD Benefits)
- **Why test IntelliJ = VSCode**: Validates same behavior, easier maintenance
- **Why standard JSON**: Simpler implementation, no additional dependencies
- **Why comprehensive tests**: Ensures handler works correctly with all operations
