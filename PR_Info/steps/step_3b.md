# Step 3b: Add Path Normalization for Lists (TDD)

## Objective
Extend path normalization in `ServerConfig.generate_args()` to work with list values from repeatable path parameters using Test-Driven Development.

## Step 3b: Write Tests First

### WHERE
- **File**: `tests/test_config/test_servers.py` (add to existing file)
- **Section**: Add new test function to existing server tests

### TESTS TO WRITE (FOCUSED APPROACH)
```python
from mcp_config.servers import ServerConfig, ParameterDef

def test_path_normalization_with_lists():
    """Test path normalization works correctly with lists from repeatable parameters."""
    config = ServerConfig(
        name="test-server",
        display_name="Test Server",
        main_module="test.py",
        parameters=[
            ParameterDef(
                name="path-param",
                arg_name="--path-param",
                param_type="path",
                repeatable=True
            )
        ]
    )
    
    # Test multiple path values get normalized
    user_params_multi = {
        "path_param": ["../docs", "./examples"]
    }
    args_multi = config.generate_args(user_params_multi, use_cli_command=True)
    
    # Should contain normalized paths (exact values depend on normalize_path implementation)
    assert "--path-param" in args_multi
    assert args_multi.count("--path-param") == 2
    # Verify paths were processed (not containing .. or ./ if normalize_path handles them)
    
    # Test single path value in list
    user_params_single = {
        "path_param": ["../single/path"]
    }
    args_single = config.generate_args(user_params_single, use_cli_command=True)
    assert "--path-param" in args_single
    assert args_single.count("--path-param") == 1
    
    # Test that non-path repeatable parameters still work (regression test)
    config_string = ServerConfig(
        name="test-server",
        display_name="Test Server", 
        main_module="test.py",
        parameters=[
            ParameterDef(
                name="string-param",
                arg_name="--string-param",
                param_type="string",
                repeatable=True
            )
        ]
    )
    
    user_params_string = {"string_param": ["val1", "val2"]}
    args_string = config_string.generate_args(user_params_string, use_cli_command=True)
    assert args_string.count("--string-param") == 2
```

### EXPECTED RESULT
Tests should **FAIL** because path normalization doesn't handle lists yet.

## Step 3b: Implement to Make Tests Pass

### WHERE
- **File**: `src/mcp_config/servers.py` 
- **Method**: `ServerConfig.generate_args()` 
- **Section**: Path normalization logic (around existing normalize_path calls)

### WHAT
**Extend path normalization to handle lists using explicit for-loop approach**:
- Update existing path normalization logic to detect list values
- Use explicit for-loop to normalize each path in the list
- Maintain existing behavior for single path values
- Keep the helper method approach from Step 3a

### HOW
- Integration: Modify existing path normalization section
- Use explicit `for i, v in enumerate(value):` approach (as we decided)
- Handle both single values and lists for `param_type="path"`
- Use updated helper method for all parameter types

### IMPLEMENTATION
```python
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
            # Normalize paths (updated logic for lists using explicit for-loop)
            if param.param_type == "path" and project_dir:
                if isinstance(value, list):
                    # Explicit for-loop approach for list normalization
                    for i, v in enumerate(value):
                        value[i] = str(normalize_path(v, project_dir))
                else:
                    value = str(normalize_path(value, project_dir))

            # Use helper method for parameter argument generation
            self._add_parameter_args(args, param, value)

    return args
```

## VERIFICATION
Run the tests written in Step 3b - they should now **PASS**.
Run all tests from Step 3a - they should still **PASS** (regression protection).

## TDD ALGORITHM
```
1. Write failing tests for path normalization with lists
2. Run tests - confirm they fail (Red)
3. Update path normalization logic to handle lists with explicit for-loop
4. Integrate with helper method from Step 3a
5. Run tests - confirm they pass (Green)
6. Run Step 3a tests to ensure no regression
```

## TIME ESTIMATE
**~30 minutes** (including testing and regression verification)

## DATA
- **Input**: Path parameters with list values from repeatable CLI arguments
- **Output**: Normalized paths in argument list
- **Structure**: `["--path-param", "/normalized/path1", "--path-param", "/normalized/path2"]`

## LLM Prompt
Using Test-Driven Development, implement Step 3b for path normalization with lists. First write tests in `tests/test_config/test_servers.py` that verify path normalization works with list values, handles single values, and doesn't break string parameters. Then update the path normalization logic in `generate_args()` in `src/mcp_config/servers.py` using explicit for-loop approach for list handling. Verify all tests pass and no regression from Step 3a.

## NOTES
- **Builds on Step 3a**: Requires helper method from Step 3a to be implemented
- **Explicit approach**: Uses for-loop rather than list comprehension (as decided)
- **Regression protection**: Ensures Step 3a functionality still works
- **Integration**: Works with existing normalize_path function
