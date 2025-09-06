# Step 4: CLI Integration + Universal Comments Documentation (TDD)

## LLM Prompt
```
Following TDD approach, complete CLI integration for IntelliJ client and update all documentation to reflect universal JSON comment support across ALL clients. Write integration tests FIRST, then update CLI and documentation. Test that all CLI commands work with all clients and preserve comments.
```

## WHERE
- **Files**:
  - `tests/test_config/test_universal_integration.py` (new - **WRITE TESTS FIRST**)
  - `tests/test_config/test_cli_intellij.py` (new - **WRITE TESTS FIRST**)
  - `src/mcp_config/cli_utils.py` (add "intellij" to SUPPORTED_CLIENTS after tests)
  - `src/mcp_config/help_system.py` (update with universal comment support after tests)
  - `README.md` (universal comment support + IntelliJ)
  - `USER_GUIDE.md` (comprehensive universal comments guide)
  - `pyproject.toml` (confirm json-five dependency added)

## TDD APPROACH (Tests Drive CLI Integration!)
### 1. Write CLI Integration Tests First (Red)
```python
# tests/test_config/test_universal_integration.py - WRITE FIRST
def test_all_cli_commands_work_with_all_clients()
def test_universal_comment_preservation_end_to_end()
def test_setup_command_preserves_comments_all_clients()
def test_remove_command_preserves_comments_all_clients()
def test_list_command_works_with_comments()
def test_validate_command_handles_comments()

# tests/test_config/test_cli_intellij.py - WRITE FIRST  
def test_intellij_client_registration()
def test_intellij_setup_command()
def test_intellij_remove_command()
def test_intellij_list_command()
def test_intellij_validate_command()
def test_intellij_cli_help_text()
```

### 2. Run Tests (Should Fail)
```bash
pytest tests/test_config/test_cli_intellij.py -v      # RED - "intellij" not in CLI yet
pytest tests/test_config/test_universal_integration.py -v  # RED - no universal comment CLI support
```

### 3. Implement CLI Changes (Green)
- Add "intellij" to SUPPORTED_CLIENTS
- Update help text with universal comment support
- Make all CLI integration tests pass

## TDD Test Plan (Write These FIRST!)
### Critical CLI Integration Tests
1. **Client registration tests**:
   ```python
   def test_intellij_in_supported_clients():
       from mcp_config.cli_utils import SUPPORTED_CLIENTS
       assert "intellij" in SUPPORTED_CLIENTS
   
   def test_intellij_handler_in_registry():
       from mcp_config.clients import CLIENT_HANDLERS
       assert "intellij" in CLIENT_HANDLERS
       assert CLIENT_HANDLERS["intellij"] == IntelliJHandler
   ```

2. **End-to-end CLI workflow tests**:
   ```python
   @pytest.mark.parametrize("client", ["claude-desktop", "vscode-workspace", "intellij"])
   def test_setup_workflow_preserves_comments(client):
       # Test: mcp-config setup server "desc" --client {client}
       # Verify: Comments in existing config are preserved
   
   def test_intellij_specific_workflow():
       # Test complete IntelliJ workflow from CLI
       # setup → list → remove → validate
   ```

3. **Universal comment CLI tests**:
   ```python
   def test_all_commands_preserve_comments():
       # Test every CLI command preserves comments for every client
       commands = ["setup", "remove", "list", "validate", "backup"]
       clients = ["claude-desktop", "vscode-workspace", "vscode-user", "intellij"]
       
       for command in commands:
           for client in clients:
               # Test command preserves comments
   ```

4. **Help and documentation tests**:
   ```python
   def test_help_mentions_universal_comments():
       # Test CLI help mentions comment support for all clients
       
   def test_intellij_help_text_accurate():
       # Test IntelliJ-specific help is accurate
   ```

### Integration Test Examples
```python
def test_real_world_intellij_workflow():
    """Test realistic IntelliJ GitHub Copilot workflow."""
    # Create IntelliJ config with comments
    config_content = '''
    {
        // IntelliJ GitHub Copilot MCP Configuration
        "servers": {
            "existing-server": {
                "command": "existing-command",
                "args": ["arg1"]
                /* This server was configured manually */
            }
        }
    }
    '''
    
    # Run CLI setup command
    result = run_cli_command([
        "setup", "mcp-code-checker", "My Project",
        "--client", "intellij",
        "--project-dir", "."
    ])
    
    # Verify:
    # 1. Command succeeded
    # 2. New server added
    # 3. Existing comments preserved
    # 4. New server has correct IntelliJ format

def test_cross_client_consistency():
    """Test that same server setup works consistently across all clients."""
    clients = ["claude-desktop", "vscode-workspace", "intellij"]
    
    for client in clients:
        # Setup same server on each client
        # Verify consistent behavior
        # Verify comments preserved where supported
```

## WHAT (Test-Driven CLI Updates)
### CLI Updates (Simple - After Tests Pass)
```python
# cli_utils.py - One line change (after tests)
SUPPORTED_CLIENTS = [
    "claude-desktop", 
    "vscode-workspace", 
    "vscode-user",
    "intellij"  # Add this to make tests pass
]
```

### Help Text (Test-Driven Universal Comments)
```python
UNIVERSAL_COMMENTS_HELP = """
✨ Universal JSON Comment Support ✨
All MCP configuration files now preserve comments automatically!

Supported Clients:
  claude-desktop     - Comments preserved in claude_desktop_config.json
  vscode-workspace   - Comments preserved in .vscode/mcp.json  
  vscode-user        - Comments preserved in user profile mcp.json
  intellij           - Comments preserved in GitHub Copilot mcp.json

Example with comments:
  {
      // Your helpful comments are preserved!
      "mcpServers": {
          "my-server": {
              "command": "python", 
              "args": ["-m", "my_server"]
              /* Block comments work too */
          }
      }
  }
"""
```

## TDD Workflow
```bash
# 1. Write comprehensive CLI integration tests
pytest tests/test_config/test_cli_intellij.py::test_intellij_client_registration -v  # RED

# 2. Add "intellij" to SUPPORTED_CLIENTS to make test pass
# Edit src/mcp_config/cli_utils.py

# 3. Test CLI commands work
pytest tests/test_config/test_cli_intellij.py::test_intellij_setup_command -v

# 4. Write universal comment integration tests  
pytest tests/test_config/test_universal_integration.py -v  # Should be GREEN if Step 3 worked

# 5. Update help text to make help tests pass
pytest tests/test_config/test_cli_intellij.py::test_intellij_cli_help_text -v

# 6. Verify all integration tests pass
pytest tests/test_config/test_universal_integration.py -v  # ALL GREEN
```

## CLI Examples (Test-Validated)
```bash
# These commands tested to preserve comments for ALL clients!
mcp-config setup myserver "Description" --client claude-desktop
mcp-config setup myserver "Description" --client vscode-workspace  
mcp-config setup myserver "Description" --client intellij

# Validation works with comments for all clients (tested)
mcp-config validate --client claude-desktop
mcp-config validate --client intellij

# List shows servers from commented configs (tested)
mcp-config list --client intellij --detailed
```

## Documentation Updates (Test-Driven)
### README Enhancement (After Tests Pass)
```markdown
## Universal JSON Comment Support ✨

**Key Feature**: All MCP configuration files preserve comments automatically!

- **Claude Desktop**: claude_desktop_config.json with comments
- **VSCode**: .vscode/mcp.json with comments  
- **IntelliJ/PyCharm**: GitHub Copilot mcp.json with comments

Same comment syntax, universal preservation - all tested!
```

## Comments (TDD Benefits)
- **Why test CLI integration**: Ensures universal comment support works end-to-end
- **Why test all clients**: CLI changes must work consistently across all handlers
- **Why test help accuracy**: Documentation must match actual functionality
- **Why comprehensive integration tests**: Universal changes affect entire CLI surface
