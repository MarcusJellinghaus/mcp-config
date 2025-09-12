# Step 2: Update CLI Parser for Repeatable Parameters (TDD)

## Objective
Modify the CLI argument parser to use `action="append"` for parameters marked as repeatable, allowing multiple values to be collected into a list using Test-Driven Development.

## Step 2a: Write Tests First

### WHERE
- **File**: `tests/test_config/test_cli_utils.py` (add to existing file)
- **Section**: Add new test functions to existing CLI utils tests

### TESTS TO WRITE (STREAMLINED APPROACH)
```python
import argparse
from mcp_config.servers import ParameterDef
from mcp_config.cli_utils import add_parameter_to_parser

def test_repeatable_parameter_parsing():
    """Test CLI parser handles repeatable parameters with action=append."""
    parser = argparse.ArgumentParser()
    param = ParameterDef(
        name="reference-project",
        arg_name="--reference-project",
        param_type="string",
        repeatable=True
    )
    add_parameter_to_parser(parser, param)
    
    # Test parsing multiple values
    args_multiple = parser.parse_args([
        "--reference-project", "docs=/path/to/docs",
        "--reference-project", "examples=/path/to/examples"
    ])
    assert args_multiple.reference_project == ["docs=/path/to/docs", "examples=/path/to/examples"]
    
    # Test parsing single value (still becomes list with action=append)
    args_single = parser.parse_args(["--reference-project", "docs=/path/to/docs"])
    assert args_single.reference_project == ["docs=/path/to/docs"]

def test_non_repeatable_unchanged():
    """Test non-repeatable parameters still work normally."""
    parser = argparse.ArgumentParser()
    param = ParameterDef(
        name="project-dir",
        arg_name="--project-dir",
        param_type="string",
        repeatable=False
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

## TIME ESTIMATE
**~45 minutes** (including testing and debugging)

## DATA
- **Input**: `param` with potential `repeatable=True`
- **Output**: argparse argument configured for multiple values
- **Structure**: kwargs dict with `"action": "append"` when repeatable

## LLM Prompt
Using Test-Driven Development, implement Step 2 to update the CLI parser. First write tests in `tests/test_config/test_cli_utils.py` that verify repeatable parameters use action="append", accept multiple values, and don't break existing functionality. Then modify `add_parameter_to_parser()` in `src/mcp_config/cli_utils.py` to handle repeatable parameters with simplified logic (no hasattr checks needed). Verify all tests pass.
