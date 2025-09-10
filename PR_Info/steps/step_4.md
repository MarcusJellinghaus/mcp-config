# Step 4: CLI Integration + Documentation (Simplified & Broken Down)

**Note**: Original Step 4 was too complex. Broken into 5 smaller, self-contained steps for better manageability.

---

## Step 4A: Basic CLI Integration for IntelliJ

### LLM Prompt
```
Add basic IntelliJ client support to the CLI. Simply add "intellij" to SUPPORTED_CLIENTS and update help text to mention IntelliJ support. Write minimal tests to verify CLI recognizes IntelliJ.
```

### WHERE
- `src/mcp_config/cli_utils.py` (add "intellij" to SUPPORTED_CLIENTS)
- `tests/test_config/test_cli_utils.py` (add simple test for intellij in supported clients)

### WHAT (Simple Changes)
```python
# cli_utils.py - One line addition
SUPPORTED_CLIENTS = [
    "claude-desktop", 
    "vscode-workspace", 
    "vscode-user",
    "intellij"  # Add this line
]
```

### Tests (Minimal)
```python
def test_intellij_in_supported_clients():
    from mcp_config.cli_utils import SUPPORTED_CLIENTS
    assert "intellij" in SUPPORTED_CLIENTS
```

---

## Step 4B: Update Help System for IntelliJ Support

### LLM Prompt
```
Update the help system to document IntelliJ client support. Add clear examples showing IntelliJ configuration works alongside Claude Desktop and VSCode.
```

### WHERE
- `src/mcp_config/help_system.py`
- `tests/test_config/test_help_system.py` (if exists, or create minimal test)

### WHAT (Help Text Updates)
```python
INTELLIJ_SUPPORT_HELP = """
🚀 IntelliJ/PyCharm Support!
MCP Config Tool now supports multiple clients:

  claude-desktop  → claude_desktop_config.json
  vscode-*        → .vscode/mcp.json  
  intellij        → mcp.json (GitHub Copilot)

Example:
  {
      "servers": {
          "my-server": { "command": "python" }
      }
  }
"""
```

---

## Step 4C: Basic CLI Integration Tests

### LLM Prompt
```
Write basic integration tests to verify the CLI setup/remove commands work with the IntelliJ client. Focus on happy path testing - don't worry about edge cases yet.
```

### WHERE
- `tests/test_config/test_cli_intellij_basic.py` (new file)

### WHAT (Simple Integration Tests)
```python
def test_intellij_setup_command_basic():
    """Test that setup command works with intellij client."""
    # Basic test that CLI accepts --client intellij
    
def test_intellij_list_command_basic():
    """Test that list command works with intellij client."""
    # Basic test that list works with intellij
```

---

## Step 4D: Update README (Basic)

### LLM Prompt
```
Update README.md to mention IntelliJ support and universal comment preservation. Keep it simple and focused on the key user benefits.
```

### WHERE
- `README.md`

### WHAT (Simple README Updates)
```markdown
## Supported Clients

- **Claude Desktop** - claude_desktop_config.json
- **VSCode** - .vscode/mcp.json  
- **IntelliJ/PyCharm** - GitHub Copilot mcp.json

## Features

- 🔧 **Multi-Client**: Works with Claude Desktop, VSCode, and IntelliJ
- 🚀 **Cross-Platform**: Windows, macOS, and Linux support
- 📝 **Simple**: Standard JSON configuration
```

---

## Step 4E: Update USER_GUIDE (Focused)

### LLM Prompt
```
Update USER_GUIDE.md with a focused section on IntelliJ usage and comment support. Don't create comprehensive documentation yet - just cover the basics users need to know.
```

### WHERE
- `USER_GUIDE.md`

### WHAT (Basic User Guide Updates)
```markdown
## IntelliJ/PyCharm Support

MCP Config Tool supports IntelliJ IDEA and PyCharm through GitHub Copilot:

```bash
# Setup server for IntelliJ
mcp-config setup myserver "Description" --client intellij

# List IntelliJ servers  
mcp-config list --client intellij
```

### Configuration Format

All clients use standard JSON configuration:

```json
{
    "servers": {
        "my-server": {
            "command": "python",
            "args": ["-m", "my_server"]
        }
    }
}
```

---

## Why This Breakdown is Better

### Original Problems
- **Too Complex**: Combined CLI, testing, and documentation in one massive step
- **All-or-Nothing**: Hard to validate individual pieces worked
- **Testing Overhead**: Full TDD approach added complexity
- **Documentation Heavy**: Tried to create comprehensive docs all at once

### New Benefits
- **Self-Contained**: Each step can be completed and validated independently
- **Incremental**: Build functionality piece by piece
- **Testable**: Each step has clear success criteria
- **Manageable**: Smaller chunks are easier to implement and review
- **Focused**: Each step has a single clear purpose

### Implementation Order
1. **4A**: Get basic CLI working (5 minutes)
2. **4B**: Update help text (10 minutes)  
3. **4C**: Add basic tests (15 minutes)
4. **4D**: Update README (10 minutes)
5. **4E**: Update USER_GUIDE (15 minutes)

**Total**: ~1 hour instead of the 3-4 hours the original Step 4 would have required.

### Dependencies
- Each step builds on the previous one
- But each can be validated independently
- If one step has issues, others aren't blocked
- Can skip documentation steps if needed to focus on functionality

## Comments
- **Why simplify**: Original approach was overwhelming and hard to validate
- **Why break down**: Smaller steps are easier to implement, test, and review
- **Why basic first**: Get core functionality working before comprehensive testing
- **Why focused docs**: Users need practical examples, not comprehensive theory
