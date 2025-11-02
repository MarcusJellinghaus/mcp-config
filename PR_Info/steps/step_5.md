# Step 5: Documentation Updates

## LLM Prompt
```
Update user documentation to include Claude Code support based on PR_Info/steps/summary.md and this step.

Add Claude Code to README.md and USER_GUIDE.md following existing patterns.
Keep changes minimal and focused on essential information.

No tests required for this step - documentation only.
```

## Context
The README.md and USER_GUIDE.md provide user-facing documentation. We need to add Claude Code as a supported client with quick start examples and basic usage guidance.

## WHERE: File Structure
```
.
├── README.md               # MODIFIED - Add Claude Code to quick start
├── USER_GUIDE.md          # MODIFIED - Add Claude Code section
└── ...
```

## WHAT: Changes to Implement

### 1. Update README.md

#### Add to Quick Start Section
```markdown
# BEFORE (Quick Start section):
# Setup for Claude Desktop
mcp-config setup mcp-code-checker "My Project" --project-dir .

# Setup for VSCode (team projects)
mcp-config setup mcp-code-checker "My Project" --client vscode-workspace --project-dir .

# Setup for IntelliJ/PyCharm (GitHub Copilot)
mcp-config setup mcp-code-checker "My Project" --client intellij --project-dir .

# AFTER:
# Setup for Claude Desktop
mcp-config setup mcp-code-checker "My Project" --project-dir .

# Setup for Claude Code (project-level)
mcp-config setup mcp-code-checker "My Project" --client claude-code --project-dir .

# Setup for VSCode (team projects)
mcp-config setup mcp-code-checker "My Project" --client vscode-workspace --project-dir .

# Setup for IntelliJ/PyCharm (GitHub Copilot)
mcp-config setup mcp-code-checker "My Project" --client intellij --project-dir .
```

#### Update Supported Clients Section
```markdown
# BEFORE:
## Supported Clients

- **Claude Desktop** - claude_desktop_config.json
- **VSCode** - .vscode/mcp.json  
- **IntelliJ/PyCharm** - GitHub Copilot mcp.json

# AFTER:
## Supported Clients

- **Claude Desktop** - claude_desktop_config.json (user-level)
- **Claude Code** - .mcp.json (project-level)
- **VSCode** - .vscode/mcp.json  
- **IntelliJ/PyCharm** - GitHub Copilot mcp.json
```

### 2. Update USER_GUIDE.md

#### Add Claude Code Section After Claude Desktop
```markdown
## Claude Code Configuration

Claude Code uses project-level configuration files (`.mcp.json`) located in your project root directory.

### Configuration File Location
- **Path**: `.mcp.json` in your project root directory
- **Scope**: Project-level (each project has its own config)
- **Version Control**: Can be committed to Git for team sharing

### Setup Example
```bash
# Navigate to your project directory
cd /path/to/your/project

# Setup MCP server for this project
mcp-config setup mcp-code-checker "my-checker" --client claude-code --project-dir .

# Result: Creates .mcp.json in current directory
```

### Configuration Format
```json
{
  "mcpServers": {
    "my-checker": {
      "type": "stdio",
      "command": "python.exe",
      "args": ["--project-dir", "C:\\path\\to\\project"],
      "env": {"PYTHONPATH": "C:\\path\\"}
    }
  }
}
```

### Key Differences from Claude Desktop
- **Location**: Project root (cwd) vs user config directory
- **Type field**: Requires `"type": "stdio"` for all servers
- **Scope**: Per-project vs user-wide
- **Version control**: Typically committed to Git

### Server Name Requirements
Claude Code has specific naming requirements:
- **Pattern**: `[a-zA-Z0-9_-]` (letters, numbers, underscores, hyphens only)
- **Length**: 1-64 characters maximum
- **Auto-normalization**: Invalid characters are automatically normalized
  - Spaces → underscores
  - Invalid characters → removed
  - Names truncated to 64 characters

```bash
# Example: Server name normalization
mcp-config setup mcp-code-checker "my server!" --client claude-code --project-dir .
# ℹ️  Server name normalized: 'my server!' → 'my_server'
```

### Common Commands
```bash
# List servers in current project
mcp-config list --client claude-code

# Remove server from current project
mcp-config remove "my-checker" --client claude-code

# Validate server configuration
mcp-config validate "my-checker" --client claude-code

# Preview changes without applying
mcp-config setup mcp-code-checker "test" --client claude-code --project-dir . --dry-run
```

### Best Practices
1. **Run from project root**: Always run commands from your project directory
2. **Commit to Git**: Include `.mcp.json` in version control for team sharing
3. **Backup files**: Backups are created as hidden files (`.mcp.backup_*.json`)
4. **Consistent naming**: Use clear, descriptive server names following conventions
```

## HOW: Integration Points

### README.md Changes
1. Locate "Quick Start" section
2. Add Claude Code example after Claude Desktop example
3. Locate "Supported Clients" section
4. Add Claude Code between Claude Desktop and VSCode

### USER_GUIDE.md Changes
1. Find where Claude Desktop section is documented
2. Add new "Claude Code Configuration" section after it
3. Include all subsections: Location, Setup, Format, Differences, Naming, Commands, Best Practices

## ALGORITHM: Core Logic

### Documentation Update Process
```
1. Open README.md
2. Find "Quick Start" section
   → Add claude-code example
3. Find "Supported Clients" section
   → Add Claude Code entry
4. Save README.md

5. Open USER_GUIDE.md
6. Find Claude Desktop section
7. Insert new "Claude Code Configuration" section after it
8. Add all subsections with examples
9. Save USER_GUIDE.md

10. Manual review - verify formatting and links
```

## DATA: Content Specifications

### Quick Start Addition
```bash
# Setup for Claude Code (project-level)
mcp-config setup mcp-code-checker "My Project" --client claude-code --project-dir .
```

### Supported Clients Entry
```
- **Claude Code** - .mcp.json (project-level)
```

### USER_GUIDE.md Section
- **Title**: "Claude Code Configuration"
- **Subsections**:
  1. Configuration File Location
  2. Setup Example
  3. Configuration Format
  4. Key Differences from Claude Desktop
  5. Server Name Requirements
  6. Common Commands
  7. Best Practices

## Implementation Order

1. **Open** `README.md`
2. **Locate** Quick Start section
3. **Add** Claude Code setup example
4. **Locate** Supported Clients section
5. **Add** Claude Code entry
6. **Save** README.md
7. **Open** `USER_GUIDE.md`
8. **Locate** insertion point (after Claude Desktop section)
9. **Add** complete Claude Code Configuration section
10. **Save** USER_GUIDE.md
11. **Review** both files for formatting and accuracy
12. **Test** any code examples if possible

## Acceptance Criteria
- [ ] README.md includes Claude Code in Quick Start
- [ ] README.md includes Claude Code in Supported Clients
- [ ] USER_GUIDE.md has complete Claude Code Configuration section
- [ ] All code examples are correct and tested
- [ ] Formatting is consistent with existing documentation
- [ ] Links work (if any)
- [ ] Markdown renders correctly
- [ ] Examples follow actual command patterns
- [ ] Best practices are clear and actionable

## Manual Testing / Review
```bash
# Render README.md and verify:
# - Claude Code appears in Quick Start
# - Claude Code appears in Supported Clients
# - Formatting is clean

# Render USER_GUIDE.md and verify:
# - New section appears in correct location
# - All subsections are present
# - Code blocks render correctly
# - Examples match actual CLI behavior
```

## Notes
- **Keep it simple**: Focus on essential information
- **Follow patterns**: Match existing documentation style
- **Be accurate**: Test examples if possible
- **User-focused**: Write for users, not developers
- **No implementation details**: Save those for CONTRIBUTING.md
- **Formatting**: Use consistent markdown (backticks, headers, lists)

## Example Section Format (Reference)
```markdown
## Claude Code Configuration

[Introductory paragraph explaining what Claude Code is]

### Configuration File Location
[Bullet points about location and scope]

### Setup Example
```bash
[Actual working commands]
```

### Configuration Format
```json
[Example JSON configuration]
```

### Key Differences from Claude Desktop
[Bullet points highlighting differences]

[Continue with other subsections...]
```

## Next Step
After completing this step, **all implementation is complete**. Proceed to:
1. Run all tests to verify everything works
2. Manual testing of CLI commands
3. Code review and cleanup
4. Create pull request

## Final Checklist
- [ ] Step 1: Server name normalization (tested)
- [ ] Step 2: ClaudeCodeHandler core (tested)
- [ ] Step 3: CLI integration (tested)
- [ ] Step 4: Help system updates (manual verification)
- [ ] Step 5: Documentation updates (manual verification)
- [ ] All tests passing
- [ ] Manual CLI testing complete
- [ ] Code formatted and linted
- [ ] Ready for PR
