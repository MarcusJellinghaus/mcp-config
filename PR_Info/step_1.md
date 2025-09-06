# Step 1: JSON Comments Utility Implementation

## LLM Prompt
```
Referring to the Summary: IntelliJ MCP Client Support with JSON Comments, implement Step 1: Create a JSON comments utility that preserves comments during read/write operations. Use json-five library as required dependency for comment preservation. Follow TDD approach by writing tests first.
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
def save_json_with_comments(file_path: Path, data: dict[str, Any]) -> None
```

## HOW
### Integration Points
- **Dependencies**: Add `json-five` to `pyproject.toml` required dependencies
- **Imports**: 
  ```python
  from pathlib import Path
  from typing import Any
  import json5
  from json5.loader import ModelLoader
  from json5.dumper import ModelDumper
  ```

### Error Handling
- **FileNotFoundError**: Return empty dict
- **JSONDecodeError**: Re-raise with helpful message
- **Comment Preservation Issues**: Simple warning message

## ALGORITHM
```
1. Use ModelLoader from json-five for comment preservation
2. For writing: Use ModelDumper to preserve original format
3. Create parent directories if needed
4. Use atomic writes with temp files
```

## DATA
### Return Values
- `load_json_with_comments()`: `dict[str, Any]` - Parsed JSON data
- `save_json_with_comments()`: `None` - Side effect only

### Data Structures
```python
# Internal model representation from json-five
JSONModel = json5.JSONText | dict[str, Any]

# Configuration data
ConfigDict = dict[str, Any]
```

## Tests to Write First
1. **Test comment preservation** with various JSONC formats
2. **Test round-trip integrity** for complex comment structures
3. **Test file creation** with proper formatting
4. **Test error handling** for malformed JSONC
5. **Test atomic writes** and temp file handling
