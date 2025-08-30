# Step 2: Update Documentation and References

## Overview
Update all documentation files (README.md, INSTALL.md) to correctly reflect the mcp-config project instead of mcp-code-checker references.

## Files to Update

### 1. README.md
**Current Issues:**
- Title says "MCP Code Checker" instead of "MCP Config"
- Description focuses on code checking instead of MCP server configuration
- Installation instructions refer to wrong repository
- Examples use wrong command names
- GitHub URLs point to mcp-code-checker

**Required Changes:**
- Change title to "# MCP Config"
- Update description to focus on MCP server configuration functionality
- Update repository URLs from `mcp-code-checker` to `mcp-config`
- Update command examples from `mcp-code-checker` to `mcp-config`
- Remove code checking specific content
- Focus on MCP server configuration capabilities
- Update installation commands
- Update GitHub repository references

**New README.md Structure:**
```markdown
# MCP Config

A CLI tool to configure MCP servers for various clients like Claude Desktop and VSCode.

## Overview

This CLI tool enables easy configuration and management of Model Context Protocol (MCP) servers across different AI clients. With mcp-config, you can:

- Configure MCP servers for Claude Desktop
- Set up MCP servers for VSCode 
- Validate server configurations
- Auto-detect Python environments and dependencies
- Manage server lifecycles (setup, list, remove, validate)

## Features

- **Multi-client support**: Configure for Claude Desktop, VSCode workspace, and VSCode user profiles
- **Auto-detection**: Automatically detect Python executables and virtual environments
- **Validation**: Comprehensive validation of server configurations and requirements  
- **Dry-run mode**: Preview changes before applying them
- **Backup management**: Automatic backup creation before configuration changes

## Installation

See [INSTALL.md](INSTALL.md) for detailed installation instructions.

**Quick install:**

```bash
# Install from GitHub (recommended)
pip install git+https://github.com/MarcusJellinghaus/mcp-config.git

# Verify installation
mcp-config --help
```

[Continue with updated content focusing on configuration management]
```

### 2. INSTALL.md
**Current Issues:**
- All references to "MCP Code Checker" instead of "MCP Config"
- Installation commands use wrong package names
- Repository URLs are incorrect
- Command verification uses wrong command names

**Required Changes:**
- Replace all instances of "mcp-code-checker" with "mcp-config"
- Update repository URLs
- Update command names in examples
- Update package references
- Fix GitHub repository URLs

**Key Sections to Update:**
- Prerequisites (no changes needed)
- Installation commands: `pip install mcp-config`
- Repository URLs: `git+https://github.com/MarcusJellinghaus/mcp-config.git`
- Command verification: `mcp-config --help`
- Virtual environment examples
- Troubleshooting section commands

### 3. Project Configuration Verification
**Verify pyproject.toml is correct:**
- ✅ Name: "mcp-config" (correct)
- ✅ Description mentions MCP server configuration (correct)
- ✅ Repository URLs point to mcp-config (correct)
- ✅ Script entry point: `mcp-config = "src.mcp_config.main:main"` (correct)

## String Replacements Needed

### README.md Replacements:
- "MCP Code Checker" → "MCP Config"
- "mcp-code-checker" → "mcp-config"
- "code checking" → "MCP server configuration"
- References to pylint/pytest functionality → Remove or minimize
- Focus on configuration management features

### INSTALL.md Replacements:
- "MCP Code Checker" → "MCP Config"  
- "mcp-code-checker" → "mcp-config"
- "MarcusJellinghaus/mcp-code-checker" → "MarcusJellinghaus/mcp-config"
- Command examples: update all instances

## Validation Steps
1. Search for any remaining "code-checker" references
2. Verify all GitHub URLs point to mcp-config repository
3. Verify all command examples use `mcp-config`
4. Test installation instructions accuracy
5. Ensure focus is on configuration management, not code analysis

## Expected Result
- README.md accurately describes MCP server configuration tool
- INSTALL.md provides correct installation steps for mcp-config
- All repository references point to correct GitHub repository
- Documentation focuses on configuration management capabilities
- No remaining references to code checking functionality

## Next Step
After completing this step, proceed to Step 3: Fix Source Code References.
