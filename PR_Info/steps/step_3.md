# Step 3: CLI Integration

## LLM Prompt
```
Integrate ClaudeCodeHandler into the CLI based on PR_Info/steps/summary.md and this step.

Register the new handler and make it available via --client claude-code option.
Ensure all commands (setup, remove, list, validate) work with Claude Code.

Follow TDD: write integration tests first, then implement registration.
```

## Context
Now that we have a working `ClaudeCodeHandler`, we need to integrate it into the CLI so users can access it via the `--client claude-code` option. This involves registering the handler and ensuring all existing commands work correctly.

## WHERE: File Structure
```
src/mcp_config/clients/
├── __init__.py             # MODIFIED - Register ClaudeCodeHandler
└── ...

src/mcp_config/
├── main.py                 # VERIFY - Should work without changes
└── cli_utils.py            # VERIFY - Should work without changes

tests/test_config/
├── test_claude_code_integration.py   # NEW - CLI integration tests
└── ...
```

## WHAT: Changes to Implement

### 1. Register Handler
```python
# File: src/mcp_config/clients/__init__.py

from .claude_code import ClaudeCodeHandler  # NEW IMPORT

CLIENT_HANDLERS: dict[str, HandlerFactory] = {
    "claude-desktop": ClaudeDesktopHandler,
    "vscode-workspace": lambda: VSCodeHandler(workspace=True),
    "vscode-user": lambda: VSCodeHandler(workspace=False),
    "intellij": IntelliJHandler,
    "claude-code": ClaudeCodeHandler,  # NEW ENTRY
}

__all__ = [
    "ClientHandler",
    "ClaudeDesktopHandler",
    "IntelliJHandler",
    "VSCodeHandler",
    "ClaudeCodeHandler",  # NEW EXPORT
    "get_client_handler",
    "CLIENT_HANDLERS",
    "HandlerFactory",
]
```

### 2. Verify CLI Argument Parser
```python
# File: src/mcp_config/cli_utils.py or main.py
# NO CHANGES NEEDED - should already support dynamic client choices

# The --client argument should automatically pick up "claude-code" from CLIENT_HANDLERS
# Verify this works in tests
```

### 3. Integration Tests
```python
# File: tests/test_config/test_claude_code_integration.py

def test_setup_command_with_claude_code():
    """Test mcp-config setup with --client claude-code"""

def test_remove_command_with_claude_code():
    """Test mcp-config remove with --client claude-code"""

def test_list_command_with_claude_code():
    """Test mcp-config list --client claude-code"""

def test_validate_command_with_claude_code():
    """Test mcp-config validate with --client claude-code"""

def test_dry_run_with_claude_code():
    """Test --dry-run with --client claude-code"""
```

## HOW: Integration Points

### Handler Registration
```python
# The get_client_handler() function already exists and works with dict lookup
# Just add "claude-code" to CLIENT_HANDLERS and it will work automatically

def get_client_handler(client_name: str) -> ClientHandler:
    """Get client handler by name."""
    if client_name not in CLIENT_HANDLERS:
        raise ValueError(f"Unknown client: {client_name}")
    
    handler_factory = CLIENT_HANDLERS[client_name]
    # ClaudeCodeHandler is a class, so instantiate it
    return handler_factory()
```

### CLI Flow (Existing - Verify)
```
User runs: mcp-config setup mcp-code-checker "my-server" --client claude-code
    ↓
main.py parses args.client = "claude-code"
    ↓
get_client_handler("claude-code") returns ClaudeCodeHandler instance
    ↓
Existing setup logic works with ClaudeCodeHandler
    ↓
ClaudeCodeHandler.setup_server() called with server config
    ↓
.mcp.json created in current directory
```

## ALGORITHM: Core Logic

### Registration (One-time)
```
1. Import ClaudeCodeHandler in __init__.py
2. Add "claude-code": ClaudeCodeHandler to CLIENT_HANDLERS dict
3. Add ClaudeCodeHandler to __all__ exports
4. No other changes needed - existing infrastructure handles the rest
```

### Verification Strategy
```
1. Test that get_client_handler("claude-code") returns ClaudeCodeHandler
2. Test that --client claude-code is accepted by CLI
3. Test each command (setup, remove, list, validate) with --client claude-code
4. Test dry-run mode with --client claude-code
5. Verify error messages for unknown clients still work
```

## DATA: Input/Output Specifications

### get_client_handler() Behavior
```python
# Input
client_name = "claude-code"

# Output
handler = ClaudeCodeHandler()  # Instance of handler
assert isinstance(handler, ClientHandler)
assert isinstance(handler, ClaudeCodeHandler)
```

### CLI Commands
```bash
# Setup
mcp-config setup mcp-code-checker "test-server" --client claude-code --project-dir .
# Expected: Creates .mcp.json in cwd with normalized name

# List
mcp-config list --client claude-code
# Expected: Shows servers from .mcp.json in cwd

# Remove
mcp-config remove "test-server" --client claude-code
# Expected: Removes server from .mcp.json

# Validate
mcp-config validate "test-server" --client claude-code
# Expected: Validates server configuration

# Dry-run
mcp-config setup mcp-code-checker "test" --client claude-code --project-dir . --dry-run
# Expected: Shows what would be done without creating files
```

## Test Cases to Implement

### Integration Tests (test_claude_code_integration.py)
```python
def test_get_client_handler_returns_claude_code():
    """Test handler registration works"""

def test_setup_creates_mcp_json():
    """Test setup command creates .mcp.json in cwd"""

def test_setup_with_normalization():
    """Test setup normalizes server name and prints message"""

def test_list_shows_all_servers():
    """Test list command shows all servers as managed"""

def test_remove_deletes_server():
    """Test remove command deletes from .mcp.json"""

def test_validate_checks_type_field():
    """Test validate requires type: stdio"""

def test_dry_run_shows_preview():
    """Test --dry-run shows config without creating files"""

def test_unknown_client_error():
    """Test that invalid client name shows helpful error"""

def test_multiple_clients_list():
    """Test list without --client shows all clients including claude-code"""
```

## Implementation Order

1. **Create integration test file**: `tests/test_config/test_claude_code_integration.py`
2. **Write tests** for handler registration (RED)
3. **Update** `src/mcp_config/clients/__init__.py` to register handler
4. **Run registration tests** - should pass (GREEN)
5. **Write tests** for CLI commands (setup, remove, list, validate)
6. **Verify** existing CLI code handles new handler (should work without changes)
7. **Run all integration tests** - should pass (GREEN)
8. **Manual testing** - run actual CLI commands to verify

## Acceptance Criteria
- [ ] ClaudeCodeHandler registered in CLIENT_HANDLERS
- [ ] `get_client_handler("claude-code")` returns ClaudeCodeHandler instance
- [ ] `--client claude-code` accepted by all commands
- [ ] Setup command creates `.mcp.json` in cwd
- [ ] Remove command removes from `.mcp.json`
- [ ] List command shows servers from `.mcp.json`
- [ ] Validate command checks `.mcp.json` servers
- [ ] Dry-run works with claude-code client
- [ ] Error handling works (unknown client, missing config, etc.)
- [ ] All integration tests pass

## Notes
- **Minimal changes required** - existing CLI infrastructure is designed to handle new clients
- Only need to register the handler - no CLI code changes
- Focus tests on end-to-end CLI flows
- Verify that config path is cwd, not user config directory
- Test that backup files use `.mcp.backup_*` pattern

## Manual Testing Commands
```bash
# After implementation, manually test these commands

# Setup a server
cd /path/to/test/project
mcp-config setup mcp-code-checker "my server!" --client claude-code --project-dir .

# Verify .mcp.json created
cat .mcp.json
# Should see: normalized name, type: stdio, mcpServers structure

# List servers
mcp-config list --client claude-code

# Validate server
mcp-config validate "my_server" --client claude-code

# Remove server
mcp-config remove "my_server" --client claude-code

# Verify backup created
ls -la .mcp.backup_*
```

## Next Step
After completing this step, proceed to **Step 4: Help System Updates**
