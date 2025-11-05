# Test Isolation Strategy Guide

This document explains the comprehensive test isolation architecture implemented to prevent cross-test pollution and ensure reliable test execution.

## Table of Contents

1. [Overview](#overview)
2. [The Problem](#the-problem)
3. [The Solution](#the-solution)
4. [How to Use](#how-to-use)
5. [Architecture](#architecture)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

## Overview

The test suite uses a comprehensive isolation strategy to ensure that:

- **No real configuration files are accessed during tests**
- **Tests don't interfere with each other** (no cross-test pollution)
- **Test results are consistent** regardless of execution order
- **Temporary data is properly cleaned up** after each test

## The Problem

Before implementing this strategy, tests suffered from several issues:

1. **Cross-Test Pollution**: Tests in different files would share the same configuration files, causing one test's data to affect another test's results.

2. **Flaky Tests**: The test `TestClaudeDesktopHandler.test_load_missing_config` would fail when run as part of the full test suite but pass when run individually.

3. **Real File Access**: Tests could inadvertently access or modify real user configuration files.

4. **Execution Order Dependency**: Test results depended on the order in which tests were executed.

### Example of the Problem

```python
# Test A creates a server
handler.setup_server("test-server", {...})

# Later, Test B (in a different file) loads config
config = handler.load_config()
# Bug: Test B sees "test-server" created by Test A!
```

## The Solution

We implemented a three-layer isolation strategy:

### Layer 1: Global Session Isolation (`tests/conftest.py`)

- **Global fixtures** that apply to all tests automatically
- **Prevents automatic migration** that could access real files
- **Session-scoped safety net** for the entire test suite

### Layer 2: Base Test Classes (`tests/base_test_classes.py`)

- **Inheritance-based isolation** for common test patterns
- **Automatic fixture application** through `autouse=True`
- **Comprehensive handler mocking** for all client types

### Layer 3: Test-Specific Fixtures

- **Isolated temporary directories** per test function
- **Clean state guarantee** at the start of each test
- **Automatic cleanup** after each test

## How to Use

### For New Tests

#### Option 1: Use Base Classes (Recommended)

```python
from tests.base_test_classes import BaseClaudeDesktopTest

class TestMyFeature(BaseClaudeDesktopTest):
    """Test my feature with automatic isolation."""

    def test_something(self, handler):
        # handler is automatically isolated
        # No real config files will be accessed
        config = handler.load_config()
        assert config == {"mcpServers": {}}
```

#### Option 2: Use Fixtures Directly

```python
def test_something(isolated_temp_dir, mock_all_client_handlers):
    """Test with manual isolation."""
    from src.mcp_config.clients import ClaudeDesktopHandler

    handler = ClaudeDesktopHandler()
    # Handler uses isolated_temp_dir automatically
    config = handler.load_config()
    assert config == {"mcpServers": {}}
```

### Available Base Classes

- **`BaseClientHandlerTest`**: Generic base for all client handler tests
- **`BaseClaudeDesktopTest`**: Specific to Claude Desktop handler tests (provides `handler`, `sample_config`, `managed_server_config` fixtures)
- **`BaseClaudeCodeTest`**: Specific to Claude Code handler tests
- **`BaseIntegrationTest`**: For tests involving multiple client handlers

### Example: Converting Existing Tests

**Before:**
```python
class TestClaudeDesktopHandler:
    @pytest.fixture
    def temp_config_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture(autouse=True)
    def mock_config_path(self, temp_config_dir, monkeypatch):
        # 50+ lines of complex mocking code...
        pass

    def test_load_missing_config(self, handler, monkeypatch):
        # Workaround mock to prevent pollution
        def mock_load_config():
            return {"mcpServers": {}}
        monkeypatch.setattr(handler, "load_config", mock_load_config)
        # Test code...
```

**After:**
```python
from tests.base_test_classes import BaseClaudeDesktopTest

class TestClaudeDesktopHandler(BaseClaudeDesktopTest):
    def test_load_missing_config(self, handler):
        # Just test - isolation is automatic!
        config = handler.load_config()
        assert config == {"mcpServers": {}}
```

## Architecture

### Directory Structure

```
tests/
├── conftest.py                 # Global fixtures and configuration
├── base_test_classes.py        # Base classes with built-in isolation
├── fixtures/                   # Centralized test data
│   ├── __init__.py
│   ├── sample_configs.py       # Standard test configurations
│   └── mock_handlers.py        # Mock handler utilities
├── test_health/                # Test isolation validation
│   ├── __init__.py
│   └── test_isolation.py       # Health checks
└── test_config/                # Actual tests
    └── test_clients.py         # Client handler tests
```

### Key Components

#### 1. Global Test Isolation Fixture

Located in `tests/conftest.py`:

```python
@pytest.fixture(scope="session", autouse=True)
def global_test_isolation():
    """Ensure complete isolation from real config files."""
    # Patches get_client_handler to skip automatic migration
    # Prevents any test from accidentally accessing real files
```

**Scope:** Session (runs once for entire test session)
**AutoUse:** Yes (applies automatically to all tests)
**Purpose:** Safety net to prevent real file access

#### 2. Isolated Temporary Directory

```python
@pytest.fixture(scope="function")
def isolated_temp_dir():
    """Provide completely isolated temp directory for each test."""
    # Creates unique temp dir
    # Yields to test
    # Cleans up after test
```

**Scope:** Function (new directory for each test)
**AutoUse:** No (request explicitly or via base class)
**Purpose:** Isolated file system for each test

#### 3. Base Test Classes

```python
class BaseClientHandlerTest:
    @pytest.fixture(autouse=True)
    def setup_isolation(self, isolated_temp_dir, monkeypatch):
        """Automatically isolate all client handlers."""
        # Mocks all handler types
        # Forces them to use isolated_temp_dir
        # No need to do this manually in each test!
```

**Inheritance:** Extend this class for automatic isolation
**AutoUse:** Yes (via autouse fixture)
**Purpose:** Apply comprehensive mocking to all tests in the class

### Test Markers

Tests are automatically marked based on their characteristics:

- `@pytest.mark.unit`: Pure unit tests with no file I/O
- `@pytest.mark.integration`: Integration tests with file I/O
- `@pytest.mark.client_handler`: Tests for specific client handlers
- `@pytest.mark.cross_client`: Tests involving multiple clients
- `@pytest.mark.isolation_critical`: Tests that must be completely isolated

**Usage:**
```bash
# Run only unit tests
pytest -m unit

# Run only isolation-critical tests
pytest -m isolation_critical

# Run only client handler tests
pytest -m client_handler
```

## Best Practices

### DO ✅

1. **Inherit from base test classes** for automatic isolation
   ```python
   class TestMyFeature(BaseClaudeDesktopTest):
       pass
   ```

2. **Use centralized sample configs** from `tests/fixtures/sample_configs.py`
   ```python
   from tests.fixtures.sample_configs import get_sample_claude_desktop_config

   def test_something():
       config = get_sample_claude_desktop_config()
   ```

3. **Trust the isolation** - don't add workaround mocks
   ```python
   def test_load_missing_config(self, handler):
       config = handler.load_config()  # Just works!
       assert config == {"mcpServers": {}}
   ```

4. **Add health checks** when testing new isolation features
   ```python
   @pytest.mark.isolation_critical
   def test_my_isolation_feature(self, isolated_temp_dir):
       # Verify isolation works correctly
       pass
   ```

### DON'T ❌

1. **Don't access real config paths in tests**
   ```python
   # BAD
   real_path = Path.home() / ".config" / "claude"

   # GOOD
   config_path = handler.get_config_path()  # Uses isolated temp dir
   ```

2. **Don't manually create complex isolation fixtures**
   ```python
   # BAD - Use base class instead
   @pytest.fixture(autouse=True)
   def my_isolation(self, monkeypatch):
       # 50 lines of mocking...

   # GOOD
   class TestMyFeature(BaseClaudeDesktopTest):
       pass  # Isolation is automatic!
   ```

3. **Don't share state between tests**
   ```python
   # BAD
   class TestSuite:
       config = {}  # Shared state!

       def test_a(self):
           self.config["test"] = "value"

       def test_b(self):
           # Depends on test_a running first!
           assert self.config["test"] == "value"

   # GOOD
   class TestSuite(BaseClaudeDesktopTest):
       def test_a(self, handler):
           handler.setup_server("test", {...})

       def test_b(self, handler):
           # Independent - starts fresh
           config = handler.load_config()
   ```

4. **Don't skip cleanup in custom fixtures**
   ```python
   # BAD
   @pytest.fixture
   def my_temp_dir():
       tmpdir = tempfile.mkdtemp()
       yield Path(tmpdir)
       # Missing cleanup!

   # GOOD
   @pytest.fixture
   def my_temp_dir():
       tmpdir = tempfile.mkdtemp()
       try:
           yield Path(tmpdir)
       finally:
           shutil.rmtree(tmpdir, ignore_errors=True)
   ```

## Troubleshooting

### Test fails in full suite but passes individually

**Symptom:** Test passes when run alone but fails when run with other tests.

**Cause:** Cross-test pollution - another test is modifying shared state.

**Solution:**
1. Ensure the test class inherits from a base test class
2. Check that the test uses `isolated_temp_dir` fixture
3. Run isolation health checks: `pytest tests/test_health/test_isolation.py -v`

### Test sees data from another test

**Symptom:** Test loads config and sees servers it didn't create.

**Cause:** Tests are sharing the same config file path.

**Solution:**
```python
# Add this check at the start of your test
def test_something(self, handler):
    config_path = handler.get_config_path()
    assert "tmp" in str(config_path) or "temp" in str(config_path).lower()
    # Now you know isolation is working
```

### Real config file is being accessed

**Symptom:** Test modifies your real Claude Desktop configuration.

**Cause:** Handler is not properly mocked.

**Solution:**
1. Inherit from `BaseClaudeDesktopTest` or use `mock_all_client_handlers` fixture
2. Verify with: `pytest tests/test_health/test_isolation.py::test_no_real_config_access_claude_desktop -v`

### Temp files not cleaned up

**Symptom:** `/tmp` directory fills up with test data.

**Cause:** Exception during test prevents cleanup.

**Solution:**
- Use context managers and try/finally blocks
- The `isolated_temp_dir` fixture handles this automatically
- Run: `pytest tests/test_health/test_isolation.py::test_temp_directory_cleanup -v`

### Test execution order matters

**Symptom:** Tests pass when run in one order but fail in another.

**Cause:** Tests are sharing state somehow.

**Solution:**
1. Run tests in random order to catch issues: `pytest --random-order`
2. Each test should be independent
3. Use base classes for automatic isolation

## Health Checks

Run the isolation health checks to verify everything is working:

```bash
# Run all health checks
pytest tests/test_health/test_isolation.py -v

# Run specific isolation test
pytest tests/test_health/test_isolation.py::TestIsolationHealth::test_no_real_config_access_claude_desktop -v

# Check for real file pollution
pytest tests/test_health/test_isolation.py::TestFileSystemIsolation::test_no_real_files_created -v
```

**Health check categories:**
- **Real file access prevention**: Ensures tests don't touch real config files
- **Temp directory cleanup**: Verifies proper cleanup after tests
- **Cross-test pollution**: Checks for shared state between tests
- **Mock effectiveness**: Validates that mocking is working correctly

## Migration Guide

### Migrating Existing Tests

**Step 1:** Identify the test class that needs migration
```python
class TestMyHandler:
    # Old test code with manual isolation
```

**Step 2:** Import and inherit from base class
```python
from tests.base_test_classes import BaseClaudeDesktopTest

class TestMyHandler(BaseClaudeDesktopTest):
    # Rest of test code
```

**Step 3:** Remove manual isolation fixtures
```python
# DELETE these:
# - temp_config_dir fixture
# - mock_config_path fixture
# - clean_real_config fixture
# - Any manual monkeypatch mocking of handlers
```

**Step 4:** Simplify tests by removing workarounds
```python
# Before:
def test_something(self, handler, monkeypatch):
    def mock_load_config():
        return {"mcpServers": {}}
    monkeypatch.setattr(handler, "load_config", mock_load_config)
    config = handler.load_config()

# After:
def test_something(self, handler):
    config = handler.load_config()  # Just works!
```

**Step 5:** Run tests to verify
```bash
pytest tests/test_config/test_clients.py::TestMyHandler -v
```

## Summary

The test isolation architecture provides:

✅ **Automatic isolation** - No manual setup required
✅ **Reliable tests** - Consistent results regardless of execution order
✅ **Safe testing** - Real config files are never touched
✅ **Easy to use** - Inherit from base class and you're done
✅ **Health checks** - Automated validation of isolation
✅ **Centralized fixtures** - Reusable test data and utilities

**Result:** Tests are reliable, maintainable, and fast!
