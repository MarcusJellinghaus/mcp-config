# Step 4: Add Reference Project Parameter Definition (TDD)

## Objective
Add the `reference-project` parameter to the `MCP_FILESYSTEM_SERVER` configuration to enable users to specify multiple reference projects using Test-Driven Development.

## Step 4a: Write Tests First

### WHERE
- **File**: `tests/test_config/test_servers.py` (add to existing file)
- **Section**: Add new test functions to existing server tests

### TESTS TO WRITE
```python
def test_filesystem_server_has_reference_project_parameter():
    """Test that filesystem server includes reference-project parameter."""
    from mcp_config.servers import registry
    
    server_config = registry.get("mcp-server-filesystem")
    assert server_config is not None
    
    ref_param = server_config.get_parameter_by_name("reference-project")
    assert ref_param is not None
    assert ref_param.name == "reference-project"
    assert ref_param.arg_name == "--reference-project"
    assert ref_param.param_type == "string"
    assert ref_param.required is False
    assert ref_param.repeatable is True

def test_filesystem_server_reference_project_in_help():
    """Test reference-project parameter appears in CLI help."""
    from mcp_config.cli_utils import build_setup_parser
    
    parser = build_setup_parser("mcp-server-filesystem")
    help_text = parser.format_help()
    
    assert "--reference-project" in help_text
    assert "name=path" in help_text.lower() or "name=/path" in help_text.lower()
    assert "multiple" in help_text.lower()  # Should mention it can be repeated

def test_filesystem_server_generates_multiple_reference_projects():
    """Test filesystem server generates correct args for multiple reference projects."""
    from mcp_config.servers import registry
    
    server_config = registry.get("mcp-server-filesystem")
    
    user_params = {
        "project_dir": "/base/project",
        "reference_project": [
            "docs=/path/to/docs",
            "examples=/path/to/examples"
        ]
    }
    
    args = server_config.generate_args(user_params, use_cli_command=True)
    
    # Should contain both reference project entries
    assert "--reference-project" in args
    ref_indices = [i for i, arg in enumerate(args) if arg == "--reference-project"]
    assert len(ref_indices) == 2
    
    # Check values are correct
    assert "docs=/path/to/docs" in args
    assert "examples=/path/to/examples" in args

def test_filesystem_server_single_reference_project():
    """Test filesystem server works with single reference project."""
    from mcp_config.servers import registry
    
    server_config = registry.get("mcp-server-filesystem")
    
    user_params = {
        "project_dir": "/base/project",
        "reference_project": ["docs=/path/to/docs"]  # argparse with append always gives list
    }
    
    args = server_config.generate_args(user_params, use_cli_command=True)
    
    # Should contain single reference project entry
    assert "--reference-project" in args
    assert "docs=/path/to/docs" in args
    ref_indices = [i for i, arg in enumerate(args) if arg == "--reference-project"]
    assert len(ref_indices) == 1

def test_filesystem_server_no_reference_project_optional():
    """Test filesystem server works without reference projects (optional parameter)."""
    from mcp_config.servers import registry
    
    server_config = registry.get("mcp-server-filesystem")
    
    user_params = {
        "project_dir": "/base/project"
        # No reference_project provided
    }
    
    args = server_config.generate_args(user_params, use_cli_command=True)
    
    # Should not contain reference-project at all
    assert "--reference-project" not in args

def test_filesystem_server_parameter_position():
    """Test reference-project parameter is in the correct position in parameters list."""
    from mcp_config.servers import registry
    
    server_config = registry.get("mcp-server-filesystem")
    param_names = [p.name for p in server_config.parameters]
    
    # Should be in the parameters list
    assert "reference-project" in param_names
    
    # Should be after the core parameters but position doesn't matter too much
    assert "project-dir" in param_names  # Core parameter should still be there
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

## LLM Prompt
Using Test-Driven Development, implement Step 4 to add the reference-project parameter definition. First write tests in `tests/test_config/test_servers.py` that verify the filesystem server includes the reference-project parameter with correct attributes, appears in CLI help, generates proper arguments, and works both with and without reference projects. Then add the `ParameterDef` to `MCP_FILESYSTEM_SERVER.parameters` in `src/mcp_config/servers.py`. Verify all tests pass.
