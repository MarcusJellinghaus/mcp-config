# Test Isolation Guide

This guide explains how to write isolated, reliable tests using the base test classes and fixtures.

## Quick Start

### Writing New Tests

**Recommended: Use base classes**

```python
from tests.base_test_classes import BaseClaudeDesktopTest

class TestMyFeature(BaseClaudeDesktopTest):
    def test_something(self, handler):
        # Automatic isolation - handler uses temp directory
        config = handler.load_config()
        assert config == {"mcpServers": {}}
```

### Available Base Classes

- **`BaseClientHandlerTest`** - Generic base for all client handler tests
- **`BaseClaudeDesktopTest`** - Claude Desktop tests (provides `handler`, `sample_config` fixtures)
- **`BaseClaudeCodeTest`** - Claude Code tests
- **`BaseIntegrationTest`** - Multi-handler tests (provides `all_handlers` fixture)

## Why Isolation?

The test isolation architecture prevents:
- ❌ Cross-test pollution (Test A's data affecting Test B)
- ❌ Real config file access (tests modifying user files)
- ❌ Execution order dependency (results change based on test order)
- ❌ Flaky tests (passes alone, fails in suite)

## Architecture

### Directory Structure
```
tests/
├── conftest.py              # Global fixtures
├── base_test_classes.py     # Base classes with auto-isolation
├── fixtures/                # Centralized test data
│   ├── sample_configs.py
│   └── mock_handlers.py
└── test_health/             # Isolation validation
    └── test_isolation.py
```

### Key Components

**1. Global Fixtures (`conftest.py`)**
- `isolated_temp_dir` - Fresh temp directory per test
- `sample_configs` - Centralized test data
- `global_test_isolation` - Session-scoped safety net

**2. Base Classes (`base_test_classes.py`)**
- Auto-mocks all handlers to use `isolated_temp_dir`
- Separate subdirectories per handler type:
  - `isolated_temp_dir/claude_desktop/`
  - `isolated_temp_dir/claude_code/`
  - `isolated_temp_dir/vscode/`

**3. Test Markers**
```bash
pytest -m unit                # Unit tests only
pytest -m integration         # Integration tests only
pytest -m isolation_critical  # Isolation validation tests
```

## Best Practices

### ✅ DO

```python
# Inherit from base classes
class TestMyFeature(BaseClaudeDesktopTest):
    pass

# Use centralized test data
from tests.fixtures.sample_configs import get_sample_claude_desktop_config

# Trust the isolation - no workarounds needed
def test_load_config(self, handler):
    config = handler.load_config()  # Just works!
```

### ❌ DON'T

```python
# Don't access real config paths
real_path = Path.home() / ".config" / "claude"  # BAD

# Don't create manual isolation fixtures
@pytest.fixture(autouse=True)
def my_isolation(self, monkeypatch):  # BAD - use base class instead
    # 50 lines of mocking...

# Don't share state between tests
class TestSuite:
    config = {}  # BAD - shared mutable state
```

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Test fails in suite, passes alone | Cross-test pollution | Inherit from base class, verify with health checks |
| Test sees data from another test | Shared config paths | Check `handler.get_config_path()` is in temp dir |
| Real config file accessed | Handler not mocked | Use base class or `mock_all_client_handlers` fixture |
| Temp files not cleaned up | Missing cleanup | Use `isolated_temp_dir` fixture (auto-cleanup) |
| Results depend on test order | Shared state | Make tests independent, use base classes |

### Verify Isolation
```bash
# Run health checks
pytest tests/test_health/test_isolation.py -v

# Test in random order
pytest --random-order

# Check specific isolation
pytest tests/test_health/test_isolation.py::TestIsolationHealth::test_no_real_config_access_claude_desktop -v
```

## Migration Guide

**Convert existing test:**

```python
# BEFORE: Manual isolation (150+ lines of fixtures)
class TestClaudeDesktopHandler:
    @pytest.fixture
    def temp_config_dir(self):
        # 20+ lines...

    @pytest.fixture(autouse=True)
    def mock_config_path(self, monkeypatch):
        # 50+ lines...

    def test_something(self, handler, monkeypatch):
        # Workaround mocks...
        def mock_load_config():
            return {"mcpServers": {}}
        monkeypatch.setattr(handler, "load_config", mock_load_config)
        config = handler.load_config()

# AFTER: Use base class (simple!)
from tests.base_test_classes import BaseClaudeDesktopTest

class TestClaudeDesktopHandler(BaseClaudeDesktopTest):
    def test_something(self, handler):
        config = handler.load_config()  # Isolation automatic!
```

**Steps:**
1. Import base class: `from tests.base_test_classes import BaseClaudeDesktopTest`
2. Inherit: `class TestMyHandler(BaseClaudeDesktopTest):`
3. Delete manual fixtures: `temp_config_dir`, `mock_config_path`, etc.
4. Remove workaround mocks
5. Run tests: `pytest tests/test_config/test_clients.py::TestMyHandler -v`

## Summary

**Test isolation provides:**
- ✅ Automatic isolation - no manual setup
- ✅ Reliable tests - consistent results
- ✅ Safe testing - real files protected
- ✅ Easy to use - just inherit from base class
- ✅ Health checks - automated validation

**Result:** Write less code, get more reliable tests!
