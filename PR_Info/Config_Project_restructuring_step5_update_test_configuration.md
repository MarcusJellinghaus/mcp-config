# Step 5: Update Test Configuration and Run Validation

## Overview
Update test files to import from correct modules after restructuring, ensure test data paths are correct, and run comprehensive validation to verify everything works.

## Test Files to Update

### 1. Import Statement Updates
All test files need to import from the correct restructured modules.

**Files to check and update:**
```
tests/test_config/
├── test_clients.py
├── test_cli_utils.py
├── test_detection.py
├── test_discovery.py
├── test_dry_run.py
├── test_integration.py
├── test_main.py
├── test_output.py
├── test_output_enhanced.py
├── test_servers.py
├── test_utils.py
├── test_validation.py
├── test_validation_enhanced.py
├── test_vscode_cli.py
├── test_vscode_handler.py
├── test_vscode_integration.py
├── test_vscode_performance.py
└── [other test files]
```

**Expected import patterns in test files:**
```python
# Correct imports for test files:
from src.mcp_config.main import main
from src.mcp_config.servers import registry, ServerConfig
from src.mcp_config.clients import get_client_handler
from src.mcp_config.validation import validate_server_configuration
# etc.

# NOT these (old patterns):
from src.main import main  # Wrong - this was the old duplicate
from src.servers import registry  # Wrong - this was removed
```

### 2. Test Data Path Verification
Ensure test data paths are still correct after restructuring.

**Expected test data structure:**
```
tests/testdata/
├── test_command_runner_stdio/
│   └── README.md
└── [other test data directories]
```

**Verify these paths in test files:**
- References to `tests/testdata/` should still work
- Any hardcoded paths need to be checked
- Temporary file creation paths should be verified

### 3. Specific Test Files Requiring Updates

**tests/test_config/test_main.py:**
- Import: `from src.mcp_config.main import main`
- CLI command testing
- Argument parsing tests

**tests/test_config/test_servers.py:**
- Import: `from src.mcp_config.servers import registry, ServerConfig, ParameterDef`
- Server configuration tests
- Registry functionality tests

**tests/test_config/test_clients.py:**
- Import: `from src.mcp_config.clients import get_client_handler`
- Client handler tests

**tests/test_config/test_integration.py:**
- Import: `from src.mcp_config.integration import setup_mcp_server, remove_mcp_server`
- Integration tests

## Test Configuration Updates

### 1. pytest Configuration
Verify `pyproject.toml` pytest configuration is still correct:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_default_fixture_loop_scope = "function"
pythonpath = ["."]  # This should still work
markers = [
    "cli: Tests for CLI command functionality",
    "installation: Tests for installation modes"
]
```

### 2. PYTHONPATH Considerations
The current `pythonpath = ["."]` should still work because:
- Tests import `src.mcp_config.*`
- The root directory (.) contains the `src/` folder

## Validation Steps

### 1. Import Validation
Test that all imports work correctly:

```bash
# Run a simple import test for each major test file
python -c "
try:
    from src.mcp_config.main import main
    from src.mcp_config.servers import registry
    from src.mcp_config.clients import get_client_handler
    print('✓ Core imports successful')
except ImportError as e:
    print(f'✗ Import error: {e}')
"
```

### 2. Individual Test File Validation
Check each test file can be imported:

```bash
# Test each file can be loaded
python -m pytest tests/test_config/test_main.py --collect-only
python -m pytest tests/test_config/test_servers.py --collect-only
python -m pytest tests/test_config/test_clients.py --collect-only
# etc.
```

### 3. Run Complete Test Suite
```bash
# Run all tests to identify any remaining issues
python -m pytest tests/ -v
```

## Comprehensive Code Quality Validation

After fixing all import issues, run the full validation sequence:

### 1. Pylint Check
```bash
# Run pylint with error and fatal categories only (as per guidelines)
python -m pylint src/ --disable=all --enable=E,F
```

**Expected result:** No errors or fatal issues

### 2. Pytest Check  
```bash
# Run complete test suite
python -m pytest tests/ -v
```

**Expected result:** All tests pass

### 3. MyPy Type Check
```bash
# Run mypy with strict settings
python -m mypy src/ --strict
```

**Expected result:** No type errors

## Common Issues and Solutions

### 1. Import Errors in Tests
**Issue:** `ModuleNotFoundError: No module named 'src.mcp_config'`

**Solutions:**
- Verify PYTHONPATH includes root directory
- Check import statements use full module paths
- Ensure `__init__.py` files are present

### 2. Test Data Path Issues
**Issue:** Test data files not found

**Solutions:**  
- Verify `tests/testdata/` paths are correct
- Check relative path calculations in tests
- Update hardcoded paths if necessary

### 3. Circular Import Issues
**Issue:** `ImportError: cannot import name 'X' from partially initialized module`

**Solutions:**
- Review import dependencies between modules
- Use delayed imports if necessary
- Restructure interdependent code

## Expected Results

### After Import Fixes:
- All test files import successfully
- No `ModuleNotFoundError` exceptions
- Test collection works without errors

### After Full Validation:
- **Pylint**: No errors or fatal issues
- **Pytest**: All tests pass  
- **MyPy**: No type checking errors
- CLI command works: `mcp-config --help`

## Specific Test Commands to Run

```bash
# 1. Test import health
python -c "import src.mcp_config; print('Package imports successfully')"

# 2. Test CLI functionality
python -m src.mcp_config.main --help

# 3. Test individual modules
python -c "from src.mcp_config.servers import registry; print(f'Found {len(registry.list_servers())} servers')"

# 4. Run specific test categories
python -m pytest tests/test_config/ -v -k "not test_vscode"

# 5. Full test suite
python -m pytest tests/ -v
```

## Final Validation Checklist

- [ ] All test files import without errors
- [ ] Test data paths are accessible  
- [ ] Pylint shows no errors/fatal issues
- [ ] All tests pass
- [ ] MyPy shows no type errors
- [ ] CLI command responds correctly
- [ ] Package can be imported successfully

## Next Step
After completing this step, proceed to Step 6: Final CLI Testing and Documentation Verification.
