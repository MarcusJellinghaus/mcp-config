# Step 2: ClaudeCodeHandler Core Implementation

## LLM Prompt
```
Implement ClaudeCodeHandler class based on PR_Info/steps/summary.md and this step.

Create a new client handler for Claude Code that:
- Uses .mcp.json in project root (cwd)
- Adds "type": "stdio" to all server configurations
- Uses mcpServers section (like Claude Desktop)
- No metadata tracking (all servers are managed)
- Normalizes server names using normalize_server_name() from Step 1
- Warns about user-level ~/.mcp.json if present

Follow TDD: write tests first, then implement the handler.
Reuse ClaudeDesktopHandler pattern for consistency.
```

## Context
Claude Code uses project-level configuration files (`.mcp.json`) with a slightly different format than other clients. We need to create a handler that follows the existing `ClientHandler` pattern while adapting for Claude Code specifics.

## WHERE: File Structure
```
src/mcp_config/clients/
├── base.py                 # EXISTING - Base class to extend
├── claude_code.py          # MODIFIED - Add ClaudeCodeHandler class
├── constants.py            # EXISTING - Reuse constants
├── utils.py                # EXISTING - Reuse utilities
└── __init__.py             # MODIFIED in Step 3

tests/test_config/
├── test_claude_code_handler.py   # MODIFIED - Add handler tests
└── ...
```

## WHAT: Class and Methods to Implement

### Main Class
```python
# File: src/mcp_config/clients/claude_code.py

class ClaudeCodeHandler(ClientHandler):
    """Handler for Claude Code project configuration (.mcp.json)."""
    
    def __init__(self, config_dir: Path | None = None):
        """
        Initialize handler with optional config directory.
        
        Args:
            config_dir: Directory for .mcp.json (defaults to cwd)
        """
    
    def get_config_path(self) -> Path:
        """Get path to .mcp.json in project root."""
    
    def load_config(self) -> dict[str, Any]:
        """Load existing .mcp.json configuration."""
    
    def save_config(self, config: dict[str, Any]) -> None:
        """Save .mcp.json with proper formatting."""
    
    def setup_server(self, server_name: str, server_config: dict[str, Any]) -> bool:
        """Add server to .mcp.json with type field and name normalization."""
    
    def remove_server(self, server_name: str) -> bool:
        """Remove server from .mcp.json (all servers removable)."""
    
    def list_managed_servers(self) -> list[dict[str, Any]]:
        """List all servers (all are managed in Claude Code)."""
    
    def list_all_servers(self) -> list[dict[str, Any]]:
        """List all servers (same as managed for Claude Code)."""
    
    def backup_config(self) -> Path:
        """Create backup with .mcp.backup_* pattern."""
    
    def validate_config(self) -> list[str]:
        """Validate config including type field requirement."""
```

### Helper Methods
```python
def _check_user_config_warning(self) -> None:
    """Check for user-level .mcp.json and print warning if exists."""

def _add_type_field(self, server_config: dict[str, Any]) -> dict[str, Any]:
    """Add 'type': 'stdio' to server configuration."""

def _strip_metadata_fields(self, server_config: dict[str, Any]) -> dict[str, Any]:
    """Remove metadata fields like _server_type from config."""
```

## HOW: Integration Points

### Imports
```python
# File: src/mcp_config/clients/claude_code.py
import os
import platform
from pathlib import Path
from typing import Any

from .base import ClientHandler
from .constants import DEFAULT_CLAUDE_CONFIG  # Reuse mcpServers structure
from .utils import (
    backup_config,
    load_json_config,
    save_json_config,
    validate_server_config,
)
```

### Key Differences from ClaudeDesktopHandler
```python
# Reuse structure from ClaudeDesktopHandler but adapt:
# 1. get_config_path() -> return self.config_dir / ".mcp.json" (project-level)
# 2. setup_server() -> add "type": "stdio", normalize name, strip _server_type metadata
# 3. remove_server() -> no metadata checks (all servers are managed)
# 4. list_managed_servers() -> return all servers (no metadata file)
# 5. backup_config() -> use .mcp.backup_* naming (hidden files)
```

## ALGORITHM: Core Logic

### setup_server() Pseudocode
```
1. Normalize server name using normalize_server_name()
2. Print normalization message if name changed (Decision #13: show every time)
3. Check and warn about user-level config (Decision #2: informational only)
4. Create backup of existing config
5. Load current configuration
6. Strip metadata fields from server_config (_server_type, etc.) (Decision #4)
7. Add "type": "stdio" to server_config
8. Add server to config["mcpServers"]
9. Save updated configuration
10. Return True on success, False on failure
```

### remove_server() Pseudocode
```
1. Load current configuration
2. Check if server exists in mcpServers
3. Create backup of existing config
4. Remove server from config["mcpServers"]
5. Save updated configuration
6. Return True on success, False on failure
```

### _add_type_field() Pseudocode
```
1. Copy server_config to avoid mutation
2. Add "type": "stdio" to copy
3. Return modified config
```

### _strip_metadata_fields() Pseudocode
```
1. Copy server_config to avoid mutation
2. Remove _server_type field if present
3. Remove any other internal metadata fields
4. Return cleaned config
```

## DATA: Input/Output Specifications

### ClaudeCodeHandler.__init__()
- **Input**: `config_dir: Path | None` (optional)
- **Output**: None (initializes instance)
- **Side Effect**: Sets `self.config_dir` to `config_dir or Path.cwd()`

### get_config_path()
- **Input**: None
- **Output**: `Path` to `.mcp.json` file
- **Example**: `Path.cwd() / ".mcp.json"`

### setup_server()
- **Input**: 
  - `server_name: str` (may need normalization)
  - `server_config: dict[str, Any]` (without type field)
- **Output**: `bool` (True if successful)
- **Side Effects**: 
  - Prints normalization message
  - Prints user config warning
  - Creates backup file
  - Writes to `.mcp.json`

### Server Config Format
```python
# Input (from integration.py)
{
    "command": "python.exe",
    "args": ["--project-dir", "C:\\project"],
    "env": {"PYTHONPATH": "C:\\project\\"},
    "_server_type": "mcp-code-checker"  # metadata, should be removed
}

# Output (saved to .mcp.json)
{
    "mcpServers": {
        "my-server": {
            "type": "stdio",
            "command": "python.exe",
            "args": ["--project-dir", "C:\\project"],
            "env": {"PYTHONPATH": "C:\\project\\"}
        }
    }
}
```

### list_managed_servers() / list_all_servers()
- **Input**: None
- **Output**: `list[dict[str, Any]]`
- **Format**:
```python
[
    {
        "name": "my-server",
        "type": "mcp-code-checker",  # from inference or unknown
        "command": "python.exe",
        "args": [...],
        "env": {...},
        "managed": True  # always True for Claude Code
    }
]
```

## Test Cases to Implement

### Unit Tests (test_claude_code_handler.py)
```python
def test_get_config_path():
    """Test config path is cwd/.mcp.json"""

def test_load_config_creates_default():
    """Test loading non-existent config returns default structure"""

def test_save_config_creates_file():
    """Test saving config creates .mcp.json file"""

def test_setup_server_adds_type_field():
    """Test that type: stdio is added to server config"""

def test_setup_server_normalizes_name():
    """Test that server names are normalized"""

def test_setup_server_warns_user_config():
    """Test warning printed if ~/.mcp.json exists"""

def test_remove_server_success():
    """Test removing existing server"""

def test_remove_server_not_found():
    """Test removing non-existent server fails gracefully"""

def test_list_managed_servers():
    """Test listing servers returns all servers as managed"""

def test_backup_config_creates_hidden_file():
    """Test backup uses .mcp.backup_* pattern"""

def test_validate_config_basic():
    """Test basic configuration validation (structure, required fields)"""
```

## Implementation Order

1. **Update test file**: Add `ClaudeCodeHandler` tests to `tests/test_config/test_claude_code_handler.py`
2. **Write tests** for each method (RED)
3. **Implement** `ClaudeCodeHandler` class in `src/mcp_config/clients/claude_code.py`
4. **Start with simple methods**: `__init__`, `get_config_path`, `load_config`, `save_config`
5. **Implement** `_add_type_field` helper
6. **Implement** `_check_user_config_warning` helper
7. **Implement** `setup_server` with normalization
8. **Implement** `remove_server`
9. **Implement** `list_managed_servers` and `list_all_servers`
10. **Implement** `backup_config` with custom naming
11. **Implement** `validate_config`
12. **Run tests** - all should pass (GREEN)

## Acceptance Criteria
- [ ] All test cases pass
- [ ] Handler follows ClientHandler interface
- [ ] Reuses utilities from clients/utils.py
- [ ] Adds "type": "stdio" to all server configs
- [ ] Normalizes server names and notifies user
- [ ] Warns about user-level config if present
- [ ] No metadata file created or used
- [ ] Backup uses hidden file pattern (.mcp.backup_*)
- [ ] Code follows project style (type hints, docstrings)

## Notes
- Copy pattern from `ClaudeDesktopHandler` for consistency
- Key differences from ClaudeDesktopHandler:
  - `get_config_path()` returns project-level path (via config_dir parameter)
  - `setup_server()` strips metadata fields, adds type field, and normalizes names
  - No metadata file operations (all servers are managed)
  - Different backup naming convention (hidden files)
- User config warning is informational only (non-blocking) - Decision #2
- All servers in `.mcp.json` are considered managed (owned by this tool)
- **validate_config() does NOT check for type field** - Decision #5: users who manually edit are responsible for correctness

## Next Step
After completing this step, proceed to **Step 3: CLI Integration**
