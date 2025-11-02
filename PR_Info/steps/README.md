# Implementation Steps - Claude Code Support

This directory contains the step-by-step implementation plan for adding Claude Code configuration support to mcp-config (Issue #31).

## Quick Reference

### Implementation Overview
- **Feature**: Add Claude Code project configuration support (`.mcp.json`)
- **Approach**: TDD (Test-Driven Development)
- **Principle**: KISS - Keep It Simple
- **Estimated LOC**: ~300 lines (150 implementation + 150 tests)

### Files Created/Modified
**New Files (3)**:
- `src/mcp_config/clients/claude_code.py` - Handler implementation
- `tests/test_config/test_claude_code_handler.py` - Unit tests
- `tests/test_config/test_claude_code_integration.py` - Integration tests

**Modified Files (6)**:
- `src/mcp_config/clients/__init__.py` - Register handler
- `src/mcp_config/help_system.py` - Add help documentation
- `README.md` - Update quick start and supported clients
- `USER_GUIDE.md` - Add Claude Code configuration section
- (No changes needed to `main.py` or `cli_utils.py` - existing infrastructure handles new client)

## Step-by-Step Plan

### [Summary](summary.md)
Read this first for architectural overview, design decisions, and scope.

### [Step 1: Server Name Normalization](step_1.md)
**Goal**: Implement utility function to normalize server names for Claude Code requirements

**Key Activities**:
- Create test file with normalization test cases
- Implement `normalize_server_name()` function
- Handle spaces, invalid characters, length truncation
- Return tuple: `(normalized_name, was_modified)`

**TDD**: Write tests → Run (RED) → Implement → Run (GREEN)

**Acceptance**: All test cases pass, handles edge cases

---

### [Step 2: ClaudeCodeHandler Core](step_2.md)
**Goal**: Implement complete ClaudeCodeHandler class

**Key Activities**:
- Write unit tests for all handler methods
- Implement `ClaudeCodeHandler` extending `ClientHandler`
- Key methods: `get_config_path()`, `setup_server()`, `remove_server()`, `list_*_servers()`
- Add `"type": "stdio"` field
- Integrate server name normalization
- Add user config warning check
- Use project root (cwd) for `.mcp.json`
- No metadata tracking (all servers are managed)

**TDD**: Write tests → Run (RED) → Implement → Run (GREEN)

**Acceptance**: All unit tests pass, handler follows base interface

---

### [Step 3: CLI Integration](step_3.md)
**Goal**: Register handler and enable CLI access

**Key Activities**:
- Write integration tests for CLI commands
- Register `ClaudeCodeHandler` in `CLIENT_HANDLERS`
- Verify existing CLI handles new client without changes
- Test all commands: setup, remove, list, validate, dry-run

**TDD**: Write tests → Register handler → Run (GREEN)

**Acceptance**: All CLI commands work with `--client claude-code`

---

### [Step 4: Help System Updates](step_4.md)
**Goal**: Add Claude Code to help documentation

**Key Activities**:
- Update `format_tool_overview()` to include claude-code
- Add claude-code to all command help (setup, remove, list, validate)
- Add examples showing claude-code usage
- Follow existing formatting patterns

**No Tests**: Documentation only

**Acceptance**: Help commands show claude-code correctly

---

### [Step 5: Documentation Updates](step_5.md)
**Goal**: Update user-facing documentation

**Key Activities**:
- Add Claude Code to README.md (Quick Start, Supported Clients)
- Add complete Claude Code section to USER_GUIDE.md
- Include: location, setup, format, naming, commands, best practices
- Ensure examples are accurate and tested

**No Tests**: Documentation only

**Acceptance**: Documentation is clear, accurate, and complete

---

## Implementation Order

Execute steps sequentially:
1. **Step 1** → Normalization utility (foundation)
2. **Step 2** → Handler implementation (core logic)
3. **Step 3** → CLI integration (make it accessible)
4. **Step 4** → Help system (in-app documentation)
5. **Step 5** → User docs (external documentation)

Each step builds on the previous one. Complete all tests before moving to the next step.

## Testing Strategy

### Unit Tests (Steps 1-2)
- Test individual functions and methods
- Mock file system operations where appropriate
- Cover edge cases and error handling

### Integration Tests (Step 3)
- Test end-to-end CLI flows
- Verify file creation and modification
- Test all commands with claude-code client

### Manual Testing (Steps 4-5)
- Run actual CLI commands
- Verify help output
- Check documentation rendering

## Key Design Decisions

### ✅ What We're Implementing
1. Basic Claude Code support with `.mcp.json` in project root
2. `"type": "stdio"` field requirement
3. Server name normalization with user notification
4. User config warning for `~/.mcp.json`
5. All servers treated as managed (no metadata)
6. Hidden backup pattern (`.mcp.backup_*.json`)

### ❌ What We're Deferring (Future Work)
1. Environment variable substitution (`--use-env-vars`)
2. Custom config directory support (`--config-dir`)
3. Complex validation frameworks
4. Server name conflict resolution
5. Migration tools from other clients

### KISS Simplifications
- Reuse `ClaudeDesktopHandler` pattern extensively
- No new CLI parameters (uses cwd by default)
- Simple inline normalization (no validation framework)
- One-line user config warning (no blocking)
- Copy-paste help text patterns (no abstraction)

## Success Criteria

### Functional Requirements
- [ ] Can setup servers with `--client claude-code`
- [ ] Creates `.mcp.json` in project root
- [ ] Adds `"type": "stdio"` to all servers
- [ ] Normalizes server names and notifies users
- [ ] Warns about user-level `.mcp.json`
- [ ] All commands work (setup, remove, list, validate)

### Quality Requirements
- [ ] All tests pass
- [ ] Code follows project style
- [ ] Help system updated
- [ ] Documentation complete
- [ ] No breaking changes
- [ ] Minimal code changes (~300 LOC)

## Getting Started

1. Read [summary.md](summary.md) for full context
2. Review [decisions.md](decisions.md) for planning decisions and rationale
3. Start with [step_1.md](step_1.md)
4. Follow TDD approach strictly
5. Complete each step fully before moving on
6. Run tests after each step
7. Review and refactor if needed

## Questions?

Refer back to:
- **Summary** for architectural decisions
- **Decisions.md** for planning review decisions and rationale
- **Individual steps** for specific implementation details
- **Issue #31** for original requirements
- **Existing handlers** (ClaudeDesktopHandler, VSCodeHandler) for patterns
