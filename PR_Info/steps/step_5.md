# Step 5: Integration Tests and Final Verification (TDD)

## Objective
Create comprehensive integration tests to verify the complete repeatable parameter functionality works end-to-end, and ensure backward compatibility.

## Step 5a: Write Integration Tests

### WHERE
- **Files**: Add to existing test files or create focused integration tests
  - `tests/test_config/test_integration.py` (if it exists) or relevant existing files
  - Focus on end-to-end scenarios

### INTEGRATION TESTS TO WRITE
```python
def test_full_setup_command_with_reference_projects():
    """Test complete setup command with multiple reference projects."""
    from mcp_config.cli_utils import parse_and_validate_args
    from mcp_config.servers import registry
    
    # Simulate CLI args for setup command with multiple reference projects
    test_args = [
        "setup", "mcp-server-filesystem", "test-fs",
        "--project-dir", "/base/project",
        "--reference-project", "docs=/path/to/docs",
        "--reference-project", "examples=/path/to/examples",
        "--dry-run"
    ]
    
    parsed_args, errors = parse_and_validate_args(test_args)
    
    # Should parse without errors
    assert len(errors) == 0
    assert parsed_args.server_type == "mcp-server-filesystem"
    assert parsed_args.reference_project == ["docs=/path/to/docs", "examples=/path/to/examples"]
    
    # Should generate correct arguments
    server_config = registry.get("mcp-server-filesystem")
    user_params = {
        "project_dir": parsed_args.project_dir,
        "reference_project": parsed_args.reference_project
    }
    
    args = server_config.generate_args(user_params, use_cli_command=True)
    
    # Verify final argument structure
    ref_count = args.count("--reference-project")
    assert ref_count == 2
    assert "docs=/path/to/docs" in args
    assert "examples=/path/to/examples" in args

def test_reference_projects_with_different_clients():
    """Test reference projects work with different MCP clients."""
    from mcp_config.servers import registry
    
    server_config = registry.get("mcp-server-filesystem")
    user_params = {
        "project_dir": "/base/project",
        "reference_project": ["docs=/path/to/docs"]
    }
    
    # Should work for CLI command mode
    cli_args = server_config.generate_args(user_params, use_cli_command=True)
    assert "--reference-project" in cli_args
    assert "docs=/path/to/docs" in cli_args
    
    # Should work for direct execution mode
    direct_args = server_config.generate_args(user_params, use_cli_command=False)
    assert "--reference-project" in direct_args
    assert "docs=/path/to/docs" in direct_args

def test_dry_run_shows_reference_projects():
    """Test dry-run output includes reference project arguments."""
    from mcp_config.servers import registry
    
    server_config = registry.get("mcp-server-filesystem")
    user_params = {
        "project_dir": "/base/project",
        "reference_project": ["docs=/docs", "examples=/examples"]
    }
    
    args = server_config.generate_args(user_params, use_cli_command=True)
    
    # Convert to command string (simulating dry-run display)
    cmd_parts = ["mcp-server-filesystem"] + args
    command_string = " ".join(cmd_parts)
    
    # Should show both reference projects in the command
    assert "--reference-project docs=/docs" in command_string
    assert "--reference-project examples=/examples" in command_string

def test_backward_compatibility_unchanged():
    """Test that existing functionality still works after changes."""
    from mcp_config.servers import registry
    
    # Test MCP Code Checker (doesn't have reference projects)
    code_checker_config = registry.get("mcp-code-checker")
    user_params = {
        "project_dir": "/base/project",
        "log_level": "INFO"
    }
    
    args = code_checker_config.generate_args(user_params, use_cli_command=True)
    
    # Should work as before
    assert "--project-dir" in args
    assert "/base/project" in args
    assert "--log-level" in args
    assert "INFO" in args
    
    # Should not contain reference-project (not applicable to this server)
    assert "--reference-project" not in args
    
    # Test MCP Filesystem Server without reference projects
    fs_config = registry.get("mcp-server-filesystem")
    basic_params = {"project_dir": "/base/project"}
    
    basic_args = fs_config.generate_args(basic_params, use_cli_command=True)
    
    # Should work without reference projects
    assert "--project-dir" in basic_args
    assert "/base/project" in basic_args
    assert "--reference-project" not in basic_args

def test_mixed_parameter_types_integration():
    """Test integration with various parameter types and repeatable."""
    from mcp_config.servers import registry
    
    server_config = registry.get("mcp-server-filesystem")
    user_params = {
        "project_dir": "/base/project",  # Required path parameter
        "log_level": "DEBUG",             # Choice parameter
        "reference_project": [            # Repeatable string parameter
            "docs=/path/to/docs",
            "examples=/path/to/examples"
        ]
    }
    
    args = server_config.generate_args(user_params, use_cli_command=True)
    
    # Should contain all parameter types
    assert "--project-dir" in args
    assert "--log-level" in args
    assert "--reference-project" in args
    
    # Verify values
    assert "/base/project" in args
    assert "DEBUG" in args
    assert "docs=/path/to/docs" in args
    assert "examples=/path/to/examples" in args
    
    # Verify correct counts
    assert args.count("--reference-project") == 2
    assert args.count("--project-dir") == 1
    assert args.count("--log-level") == 1

def test_edge_case_empty_and_none_values():
    """Test edge cases with empty lists and None values."""
    from mcp_config.servers import registry
    
    server_config = registry.get("mcp-server-filesystem")
    
    # Test with empty reference project list
    empty_params = {
        "project_dir": "/base/project",
        "reference_project": []  # Empty list should be skipped
    }
    
    empty_args = server_config.generate_args(empty_params, use_cli_command=True)
    assert "--reference-project" not in empty_args
    
    # Test with None value (parameter not provided)
    none_params = {
        "project_dir": "/base/project"
        # reference_project not provided (None)
    }
    
    none_args = server_config.generate_args(none_params, use_cli_command=True)
    assert "--reference-project" not in none_args

def test_parameterized_repeatable_functionality():
    """Parameterized test covering multiple scenarios efficiently."""
    import pytest
    from mcp_config.servers import ServerConfig, ParameterDef
    
    @pytest.mark.parametrize("scenario", [
        {
            "name": "single_value",
            "input": ["value1"],
            "expected_count": 1,
            "expected_values": ["value1"]
        },
        {
            "name": "multiple_values", 
            "input": ["value1", "value2", "value3"],
            "expected_count": 3,
            "expected_values": ["value1", "value2", "value3"]
        },
        {
            "name": "empty_list",
            "input": [],
            "expected_count": 0,
            "expected_values": []
        }
    ])
    def parameterized_test_execution(scenario):
        config = ServerConfig(
            name="test-server",
            display_name="Test Server",
            main_module="test.py",
            parameters=[
                ParameterDef(
                    name="test-repeat",
                    arg_name="--test-repeat",
                    param_type="string",
                    repeatable=True
                )
            ]
        )
        
        user_params = {"test_repeat": scenario["input"]} if scenario["input"] else {}
        args = config.generate_args(user_params, use_cli_command=True)
        
        actual_count = args.count("--test-repeat")
        assert actual_count == scenario["expected_count"]
        
        for value in scenario["expected_values"]:
            assert value in args
    
    # Execute parameterized tests
    test_scenarios = [
        {"name": "single_value", "input": ["value1"], "expected_count": 1, "expected_values": ["value1"]},
        {"name": "multiple_values", "input": ["value1", "value2", "value3"], "expected_count": 3, "expected_values": ["value1", "value2", "value3"]},
        {"name": "empty_list", "input": [], "expected_count": 0, "expected_values": []}
    ]
    
    for scenario in test_scenarios:
        parameterized_test_execution(scenario)
```

### EXPECTED RESULT
Some tests may **FAIL** if there are integration issues, but most should **PASS** if Steps 1-4 were implemented correctly.

## Step 5b: Fix Any Integration Issues

### OBJECTIVE
Resolve any issues discovered by integration tests and ensure complete functionality.

### PROCESS
1. Run integration tests and identify failures
2. Debug issues systematically
3. Make minimal fixes to resolve integration problems
4. Re-run all tests (unit + integration) to ensure everything works
5. Document any design decisions or trade-offs made

## VERIFICATION
Run complete test suite:
- All unit tests from Steps 1-4 should **PASS**
- All integration tests should **PASS** 
- No regression in existing functionality
- End-to-end scenarios work correctly

## TDD ALGORITHM
```
1. Write comprehensive integration tests
2. Run tests - identify any integration failures (Red)
3. Fix integration issues with minimal changes
4. Run all tests - confirm everything passes (Green)
5. Refactor if needed to improve code quality
6. Final verification with complete test suite
```

## DATA
- **Input**: Complete feature implementation from Steps 1-4
- **Output**: Fully tested, production-ready repeatable parameter functionality
- **Structure**: Comprehensive test coverage across unit, integration, and edge case scenarios

## LLM Prompt
Using Test-Driven Development, implement Step 5 for integration testing and final verification. Write comprehensive integration tests that cover end-to-end scenarios, backward compatibility, edge cases, and cross-client functionality. Run all tests and fix any integration issues discovered. Ensure the complete repeatable parameter feature works correctly with the reference-project parameter while maintaining existing functionality. Verify all tests pass before considering the implementation complete.

## Notes
- **TDD Completion**: This step completes the TDD cycle with comprehensive integration testing
- **Quality Assurance**: Focus on real-world usage scenarios
- **Regression Protection**: Ensure existing features continue to work
- **Edge Case Coverage**: Handle empty lists, mixed parameters, various clients
- **Documentation**: Integration tests serve as usage examples
