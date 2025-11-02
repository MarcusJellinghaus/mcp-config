# Claude Code Configuration Support - Implementation Summary

## Overview
Add support for Claude Code project configuration (`.mcp.json`) to the mcp-config tool, enabling users to configure MCP servers for Claude Code CLI alongside existing support for Claude Desktop, VSCode, and IntelliJ.

## Issue Reference
- **Issue #31**: Add Claude Code Config Generation to mcp-config
- **Branch**: 31-add-claude-code-config-generation-to-mcp-config

## Goals
1. Generate `.mcp.json` files in project root for Claude Code
2. Support `"type": "stdio"` requirement for all servers
3. Validate and normalize server names to Claude Code requirements
4. Provide consistent CLI experience with existing clients
5. Maintain KISS principle - minimal, maintainable code

## Architectural & Design Changes

### 1. New Client Handler
**File**: `src/mcp_config/clients/claude_code.py`

Following the existing `ClientHandler` pattern, we add `ClaudeCodeHandler` class that:
- Extends `ClientHandler` base class
- Uses `.mcp.json` in current working directory (project root)
- Adds `"type": "stdio"` field to all server configurations
- Uses `mcpServers` section (like Claude Desktop)
- **Simplification**: No metadata tracking - all servers treated as managed
- **Simplification**: No separate metadata file needed

**Key Design Decision**: Reuse `ClaudeDesktopHandler` structure but adapt for:
- Project-level config location (cwd) vs user-level
- Required `"type": "stdio"` field
- Hidden backup naming (`.mcp.backup_*` vs `claude_desktop_config_backup_*`)
- All servers are removable (no metadata distinction)

### 2. Server Name Validation
**File**: `src/mcp_config/clients/claude_code.py`

Add server name normalization to meet Claude Code requirements:
- **Pattern**: `^[a-zA-Z0-9_-]{1,64}$`
- **Normalization**: Spaces → underscores, invalid chars removed
- **Length**: Truncate to 64 characters
- **User Feedback**: Display normalization message when name changes

**Design Decision**: Simple inline function vs complex validation framework (KISS principle)

### 3. User Config Warning
**File**: `src/mcp_config/clients/claude_code.py`

Check for user-level `.mcp.json` at `~/.mcp.json` and warn about undefined interaction:
- Simple existence check in `setup_server()`
- Warning message displayed once during setup
- No blocking behavior - just informational

### 4. Client Registration
**File**: `src/mcp_config/clients/__init__.py`

Register new handler in `CLIENT_HANDLERS` dict:
```python
"claude-code": ClaudeCodeHandler
```

### 5. CLI Integration
**Files**: `src/mcp_config/main.py`, `src/mcp_config/cli_utils.py`

Add `claude-code` as client choice in argument parser:
- Reuse existing `--client` parameter
- No new CLI parameters needed (uses cwd by default)
- All existing commands work: setup, remove, list, validate

### 6. Help System
**File**: `src/mcp_config/help_system.py`

Add Claude Code documentation:
- Command examples with `--client claude-code`
- Basic `.mcp.json` explanation
- Integration guidance

### 7. Documentation
**Files**: `README.md`, `USER_GUIDE.md`

Update user-facing documentation:
- Add Claude Code to supported clients list
- Quick start examples
- Configuration file location explanation

## Files to Create or Modify

### New Files (1)
1. `src/mcp_config/clients/claude_code.py` - ClaudeCodeHandler implementation

### Modified Files (6)
1. `src/mcp_config/clients/__init__.py` - Register handler
2. `src/mcp_config/help_system.py` - Add help documentation
3. `README.md` - Add Claude Code to supported clients
4. `USER_GUIDE.md` - Add usage documentation
5. `tests/test_config/test_claude_code_handler.py` - Unit tests (NEW TEST FILE)
6. `tests/test_config/test_claude_code_integration.py` - Integration tests (NEW TEST FILE)

### Test Files (2 new)
1. `tests/test_config/test_claude_code_handler.py` - Handler unit tests
2. `tests/test_config/test_claude_code_integration.py` - CLI integration tests

## Key Simplifications (KISS Principle)

### What We're NOT Implementing (MVP Scope)
1. ❌ **Environment variable substitution** (`--use-env-vars`)
   - Complex feature requiring path detection, platform-specific variables
   - Users can manually edit `.mcp.json` if needed
   - **Recommendation**: Add in Phase 2 if user demand exists

2. ❌ **Custom config directory** (`--config-dir`)
   - Always use current working directory (project root)
   - Matches Claude Code's project-based model
   - Users run command from project directory

3. ❌ **Complex validation framework**
   - Simple inline normalization function
   - Immediate user feedback via print statements

### What We're Keeping Simple
1. ✅ **Copy-paste pattern** from `ClaudeDesktopHandler`
   - Same `mcpServers` structure
   - Minimal changes for Claude Code specifics
   - Proven, tested code base

2. ✅ **No metadata file**
   - All servers in `.mcp.json` are managed
   - Simpler remove logic (no ownership checks)
   - Matches project config model

3. ✅ **Basic help text**
   - Essential usage examples
   - No complex documentation system
   - Users learn by example

## Implementation Approach

### Test-Driven Development
Each step includes:
1. Write tests first (TDD)
2. Implement minimal code to pass tests
3. Verify integration
4. Move to next step

### Step Breakdown
1. **Step 1**: Server name normalization (utility function + tests)
2. **Step 2**: ClaudeCodeHandler core (handler class + tests)
3. **Step 3**: CLI integration (registration + argument handling)
4. **Step 4**: Help system updates (documentation)
5. **Step 5**: User documentation (README, USER_GUIDE)

## Success Criteria
- [ ] Can setup servers: `mcp-config setup <server> <name> --client claude-code`
- [ ] Generates valid `.mcp.json` in project root with `"type": "stdio"`
- [ ] Server names auto-normalized with user notification
- [ ] Warns about user-level `.mcp.json` if present
- [ ] List, remove, validate commands work with Claude Code
- [ ] Help available via `mcp-config help` (with claude-code examples)
- [ ] Documentation updated in README.md and USER_GUIDE.md
- [ ] All tests pass

## Non-Goals (Future Work)
- Environment variable substitution (`--use-env-vars`)
- Custom config directory support
- Advanced validation reporting
- Server name conflict resolution
- Migration tools from other clients

## Estimated Complexity
- **Lines of Code**: ~300 new lines (150 implementation + 150 tests)
- **Files Modified**: 6 files + 2 new test files
- **Implementation Time**: 4-6 hours with TDD approach
- **Risk Level**: Low (follows existing patterns)

## Dependencies
None - uses existing infrastructure

## Backward Compatibility
No breaking changes - purely additive feature
