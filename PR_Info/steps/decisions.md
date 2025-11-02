# Implementation Decisions

This document records decisions made during the planning review discussion.

## Decision Log

### 1. Documentation Level - Step 1
**Decision**: Keep both ALGORITHM and HOW sections in Step 1  
**Rationale**: Comprehensive documentation preferred even if some overlap exists  
**Date**: 2025-11-02

### 2. User Config Warning (~/.mcp.json)
**Decision**: Keep the user-level config warning as planned  
**Rationale**: Simple informational message, non-blocking, useful for user awareness  
**Implementation**: Simple existence check in `setup_server()`, print warning once during setup  
**Date**: 2025-11-02

### 3. Backup File Naming Pattern
**Decision**: Use `.mcp.backup_*` pattern (hidden files with leading dot)  
**Rationale**: Cleaner project directory, hidden backups on Unix systems  
**Date**: 2025-11-02

### 4. Metadata Removal Pattern
**Decision**: Confirmed standard pattern - `integration.py` adds `_server_type`, handlers strip it  
**Implementation**: ClaudeCodeHandler should remove `_server_type` field before saving to `.mcp.json`  
**Note**: No separate metadata file for Claude Code (unlike Claude Desktop/VSCode)  
**Date**: 2025-11-02

### 5. Type Field Validation
**Decision**: No validation for manually edited configs  
**Rationale**: Users who manually edit `.mcp.json` are responsible for correctness  
**Implementation**: `validate_config()` does NOT check for `type` field presence  
**Date**: 2025-11-02

### 6. Empty String Normalization Edge Case
**Decision**: Raise `ValueError` if normalization results in empty string  
**Rationale**: Better to fail fast with clear error than save invalid config  
**Implementation**: Add check in `normalize_server_name()` after normalization  
**Error Message**: "Server name contains no valid characters after normalization"  
**Date**: 2025-11-02

### 7. Backup File Cleanup
**Decision**: No guidance or tooling for backup cleanup  
**Rationale**: Users can manually delete old backups when needed  
**Date**: 2025-11-02

### 8. Step 2 Documentation Structure
**Decision**: Keep WHAT and HOW sections separate, remove duplicate method signatures  
**Implementation**: Remove method signature details from HOW section since they're in WHAT  
**Date**: 2025-11-02

### 9. Test File Organization
**Decision**: Keep separate test files as planned  
**Files**: `test_claude_code_handler.py` and `test_claude_code_integration.py`  
**Rationale**: Clearer and easier to maintain than parametrized cross-client tests  
**Date**: 2025-11-02

### 10. --project-dir Parameter
**Decision**: Keep `--project-dir .` in all examples  
**Rationale**: Serves different purpose than `config_dir`:
  - `--project-dir`: Where MCP server operates (works on code)
  - `config_dir`: Where `.mcp.json` is created (handler location)  
**Note**: These are two distinct directories with different purposes  
**Date**: 2025-11-02

### 11. Known Limitations Section
**Decision**: Do NOT add "Known Limitations" section  
**Rationale**: Keep plan focused on implementation, not what we're not building  
**Date**: 2025-11-02

### 12. Invalid JSON Error Handling
**Decision**: Rely on existing `load_json_config` utility  
**Rationale**: Utilities should already handle corrupted JSON gracefully  
**Implementation**: No additional test cases needed for this scenario  
**Date**: 2025-11-02

### 13. Normalization Message Frequency
**Decision**: Show normalization message every time a name is changed  
**Rationale**: Users should always know when their server name was modified  
**Implementation**: Print message in `setup_server()` whenever `was_modified == True`  
**Date**: 2025-11-02

## Summary

All decisions support the KISS principle and maintain consistency with existing handler patterns. The plan is approved for implementation with only minor adjustments needed in Steps 1 and 2.
