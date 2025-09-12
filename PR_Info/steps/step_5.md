# Step 5: Integration Tests and Final Verification (TDD)

## Objective
Create comprehensive integration tests to verify the complete repeatable parameter functionality works end-to-end, and ensure backward compatibility.

## Step 5a: Write Integration Tests

### WHERE
- **Files**: Add to existing test files or create focused integration tests
  - `tests/test_config/test_integration.py` (if it exists) or relevant existing files
  - Focus on end-to-end scenarios

### INTEGRATION TESTS TO WRITE (SIMPLIFIED KISS APPROACH)
```python
def test_reference_project_end_to_end():
    """Test complete workflow: CLI parsing → argument generation → command execution."""
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
    
    # Test CLI parsing
    parsed_args, errors = parse_and_validate_args(test_args)
    assert len(errors) == 0
    assert parsed_args.server_type == "mcp-server-filesystem"
    assert parsed_args.reference_project == ["docs=/path/to/docs", "examples=/path/to/examples"]
    
    # Test argument generation
    server_config = registry.get("mcp-server-filesystem")
    user_params = {
        "project_dir": parsed_args.project_dir,
        "reference_project": parsed_args.reference_project
    }
    args = server_config.generate_args(user_params, use_cli_command=True)
    
    # Test final command structure
    assert args.count("--reference-project") == 2
    assert "docs=/path/to/docs" in args
    assert "examples=/path/to/examples" in args
    assert "--project-dir" in args
    assert "/base/project" in args

def test_reference_project_edge_cases():
    """Test empty lists, single values, None values."""
    from mcp_config.servers import registry
    
    server_config = registry.get("mcp-server-filesystem")
    
    # Test empty list (should be skipped)
    empty_params = {"project_dir": "/base/project", "reference_project": []}
    empty_args = server_config.generate_args(empty_params, use_cli_command=True)
    assert "--reference-project" not in empty_args
    
    # Test single value
    single_params = {"project_dir": "/base/project", "reference_project": ["docs=/docs"]}
    single_args = server_config.generate_args(single_params, use_cli_command=True)
    assert single_args.count("--reference-project") == 1
    assert "docs=/docs" in single_args
    
    # Test None/missing (should be skipped)
    none_params = {"project_dir": "/base/project"}
    none_args = server_config.generate_args(none_params, use_cli_command=True)
    assert "--reference-project" not in none_args

def test_filesystem_server_command_generation():
    """Test actual mcp-server-filesystem command with reference projects."""
    from mcp_config.servers import registry
    
    server_config = registry.get("mcp-server-filesystem")
    user_params = {
        "project_dir": "/base/project",
        "reference_project": ["docs=/docs", "examples=/examples"]
    }
    
    # Generate command arguments
    args = server_config.generate_args(user_params, use_cli_command=True)
    
    # Create full command (simulating what would be executed)
    cmd_parts = ["mcp-server-filesystem"] + args
    command_string = " ".join(cmd_parts)
    
    # Verify command contains expected elements
    assert "mcp-server-filesystem" in command_string
    assert "--project-dir /base/project" in command_string
    assert "--reference-project docs=/docs" in command_string
    assert "--reference-project examples=/examples" in command_string
    
    # Verify it's a valid, executable command structure
    assert command_string.count("--reference-project") == 2
    assert command_string.startswith("mcp-server-filesystem")
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
