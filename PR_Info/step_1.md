# Step 1: JSON Comments Utility Implementation

## LLM Prompt
```
Referring to the Summary: IntelliJ MCP Client Support with JSON Comments, implement Step 1: Create a JSON comments utility that preserves comments during read/write operations. Use json-five library for comment preservation with fallback to standard json. Follow TDD approach by writing tests first.
```

## WHERE
- **Files**: 
  - `src/mcp_config/json_utils.py` (new)
  - `tests/test_config/test_json_utils.py` (new)
  - `pyproject.toml` (update dependencies)

## WHAT
### Main Functions
```python
def load_json_with_comments(file_path: Path) -> dict[str, Any]
def save_json_with_comments(file_path: Path, data: dict[str, Any], original_content: str = None) -> None
def is_json_comments_available() -> bool
```

## HOW
### Integration Points
- **Dependencies**: Add `json-five` to `pyproject.toml` optional dependencies
- **Imports**: 
  ```python
  from pathlib import Path
  from typing import Any, Optional
  try:
      import json5
      from json5.loader import ModelLoader
      from json5.dumper import ModelDumper
  except ImportError:
      json5 = None
  ```

### Error Handling
- **ImportError**: Graceful fallback to standard `json` 
- **FileNotFoundError**: Return empty dict
- **JSONDecodeError**: Re-raise with helpful message

## ALGORITHM
```
1. Check if json-five is available
2. If available: Use ModelLoader for comment preservation
3. If not: Fall back to standard json module
4. For writing: Preserve original format when possible
5. Create parent directories if needed
```

## DATA
### Return Values
- `load_json_with_comments()`: `dict[str, Any]` - Parsed JSON data
- `save_json_with_comments()`: `None` - Side effect only
- `is_json_comments_available()`: `bool` - Feature availability

### Data Structures
```python
# Internal model representation (when json-five available)
JSONModel = json5.JSONText | dict[str, Any]

# Configuration data
ConfigDict = dict[str, Any]
```

## Tests to Write First
1. **Test comment preservation** with json-five available
2. **Test fallback behavior** when json-five unavailable  
3. **Test file creation** with proper formatting
4. **Test error handling** for malformed JSON
5. **Test cross-platform paths** and permissions
