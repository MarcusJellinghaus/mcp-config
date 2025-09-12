# Step 3: Update Argument Generation for Lists (TDD)

## Objective
Modify the `ServerConfig.generate_args()` method to handle parameters that produce list values from repeatable CLI arguments using Test-Driven Development.

## Step 3a: Write Tests First

### WHERE
- **File**: `tests/test_config/test_servers.py` (add to existing file)
- **Section**: Add new test functions to existing server tests

### TESTS TO WRITE (SIMPLIFIED KISS APPROACH)
```python
from mcp_config.servers import ServerConfig, ParameterDef

def test_list_argument_generation():
    """Test list values generate multiple argument pairs."""
    config = ServerConfig(
        name="test-server",
        display_name="Test Server", 
        main_module="test.py",
        parameters=[
            ParameterDef(
                name="test-param",
                arg_name="--test-param",
                param_type="string",
                repeatable=True
            )
        ]
    )
    
    # Test multiple values
    user_params_multi = {"test_param": ["val1", "val2"]}
    args_multi = config.generate_args(user_params_multi, use_cli_command=True)
    assert "--test-param" in args_multi
    assert "val1" in args_multi
    assert "val2" in args_multi
    assert args_multi.count("--test-param") == 2
    
    # Test single value in list
    user_params_single = {"test_param": ["val1"]}
    args_single = config.generate_args(user_params_single, use_cli_command=True)
    assert "--test-param" in args_single
    assert "val1" in args_single
    assert args_single.count("--test-param") == 1
    
    # Test empty list (should be skipped)
    user_params_empty = {"test_param": []}
    args_empty = config.generate_args(user_params_empty, use_cli_command=True)
    assert "--test-param" not in args_empty

def test_non_list_arguments_unchanged():
    """Test single values work as before."""
    config = ServerConfig(
        name="test-server",
        display_name="Test Server",
        main_module="test.py", 
        parameters=[
            ParameterDef(name="regular-param", arg_name="--regular-param", param_type="string"),
        ]
    )
    
    user_params = {"regular_param": "single_value"}
    args = config.generate_args(user_params, use_cli_command=True)
    
    assert "--regular-param" in args
    assert "single_value" in args
    assert args.count("--regular-param") == 1
```

### EXPECTED RESULT
Tests should **FAIL** because the list handling logic doesn't exist in `generate_args()` yet.

## Step 3b: Implement to Make Tests Pass

### WHERE
- **File**: `src/mcp_config/servers.py` 
- **Method**: `ServerConfig.generate_args()` around line 150-200
- **Section**: Parameter processing loop

### WHAT
**Enhanced implementation with extracted helper method (CLEAN CODE APPROACH)**:
- Add helper method `_add_parameter_args()` for clean, testable code
- Detect when parameter value is a list (from `action="append"`)
- Generate multiple `--param value` pairs for each list item
- Maintain existing behavior for single values
- Handle empty lists (skip completely)

**Design Decision**: Use helper method for cleaner, more maintainable code rather than inline logic

### HOW
- Integration: Modify existing parameter processing loop
- Extract logic into helper method for better testing
- Handle isinstance(value, list) check in helper
- Use helper method from main generate_args()

### IMPLEMENTATION
```python
def _add_parameter_args(self, args: list[str], param: ParameterDef, value: Any) -> None:
    """Helper method to add parameter arguments to args list.
    
    Args:
        args: List to append arguments to
        param: Parameter definition
        value: Parameter value (single value or list for repeatable params)
    """
    if param.repeatable and isinstance(value, list):
        # Handle list values for repeatable parameters
        for item in value:
            args.extend([param.arg_name, str(item)])
    else:
        # Handle single values (both repeatable and non-repeatable)
        args.extend([param.arg_name, str(value)])

def generate_args(self, user_params: dict[str, Any], use_cli_command: bool = False) -> list[str]:
    """Generate command line args from user parameters."""
    # ... existing setup code unchanged ...
    
    # Generate arguments - modified section
    for param in self.parameters:
        param_key = param.name.replace("-", "_")
        value = processed_params.get(param_key, param.default)

        # Skip if no value provided or empty list
        if value is None or (isinstance(value, list) and len(value) == 0):
            continue

        # ... existing client-specific filtering logic unchanged ...

        # Handle boolean flags
        if param.is_flag:
            if value:  # Only add flag if True
                args.append(param.arg_name)
        else:
            # Normalize paths (existing logic updated for lists)
            if param.param_type == "path" and project_dir:
                if isinstance(value, list):
                    value = [str(normalize_path(v, project_dir)) for v in value]
                else:
                    value = str(normalize_path(value, project_dir))

            # Use helper method for parameter argument generation
            self._add_parameter_args(args, param, value)

    return args
```

## VERIFICATION
Run the tests written in Step 3a - they should now **PASS**.

## TDD ALGORITHM
```
1. Write failing tests for argument generation with lists
2. Run tests - confirm they fail (Red)
3. Add helper method _add_parameter_args() for clean code
4. Modify generate_args() to use helper and handle lists
5. Run tests - confirm they pass (Green)
6. Refactor if needed (helper method already provides good separation)
```

## DATA
- **Input**: `user_params` dict potentially containing lists for repeatable params
- **Output**: `args` list with repeated `--param value` entries
- **Structure**: `["--reference-project", "docs=/path", "--reference-project", "examples=/path"]`

## LLM Prompt
Using Test-Driven Development, implement Step 3 to update argument generation. First write tests in `tests/test_config/test_servers.py` that verify list values generate multiple argument pairs, single values work unchanged, empty lists are skipped, and path normalization works with lists. Then add helper method `_add_parameter_args()` and modify `generate_args()` in `src/mcp_config/servers.py` to handle repeatable parameters. Verify all tests pass.
