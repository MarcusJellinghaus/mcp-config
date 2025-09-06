# Step 5: Integration Tests and Documentation

## LLM Prompt
```
Referring to the Summary: IntelliJ MCP Client Support with JSON Comments, implement Step 5: Create comprehensive integration tests and update all documentation. Ensure end-to-end functionality works correctly and users have clear guidance on using IntelliJ support.
```

## WHERE
- **Files**:
  - `tests/test_config/test_intellij_integration.py` (new)
  - `tests/manual_intellij_testing.md` (new)
  - `README.md` (update)
  - `USER_GUIDE.md` (update)
  - `CONTRIBUTING.md` (update)
  - `pyproject.toml` (finalize dependencies)

## WHAT
### Integration Tests
```python
def test_intellij_end_to_end_workflow()
def test_comment_preservation_integration() 
def test_intellij_with_real_config_files()
def test_cross_platform_compatibility()
def test_metadata_integration()
```

### Documentation Updates
- **README.md**: Add IntelliJ to supported clients
- **USER_GUIDE.md**: Complete IntelliJ section with examples
- **Manual Testing**: Create manual testing guide

## HOW
### Integration Points
- **End-to-End Tests**: Test complete workflow from CLI to config file
- **Real File Tests**: Use temporary files that mimic real IntelliJ configs
- **Cross-Platform**: Mock different platforms and test path resolution
- **Documentation**: Follow existing documentation patterns and style

### Test Scenarios
```python
# Key integration test scenarios
1. Setup server with comments -> verify comments preserved
2. Remove server -> verify comments in other sections preserved  
3. List servers -> verify correct output format
4. Validate config -> verify JSONC validation works
5. CLI integration -> verify all commands work end-to-end
```

## ALGORITHM
```
1. Create realistic IntelliJ config with comments
2. Run full CLI workflow (setup, list, remove, validate)
3. Verify comments preserved at each step
4. Test error conditions and recovery
5. Document usage patterns and troubleshooting
```

## DATA
### Test Data
```python
SAMPLE_INTELLIJ_CONFIG = '''
{
    // IntelliJ MCP Configuration
    "servers": {
        /* Code checker server for Python projects */
        "code-checker": {
            "command": "python",
            "args": ["checker.py"], // Main script
            "env": {
                "DEBUG": "true" // Enable debug mode
            }
        }
    }
}
'''
```

### Documentation Examples
- **Setup**: `mcp-config setup mcp-code-checker "Project" --client intellij`
- **Configuration**: Show JSONC format with comments
- **Troubleshooting**: Common issues and solutions

## Tests to Write First
1. **Test complete setup workflow** with IntelliJ client
2. **Test comment preservation** throughout operations
3. **Test CLI error handling** with IntelliJ-specific errors
4. **Test configuration validation** with malformed JSONC
5. **Test backup and restore** functionality
6. **Test metadata handling** integration
7. **Test help system** integration
8. **Test cross-platform** path handling
9. **Test fallback behavior** when json-five unavailable
10. **Test real-world scenarios** with complex configs

### Manual Testing Checklist
- [ ] Install on clean system
- [ ] Test IntelliJ config detection
- [ ] Test comment preservation manually
- [ ] Test with existing IntelliJ configs
- [ ] Test error recovery
- [ ] Verify cross-platform paths
- [ ] Test with various JetBrains IDEs
