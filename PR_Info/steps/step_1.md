# Step 1: Server Name Normalization Utility

## LLM Prompt
```
Implement server name normalization for Claude Code based on PR_Info/steps/summary.md and this step.

Claude Code requires server names matching pattern: ^[a-zA-Z0-9_-]{1,64}$

Create a utility function to normalize server names and notify users when normalization occurs.
Follow TDD: write tests first, then implement the function.
```

## Context
Claude Code has specific server naming requirements that other clients don't enforce. We need to validate and normalize server names before saving to `.mcp.json`.

## WHERE: File Structure
```
src/mcp_config/clients/
├── claude_code.py          # NEW - Will contain normalize_server_name()
└── ...

tests/test_config/
├── test_claude_code_handler.py   # NEW - Tests for normalization
└── ...
```

## WHAT: Functions to Implement

### 1. Main Function
```python
# File: src/mcp_config/clients/claude_code.py

def normalize_server_name(name: str) -> tuple[str, bool]:
    """
    Normalize server name to meet Claude Code requirements.
    
    Args:
        name: Original server name
        
    Returns:
        Tuple of (normalized_name, was_modified)
        
    Examples:
        normalize_server_name("my-server") -> ("my-server", False)
        normalize_server_name("my server!") -> ("my_server", True)
        normalize_server_name("a" * 100) -> ("a" * 64, True)
    """
```

### 2. Test Functions
```python
# File: tests/test_config/test_claude_code_handler.py

def test_normalize_server_name_valid():
    """Test that valid names pass through unchanged."""

def test_normalize_server_name_spaces():
    """Test that spaces are converted to underscores."""

def test_normalize_server_name_invalid_chars():
    """Test that invalid characters are removed."""

def test_normalize_server_name_length():
    """Test that names longer than 64 chars are truncated."""

def test_normalize_server_name_combined():
    """Test combination of transformations."""

def test_normalize_server_name_empty_result():
    """Test that names with only invalid characters raise ValueError."""
```

## HOW: Integration Points

### Imports
```python
# File: src/mcp_config/clients/claude_code.py
import re
from typing import Tuple
```

### Usage in ClaudeCodeHandler (Step 2)
```python
class ClaudeCodeHandler(ClientHandler):
    def setup_server(self, server_name: str, server_config: dict) -> bool:
        # Normalize server name
        normalized_name, was_modified = normalize_server_name(server_name)
        
        if was_modified:
            print(f"ℹ️  Server name normalized: '{server_name}' → '{normalized_name}'")
        
        # Use normalized_name for the rest of setup
        ...
```

## ALGORITHM: Core Logic

### normalize_server_name() Pseudocode
```
1. Replace all spaces with underscores
2. Remove all characters not in [a-zA-Z0-9_-]
3. Truncate to 64 characters maximum
4. Check if result differs from input
5. Return (normalized_name, was_modified)
```

### Implementation Approach
```python
def normalize_server_name(name: str) -> tuple[str, bool]:
    original = name
    
    # Step 1: Replace spaces with underscores
    normalized = name.replace(' ', '_')
    
    # Step 2: Remove invalid characters
    normalized = re.sub(r'[^a-zA-Z0-9_-]', '', normalized)
    
    # Step 3: Truncate to 64 chars
    normalized = normalized[:64]
    
    # Step 4: Check for empty string after normalization (DECISION #6)
    if not normalized:
        raise ValueError(
            f"Server name '{original}' contains no valid characters after normalization. "
            "Server names must contain at least one letter, number, underscore, or hyphen."
        )
    
    # Step 5: Check if modified
    was_modified = (normalized != original)
    
    # Step 6: Return tuple
    return normalized, was_modified
```

## DATA: Input/Output Specifications

### Input
- `name` (str): Original server name provided by user

### Output
- `tuple[str, bool]`: 
  - `str`: Normalized server name (safe for Claude Code)
  - `bool`: True if name was modified, False if unchanged

### Test Cases
| Input | Expected Output | Was Modified | Notes |
|-------|----------------|--------------|-------|
| `"my-server"` | `"my-server"` | `False` |
| `"my server"` | `"my_server"` | `True` |
| `"my server!"` | `"my_server"` | `True` |
| `"my@server#123"` | `"myserver123"` | `True` |
| `"a" * 100` | `"a" * 64` | `True` |
| `"valid_name-123"` | `"valid_name-123"` | `False` |
| `"  spaces  "` | `"__spaces__"` | `True` |
| `"MixedCase"` | `"MixedCase"` | `False` | |
| `"!!!"` | `ValueError` | N/A | Edge case: empty after normalization |

## Implementation Order

1. **Create test file**: `tests/test_config/test_claude_code_handler.py`
2. **Write tests** for `normalize_server_name()` covering all cases
3. **Run tests** - they should fail (RED)
4. **Create source file**: `src/mcp_config/clients/claude_code.py`
5. **Implement** `normalize_server_name()` function
6. **Run tests** - they should pass (GREEN)
7. **Verify** edge cases and refine if needed

## Acceptance Criteria
- [ ] All test cases pass
- [ ] Function handles empty strings gracefully
- [ ] Function handles already-valid names efficiently
- [ ] Function returns correct tuple format
- [ ] Code follows project style (type hints, docstrings)
- [ ] No external dependencies beyond standard library

## Notes
- Keep function pure (no side effects, except raising ValueError)
- Print statement happens in `setup_server()`, not in utility function
- Function is used before saving to config file
- **Edge case handled**: Empty string after normalization raises `ValueError` (see Decision #6 in decisions.md)

## Next Step
After completing this step, proceed to **Step 2: ClaudeCodeHandler Core Implementation**
