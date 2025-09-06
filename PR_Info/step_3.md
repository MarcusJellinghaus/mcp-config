# Step 3: IntelliJ Client Handler Implementation

## LLM Prompt
```
Referring to the Summary: IntelliJ MCP Client Support with JSON Comments, implement Step 3: Complete the IntelliJHandler class implementation following the existing ClientHandler pattern. Use the JSON comments utility from Step 1 and implement all required methods. Follow TDD approach with comprehensive tests.
```

## WHERE
- **Files**:
  - `src/mcp_config/clients.py` (update)
  - `tests/test_config/test_intellij_handler.py` (new)

## WHAT
### Main Class
```python
class IntelliJHandler(ClientHandler):
    def get_config_path(self) -> Path
    def load_config(self) -> dict[str, Any] 
    def save_config(self, config: dict[str, Any]) -> None
    def setup_server(self, server_name: str, server_config: dict[str, Any]) -> bool
    def remove_server(self, server_name: str) -> bool
    def list_managed_servers(self) -> list[dict[str, Any]]
    def list_all_servers(self) -> list[dict[str, Any]]
    def backup_config(self) -> Path
    def validate_config(self) -> list[str]
```

### Registry Update
```python
# Add to CLIENT_HANDLERS
CLIENT_HANDLERS["intellij"] = IntelliJHandler
```

## HOW
### Integration Points
- **Inheritance**: Extend `ClientHandler` abstract base class
- **JSON Handling**: Use `load_json_with_comments()` and `save_json_with_comments()` from Step 1
- **Path Detection**: Implement `get_config_path()` method (from Step 2)
- **Metadata**: Follow same `.mcp-config-metadata.json` pattern as VSCode

### Config Structure
```python
# IntelliJ config format (similar to VSCode)
{
    "servers": {
        "server-name": {
            "command": "python",
            "args": ["script.py"],
            "env": {"VAR": "value"}  # optional
        }
    }
}
```

## ALGORITHM
```
1. Initialize handler (no special config needed)
2. For load: Use JSON comments utility from Step 1
3. For save: Preserve existing comments using json-five
4. For setup: Clean config (no metadata) + separate metadata file
5. For remove: Check metadata ownership before deletion
6. Use existing backup pattern from other handlers
```

## DATA
### Class Constants
```python
class IntelliJHandler(ClientHandler):
    MANAGED_SERVER_MARKER = "mcp-config-managed"
    METADATA_FILE = ".mcp-config-metadata.json"
    CONFIG_SECTION = "servers"  # Like VSCode, not "mcpServers"
```

### Return Values
- Methods return same types as other ClientHandler implementations
- `load_config()`: `dict[str, Any]` with `{"servers": {}}` default
- `list_*()`: `list[dict[str, Any]]` with server info dictionaries

## Tests to Write First
1. **Test config path detection** across platforms
2. **Test load/save with comments** preservation  
3. **Test server setup/removal** with metadata handling
4. **Test list operations** (managed vs all servers)
5. **Test validation** of IntelliJ config format
6. **Test backup creation** and restoration
7. **Test comment preservation** during modifications
8. **Test metadata separation** (no metadata in main config)
9. **Test error handling** for malformed configs
10. **Test integration** with existing client registry
