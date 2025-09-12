# Step 2: Update CLI Parser for Repeatable Parameters (TDD)

## Objective
Modify the CLI argument parser to use `action="append"` for parameters marked as repeatable, allowing multiple values to be collected into a list using Test-Driven Development.

## Step 2a: Write Tests First

### WHERE
- **File**: `tests/test_config/test_cli_utils.py` (add to existing file)
- **Section**: Add new test functions to existing CLI utils tests

### TESTS TO WRITE
```python
import pytest
import argparse
from mcp_config.servers import ParameterDef
from mcp_config.cli_utils import add_parameter_to_parser

@pytest.mark.parametrize("repeatable,expected_action", [
    (True, "append"),
    (False, None),  # No action key when not repeatable
])
def test_add_parameter_to_parser_repeatable(repeatable, expected_action):
    """Test CLI parser handles repeatable parameters correctly."""
    parser = argparse.ArgumentParser()
    param = ParameterDef(
        name="test-param",
        arg_name="--test-param",
        param_type="string",
        repeatable=repeatable
    )
    
    add_parameter_to_parser(parser, param)
    
    # Check the action was set correctly
    for action in parser._actions:
        if hasattr(action, 'dest') and action.dest == 'test_param':
            if expected_action:
                assert action.__class__.__name__ == '_AppendAction'
            else:
                assert action.__class__.__name__ != '_AppendAction'

def test_cli_parsing_multiple_values():
    """Test actual CLI parsing with repeated parameters."""
    parser = argparse.ArgumentParser()
    param = ParameterDef(
        name="reference-project",
        arg_name="--reference-project",
        param_type="string",
        repeatable=True
    )
    add_parameter_to_parser(parser, param)
    
    # Test parsing multiple values
    args = parser.parse_args([
        "--reference-project", "docs=/path/to/docs",
        "--reference-project", "examples=/path/to/examples"
    ])
    
    assert args.reference_project == ["docs=/path/to/docs", "examples=/path/to/examples"]

def test_cli_parsing_single_repeatable_value():
    """Test parsing single value for repeatable parameter."""
    parser = argparse.ArgumentParser()
    param = ParameterDef(
        name="reference-project", 
        arg_name="--reference-project",
        param_type="string",
        repeatable=True
    )
    add_parameter_to_parser(parser, param)
    
    args = parser.parse_args(["--reference-project", "docs=/path/to/docs"])
    assert args.reference_project == ["docs=/path/to/docs"]

def test_non_repeatable_parameter_unchanged():
    """Test non-repeatable parameters work as before."""
    parser = argparse.ArgumentParser()
    param = ParameterDef(
        name="project-dir",
        arg_name="--project-dir",
        param_type="string",
        repeatable=False  # Explicit for clarity
    )
    add_parameter_to_parser(parser, param)
    
    args = parser.parse_args(["--project-dir", "/path/to/project"])
    assert args.project_dir == "/path/to/project"  # Single string, not list
```

### EXPECTED RESULT
Tests should **FAIL** because the repeatable logic doesn't exist in `add_parameter_to_parser()` yet.

## Step 2b: Implement to Make Tests Pass

### WHERE
- **File**: `src/mcp_config/cli_utils.py`
- **Function**: `add_parameter_to_parser(parser, param)` around line 85-120
- **Integration**: argparse argument addition logic

### WHAT
**Simplified implementation** (no hasattr() checks needed):
- Detect when `param.repeatable` is True
- Set `action="append"` for repeatable parameters
- Keep all other logic unchanged

### HOW
- Import: No new imports needed (argparse already imported)
- Integration: Modify kwargs dict before `parser.add_argument()`
- Simple conditional logic based on `param.repeatable` attribute

### IMPLEMENTATION
```python
def add_parameter_to_parser(
    parser: argparse.ArgumentParser | argparse._ArgumentGroup,
    param: Any,
) -> None:
    """Add a single parameter to an argument parser.

    Args:
        parser: ArgumentParser or ArgumentGroup to add parameter to
        param: ParameterDef object defining the parameter
    """
    option_name = f"--{param.name}"

    # Build kwargs for add_argument
    kwargs: dict[str, Any] = {
        "help": param.help,
        "dest": param.name.replace("-", "_"),  # Convert to valid Python identifier
    }

    # Handle repeatable parameters (SIMPLIFIED - no hasattr needed)
    if param.repeatable:
        kwargs["action"] = "append"

    # Handle required parameters
    if param.required:
        kwargs["required"] = True

    # ... rest of existing logic unchanged ...
```

## VERIFICATION
Run the tests written in Step 2a - they should now **PASS**.

## TDD ALGORITHM
```
1. Write failing tests for CLI parser repeatable functionality
2. Run tests - confirm they fail (Red)
3. Add repeatable parameter logic to add_parameter_to_parser()
4. Keep implementation simple (no hasattr checks)
5. Run tests - confirm they pass (Green)
6. Refactor if needed (likely not needed for this simple change)
```

## DATA
- **Input**: `param` with potential `repeatable=True`
- **Output**: argparse argument configured for multiple values
- **Structure**: kwargs dict with `"action": "append"` when repeatable

## LLM Prompt
Using Test-Driven Development, implement Step 2 to update the CLI parser. First write tests in `tests/test_config/test_cli_utils.py` that verify repeatable parameters use action="append", accept multiple values, and don't break existing functionality. Then modify `add_parameter_to_parser()` in `src/mcp_config/cli_utils.py` to handle repeatable parameters with simplified logic (no hasattr checks needed). Verify all tests pass.
