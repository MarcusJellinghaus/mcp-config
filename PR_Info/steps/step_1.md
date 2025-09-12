# Step 1: Add Repeatable Parameter Support to ParameterDef (TDD)

## Objective
Extend the `ParameterDef` dataclass to support parameters that can be specified multiple times on the command line using Test-Driven Development.

## Step 1a: Write Tests First

### WHERE
- **File**: `tests/test_config/test_servers.py` (add to existing file)
- **Section**: Add new test functions to existing test file

### TESTS TO WRITE (SIMPLIFIED KISS APPROACH)
```python
def test_parameter_def_with_repeatable():
    """Test ParameterDef supports repeatable=True and defaults to False."""
    # Test with repeatable=True
    param_true = ParameterDef(
        name="test-param",
        arg_name="--test-param", 
        param_type="string",
        repeatable=True
    )
    assert param_true.repeatable is True
    
    # Test default (repeatable=False)
    param_default = ParameterDef(
        name="test-param",
        arg_name="--test-param",
        param_type="string"
    )
    assert param_default.repeatable is False

def test_parameter_def_existing_functionality():
    """Test existing ParameterDef creation still works."""
    # Test with existing parameters from MCP_CODE_CHECKER
    param = ParameterDef(
        name="project-dir",
        arg_name="--project-dir",
        param_type="path",
        required=True
    )
    assert param.repeatable is False  # Default value
    assert param.required is True
```

### EXPECTED RESULT
Tests should **FAIL** because the `repeatable` attribute doesn't exist yet.

## Step 1b: Implement to Make Tests Pass

### WHERE
- **File**: `src/mcp_config/servers.py`
- **Class**: `ParameterDef` dataclass
- **Lines**: Around line 15-35 (dataclass definition)

### WHAT
Add a new field to enable repeatable parameters:
- `repeatable: bool = False` - field to mark parameters as repeatable
- Update docstring to document the new field

### HOW
- Add field to existing `@dataclass` definition
- Set default value to maintain backward compatibility
- No additional imports or decorators needed

### IMPLEMENTATION
```python
@dataclass
class ParameterDef:
    """Definition of a server parameter for CLI and config generation.

    Attributes:
        name: CLI parameter name (e.g., "project-dir")
        arg_name: Server argument (e.g., "--project-dir")
        param_type: Type of parameter ("string", "boolean", "choice", "path")
        required: Whether the parameter is required
        default: Default value for the parameter
        choices: List of valid choices for "choice" type parameters
        help: Help text for CLI
        is_flag: True for boolean flags (action="store_true")
        auto_detect: True if value can be auto-detected
        validator: Optional validation function
        repeatable: Whether parameter can be specified multiple times
    """
    # ... existing fields unchanged ...
    repeatable: bool = False
```

## VERIFICATION
Run the tests written in Step 1a - they should now **PASS**.

## TDD ALGORITHM
```
1. Write failing tests for repeatable parameter functionality
2. Run tests - confirm they fail (Red)
3. Add repeatable field to ParameterDef dataclass
4. Update docstring to document new field
5. Run tests - confirm they pass (Green)
6. No refactoring needed for this simple change
```

## DATA
- **Input**: Existing ParameterDef with current fields
- **Output**: Enhanced ParameterDef with repeatable support
- **Structure**: `repeatable: bool = False` added to dataclass fields

## TIME ESTIMATE
**~30 minutes** (simple dataclass extension with tests)

## LLM Prompt
Using Test-Driven Development, implement Step 1 of adding reference-project parameter support. First write tests in `tests/test_config/test_servers.py` that verify ParameterDef can be created with repeatable=True, defaults to False, and doesn't break existing functionality. Then extend the `ParameterDef` dataclass in `src/mcp_config/servers.py` to include the `repeatable: bool = False` field and updated docstring. Verify all tests pass.
