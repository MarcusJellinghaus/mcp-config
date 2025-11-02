# Step 4: Help System Updates

## LLM Prompt
```
Update the help system to include Claude Code support based on PR_Info/steps/summary.md and this step.

Add Claude Code examples to command help and create basic documentation for .mcp.json usage.
Keep changes minimal - just add Claude Code to existing patterns.

No tests required for this step - documentation only.
```

## Context
The help system already has comprehensive documentation for other clients (Claude Desktop, VSCode, IntelliJ). We need to add Claude Code examples following the same patterns.

## WHERE: File Structure
```
src/mcp_config/
├── help_system.py          # MODIFIED - Add claude-code examples
└── ...
```

## WHAT: Changes to Implement

### 1. Update Tool Overview
```python
# File: src/mcp_config/help_system.py
# Location: CommandHelpFormatter.format_tool_overview()

# CURRENT:
"🚀 Multi-Client Support:",
"  claude-desktop  → claude_desktop_config.json",
"  vscode-*        → .vscode/mcp.json",
"  intellij        → GitHub Copilot mcp.json",

# NEW:
"🚀 Multi-Client Support:",
"  claude-desktop  → claude_desktop_config.json",
"  claude-code     → .mcp.json (project root)",
"  vscode-*        → .vscode/mcp.json",
"  intellij        → GitHub Copilot mcp.json",
```

### 2. Update Setup Command Help
```python
# File: src/mcp_config/help_system.py
# Location: CommandHelpFormatter.format_setup_command_help()

# Add to "COMMAND OPTIONS" section:
"--client CHOICE    MCP client to configure [default: claude-desktop]",
"                   Choices: claude-desktop, claude-code, vscode-workspace, vscode-user, intellij",

# Add to "DETAILED OPTION DESCRIPTIONS" section (if verbose):
"  --client:",
"    Specifies which MCP client to configure:",
"    • claude-desktop: Claude Desktop app configuration",
"    • claude-code: Claude Code CLI project configuration (.mcp.json)",
"    • vscode-workspace: VSCode workspace .vscode/mcp.json (team sharing)",
"    • vscode-user: VSCode user profile (personal, all projects)",
"    • intellij: IntelliJ/PyCharm GitHub Copilot integration",

# Add to "EXAMPLES" section:
"  # Setup for Claude Code project",
"  mcp-config setup mcp-code-checker code-proj --project-dir . --client claude-code",
```

### 3. Update Remove Command Help
```python
# File: src/mcp_config/help_system.py
# Location: CommandHelpFormatter.format_remove_command_help()

# Update client choices:
"--client CHOICE    MCP client to configure [default: claude-desktop]",
"                   Choices: claude-desktop, claude-code, vscode-workspace, vscode-user, intellij",

# Add to "EXAMPLES" section:
"  # Remove from Claude Code project",
"  mcp-config remove code-proj --client claude-code",
```

### 4. Update List Command Help
```python
# File: src/mcp_config/help_system.py
# Location: CommandHelpFormatter.format_list_command_help()

# Update client choices:
"--client CHOICE    MCP client to query [default: all clients]",
"                   Choices: claude-desktop, claude-code, vscode-workspace, vscode-user, intellij",

# Add to "EXAMPLES" section:
"  mcp-config list --client claude-code",
```

### 5. Update Validate Command Help
```python
# File: src/mcp_config/help_system.py
# Location: CommandHelpFormatter.format_validate_command_help()

# Update client choices:
"--client CHOICE    MCP client to validate [default: claude-desktop]",
"                   Choices: claude-desktop, claude-code, vscode-workspace, vscode-user, intellij",

# Add to "EXAMPLES" section:
"  mcp-config validate code-proj --client claude-code",
```

## HOW: Integration Points

### Approach
1. Search for all instances of client choices in help text
2. Add `claude-code` to the list following alphabetical order
3. Add one example per command showing Claude Code usage
4. Keep formatting consistent with existing examples

### No New Functions
All changes are string modifications within existing methods. No new functions or classes needed.

## ALGORITHM: Core Logic

### Update Process
```
1. Open src/mcp_config/help_system.py
2. Find CommandHelpFormatter.format_tool_overview()
   → Add claude-code to multi-client list
3. Find CommandHelpFormatter.format_setup_command_help()
   → Update --client choices
   → Add to detailed descriptions
   → Add example
4. Find CommandHelpFormatter.format_remove_command_help()
   → Update --client choices
   → Add example
5. Find CommandHelpFormatter.format_list_command_help()
   → Update --client choices
   → Add example
6. Find CommandHelpFormatter.format_validate_command_help()
   → Update --client choices
   → Add example
7. Save file
8. Test: run mcp-config help commands
```

## DATA: Modified Strings

### Client Choice Pattern (Reusable)
```python
# BEFORE:
"Choices: claude-desktop, vscode-workspace, vscode-user, intellij"

# AFTER:
"Choices: claude-desktop, claude-code, vscode-workspace, vscode-user, intellij"
```

### Client Description Pattern (Reusable)
```python
# BEFORE:
"  • claude-desktop: Claude Desktop app configuration"
"  • vscode-workspace: VSCode workspace .vscode/mcp.json (team sharing)"
"  • vscode-user: VSCode user profile (personal, all projects)"
"  • intellij: IntelliJ/PyCharm GitHub Copilot integration"

# AFTER:
"  • claude-desktop: Claude Desktop app configuration"
"  • claude-code: Claude Code CLI project configuration (.mcp.json)"
"  • vscode-workspace: VSCode workspace .vscode/mcp.json (team sharing)"
"  • vscode-user: VSCode user profile (personal, all projects)"
"  • intellij: IntelliJ/PyCharm GitHub Copilot integration"
```

### Example Pattern (Per Command)
```python
# Setup example:
"  # Setup for Claude Code project",
"  mcp-config setup mcp-code-checker code-proj --project-dir . --client claude-code",

# Remove example:
"  # Remove from Claude Code project",
"  mcp-config remove code-proj --client claude-code",

# List example:
"  mcp-config list --client claude-code",

# Validate example:
"  mcp-config validate code-proj --client claude-code",
```

## Implementation Order

1. **Open file**: `src/mcp_config/help_system.py`
2. **Update** `format_tool_overview()` - add claude-code to overview
3. **Update** `format_setup_command_help()` - choices, descriptions, examples
4. **Update** `format_remove_command_help()` - choices, examples
5. **Update** `format_list_command_help()` - choices, examples
6. **Update** `format_validate_command_help()` - choices, examples
7. **Save** file
8. **Manual test** - run help commands and verify output

## Acceptance Criteria
- [ ] `mcp-config help` shows claude-code in multi-client list
- [ ] `mcp-config help setup` includes claude-code in choices and examples
- [ ] `mcp-config help remove` includes claude-code in choices and examples
- [ ] `mcp-config help list` includes claude-code in choices and examples
- [ ] `mcp-config help validate` includes claude-code in choices and examples
- [ ] All new text follows existing formatting patterns
- [ ] Examples are clear and consistent with other clients
- [ ] No formatting errors (alignment, indentation, etc.)

## Manual Testing Commands
```bash
# After implementation, verify these commands display correctly:

mcp-config help
# Should show claude-code in overview

mcp-config help setup
# Should show claude-code in choices and examples

mcp-config help setup --verbose
# Should show claude-code in detailed descriptions

mcp-config help remove
# Should show claude-code in examples

mcp-config help list
# Should show claude-code in examples

mcp-config help validate
# Should show claude-code in examples

mcp-config help all
# Should show claude-code throughout all sections
```

## Notes
- **Minimal changes**: Only string modifications, no logic changes
- **Consistency**: Follow existing patterns exactly
- **Alphabetical order**: claude-code comes before vscode-* in listings
- **Concise**: Keep examples short and focused
- **No tests needed**: This is documentation only
- **User-facing**: These changes directly impact what users see

## Next Step
After completing this step, proceed to **Step 5: Documentation Updates**
