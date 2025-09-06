# Step 1: Universal JSON Comments Utility (KISS + TDD)

## LLM Prompt
```
Following TDD approach, implement universal JSON utilities with comment preservation using json-five library. Write comprehensive tests FIRST, then implement. This will be used by ALL MCP clients (Claude Desktop, VSCode, IntelliJ) for consistent comment handling. Keep it simple - same API for all clients.
```

## WHERE
- **Files**: 
  - `tests/test_config/test_json_utils.py` (new - **WRITE FIRST**)
  - `src/mcp_config/json_utils.py` (new - implement after tests)
  - `pyproject.toml` (update dependencies)

## TDD APPROACH (Tests First!)
### 1. Write Tests First (Red)
```python
# tests/test_config/test_json_utils.py - WRITE THESE FIRST
def test_load_preserves_block_comments()
def test_load_preserves_line_comments()
def test_round_trip_comment_integrity()
def test_universal_config_formats()
def test_error_handling_malformed_json()
def test_new_file_creation()
def test_atomic_write_safety()
```

### 2. Run Tests (Should Fail)
```bash
pytest tests/test_config/test_json_utils.py  # Should fail - no implementation yet
```

### 3. Implement Minimum (Green)
```python
# src/mcp_config/json_utils.py - Implement to make tests pass
def load_json_with_comments(file_path: Path) -> tuple[dict[str, Any], Any]:
    # Minimal implementation to pass tests
    
def save_json_with_comments(file_path: Path, data: dict[str, Any], model: Any = None) -> None:
    # Minimal implementation to pass tests
```

### 4. Refactor (Clean)
- Optimize implementation while keeping tests green

## WHAT (TDD-Driven API)
```python
def load_json_with_comments(file_path: Path) -> tuple[dict[str, Any], Any]
def save_json_with_comments(file_path: Path, data: dict[str, Any], model: Any = None) -> None
```

## HOW (Test-Driven Implementation)
### Dependencies (Required)
```toml
# pyproject.toml
[project]
dependencies = ["json-five>=1.0.0", ...]
```

### Test-Driven Implementation
```python
from pathlib import Path
from typing import Any, tuple
from json5.loader import loads, ModelLoader  # Verified API
from json5.dumper import dumps, ModelDumper  # Verified API

# Implementation driven by test requirements
def load_json_with_comments(file_path: Path) -> tuple[dict[str, Any], Any]:
    """Universal JSON loader with comment preservation."""
    if not file_path.exists():
        return {}, None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Load with comment model for preservation
    model = loads(content, loader=ModelLoader())
    # Load as regular data for manipulation
    data = loads(content)
    
    return data, model

def save_json_with_comments(file_path: Path, data: dict[str, Any], model: Any = None) -> None:
    """Universal JSON saver with comment preservation."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        if model is not None:
            # Preserve comments using ModelDumper
            dumps(model, f, dumper=ModelDumper(), indent=2)
        else:
            # Fallback for new files (no existing comments)
            import json5
            json5.dump(data, f, indent=2)
        f.write('\n')
```

## TDD Test Plan (Write These FIRST!)
### Critical Test Cases
1. **Comment preservation tests**:
   - Block comments `/* */` preserved
   - Line comments `//` preserved  
   - Mixed comment types preserved
   - Comments in different positions

2. **Universal format tests**:
   - Claude Desktop format (`mcpServers`)
   - VSCode format (`servers`)
   - IntelliJ format (`servers`)
   - Mixed configurations

3. **Round-trip integrity**:
   - Load → modify data → save → reload → verify comments unchanged
   - Multiple round-trips preserve comments
   - Partial modifications preserve unrelated comments

4. **Error handling tests**:
   - Missing files return empty dict + None model
   - Malformed JSON raises appropriate errors
   - Invalid paths handled gracefully
   - Permission errors handled

5. **Edge case tests**:
   - Empty files
   - Files with only comments
   - Very large comment blocks
   - Unicode characters in comments

6. **Cross-client scenarios**:
   - Convert between client formats preserving comments
   - Load VSCode config, modify, save as IntelliJ format
   - Validate works with all real-world config examples

## TDD Workflow
```bash
# 1. Write failing tests
pytest tests/test_config/test_json_utils.py -v  # RED

# 2. Implement minimal code to pass
# Edit src/mcp_config/json_utils.py

# 3. Run tests until green
pytest tests/test_config/test_json_utils.py -v  # GREEN

# 4. Refactor while keeping tests green
# Improve implementation, tests stay green

# 5. Add more tests for edge cases
# Repeat cycle
```

## Comments (TDD Benefits)
- **Why tests first**: Ensures API meets actual usage requirements
- **Why comprehensive tests**: Universal utility needs to work for all clients
- **Why round-trip tests**: Comment preservation is the core requirement
- **Why edge case tests**: Real-world configs have complex comment patterns
