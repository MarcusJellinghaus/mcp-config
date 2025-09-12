# Step 4: Add Reference Project Parameter Definition (TDD)

## Objective
Add the `reference-project` parameter to the `MCP_FILESYSTEM_SERVER` configuration to enable users to specify multiple reference projects using Test-Driven Development.

## Step 4a: Write Tests First

### WHERE
- **File**: `tests/test_config/test_servers.py` (add to existing file)
- **Section**: Add new test functions to existing server tests

### TESTS TO WRITE (SIMPLIFIED KISS APPROACH)
```python
def test_filesystem_server_has_reference_project():
    """Test filesystem server includes reference-project parameter with correct attributes."""
    from mcp_config.servers import registry
    from mcp_config.cli_utils import build_setup_parser
    
    server_config = registry.get("mcp-server-filesystem")
    assert server_config is not None
    
    # Check parameter exists with correct attributes
    ref_param = server_config.get_parameter_by_name("reference-project")
    assert ref_param is not None
    assert ref_param.name == "reference-project"
    assert ref_param.arg_name == "--reference-project"
    assert ref_param.param_type == "string"
    assert ref_param.required is False
    assert ref_param.repeatable is True
    
    # Check parameter appears in CLI help
    parser = build_setup_parser("mcp-server-filesystem")
    help_text = parser.format_help()
    assert "--reference-project" in help_text

def test_reference_project_argument_generation():
    """Test reference projects generate correct arguments."""
    from mcp_config.servers import registry
    
    server_config = registry.get("mcp-server-filesystem")
    
    # Test multiple reference projects
    user_params_multi = {
        "project_dir": "/base/project",
        "reference_project": ["docs=/path/to/docs", "examples=/path/to/examples"]
    }
    args_multi = server_config.generate_args(user_params_multi, use_cli_command=True)
    assert args_multi.count("--reference-project") == 2
    assert "docs=/path/to/docs" in args_multi
    assert "examples=/path/to/examples" in args_multi
    
    # Test single reference project
    user_params_single = {
        "project_dir": "/base/project",
        "reference_project": ["docs=/path/to/docs"]
    }
    args_single = server_config.generate_args(user_params_single, use_cli_command=True)
    assert args_single.count("--reference-project") == 1
    assert "docs=/path/to/docs" in args_single
    
    # Test no reference projects (optional)
    user_params_none = {"project_dir": "/base/project"}
    args_none = server_config.generate_args(user_params_none, use_cli_command=True)
    assert "--reference-project" not in args_none
```

### EXPECTED RESULT
Tests should **FAIL** because the `reference-project` parameter doesn't exist in `MCP_FILESYSTEM_SERVER` yet.

## Step 4b: Implement to Make Tests Pass

### WHERE
- **File**: `src/mcp_config/servers.py`
- **Variable**: `MCP_FILESYSTEM_SERVER` configuration around line 350-400
- **Section**: `parameters` list

### WHAT
Add new ParameterDef to parameters list:
- `name`: "reference-project"
- `arg_name`: "--reference-project"
- `param_type`: "string" (treat as simple string, no special parsing)
- `required`: False
- `repeatable`: True (use new field from Step 1)
- `help`: Descriptive help text explaining format and repeatability

### HOW
- Integration: Append to existing `parameters` list in MCP_FILESYSTEM_SERVER
- Import: No new imports needed
- Position: Add after existing parameters (log-file is currently last)

### IMPLEMENTATION
```python
# Add to MCP_FILESYSTEM_SERVER.parameters list:
ParameterDef(
    name="reference-project",
    arg_name="--reference-project",
    param_type="string",
    required=False,
    repeatable=True,
    help="Reference project in format 'name=path'. "
         "Can be specified multiple times to add multiple reference projects. "
         "Example: --reference-project docs=/path/to/docs"
),
```

## VERIFICATION
Run the tests written in Step 4a - they should now **PASS**.

## TDD ALGORITHM
```
1. Write failing tests for reference-project parameter existence
2. Write tests for CLI help text inclusion
3. Write tests for argument generation with reference projects
4. Run tests - confirm they fail (Red)
5. Add ParameterDef to MCP_FILESYSTEM_SERVER.parameters
6. Run tests - confirm they pass (Green)
7. No refactoring needed for this simple addition
```

## DATA
- **Input**: Existing MCP_FILESYSTEM_SERVER configuration
- **Output**: Enhanced config with reference-project parameter
- **Structure**: ParameterDef with name="reference-project", repeatable=True

## TIME ESTIMATE
**~30 minutes** (including testing and verification)

## LLM Prompt
Using Test-Driven Development, implement Step 4 to add the reference-project parameter definition. First write tests in `tests/test_config/test_servers.py` that verify the filesystem server includes the reference-project parameter with correct attributes, appears in CLI help, generates proper arguments, and works both with and without reference projects. Then add the `ParameterDef` to `MCP_FILESYSTEM_SERVER.parameters` in `src/mcp_config/servers.py`. Verify all tests pass.
