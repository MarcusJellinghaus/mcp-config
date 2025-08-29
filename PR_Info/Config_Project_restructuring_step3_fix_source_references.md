# Step 3: Fix Source Code References

## Overview
Update all source code files to remove hardcoded references to "mcp-code-checker" and ensure consistent use of "mcp-config" throughout the codebase.

## Files to Update

### 1. src/mcp_config/servers.py
**Critical Issues Found:**
- Line ~239: Hardcoded server name check `if self.name == "mcp-code-checker":`
- Line ~304: CLI command name `return "mcp-code-checker"`  
- Line ~311: Installation mode detection for `mcp-code-checker`
- Line ~330: Import check for `mcp_code_checker` module
- Line ~355: Project validation logic specific to mcp-code-checker

**Required Changes:**
```python
# Current problematic code:
MCP_CODE_CHECKER = ServerConfig(
    name="mcp-code-checker",
    display_name="MCP Code Checker",
    main_module="src/main.py",
    # ... parameters
)

# Update to:
MCP_CODE_CHECKER = ServerConfig(
    name="mcp-code-checker",  # Keep this - it's the SERVER being configured
    display_name="MCP Code Checker",  # Keep this - it's the SERVER name
    main_module="src/main.py",  # This should stay as is
    # ... parameters (no changes needed)
)
```

**Note:** The ServerConfig for "mcp-code-checker" should remain because this tool CONFIGURES the mcp-code-checker server. The tool itself is mcp-config, but it configures mcp-code-checker servers.

### 2. src/mcp_config/__init__.py  
**Check for:**
- Module docstring references
- Import statements
- Function documentation

**Current Content Analysis:**
```python
"""MCP Configuration Helper - Main package initialization."""
```
This is correct - no changes needed.

### 3. src/mcp_config/main.py
**Check for:**
- CLI help text mentioning wrong project
- Error messages with incorrect references  
- Documentation strings

**Areas to Review:**
- Argument parser help text
- Error messages in exception handlers
- Function docstrings
- Print statements with project references

### 4. Other Module Files to Check
Review the following files for any hardcoded references:

**src/mcp_config/cli_utils.py:**
- Parser descriptions
- Help text
- Error messages

**src/mcp_config/clients.py:**
- Documentation strings
- Error messages  
- Configuration comments

**src/mcp_config/help_system.py:**
- Help text content
- Documentation references
- Example outputs

**src/mcp_config/output.py:**
- Print statements
- Error messages
- Status messages

**src/mcp_config/validation.py:**
- Error messages
- Documentation strings
- Validation messages

## Important Distinction

**Key Concept:** This tool is `mcp-config` (the configuration helper), but it configures `mcp-code-checker` servers (among others potentially in the future).

**Keep These References:**
- Server name: "mcp-code-checker" (this is what we're configuring)
- Server display name: "MCP Code Checker" (this is what we're configuring)
- Module paths for the server being configured

**Change These References:**
- References to this tool being called "mcp-code-checker" 
- Help text saying this IS the code checker (it's the config tool)
- Import paths that assume this is the code checker project
- Repository URLs in comments

## Specific Search and Replace Patterns

### Strings to Update:
- CLI help descriptions that describe this as a code checking tool
- Error messages that refer to the wrong project name
- Import statements for wrong module names
- Repository URLs in comments or strings

### Strings to Keep:
- `name="mcp-code-checker"` in ServerConfig (this is the server type)
- `display_name="MCP Code Checker"` in ServerConfig (this is the server name)
- References to mcp-code-checker as the thing being configured
- Module paths for the server: "src/main.py" (relative to the project being configured)

## Files Likely Needing Updates

1. **src/mcp_config/help_system.py** - Help text and documentation
2. **src/mcp_config/cli_utils.py** - Parser descriptions  
3. **src/mcp_config/main.py** - Error messages and help text
4. **src/mcp_config/output.py** - Status and error messages
5. **src/mcp_config/validation.py** - Validation error messages

## Validation Steps
1. Search entire codebase for "This is mcp-code-checker" type references
2. Verify help text describes mcp-config's purpose (configuration management)
3. Check error messages don't claim to be the code checker
4. Ensure server configuration still correctly references mcp-code-checker
5. Test CLI help output for correct tool description

## Expected Result
- Source code correctly identifies this tool as mcp-config
- Help text describes MCP server configuration functionality  
- Server configurations still correctly reference mcp-code-checker as the server type
- Error messages and documentation are consistent
- No confusion between the config tool and the servers it configures

## Next Step
After completing this step, proceed to Step 4: Fix Import Statements and Module References.
