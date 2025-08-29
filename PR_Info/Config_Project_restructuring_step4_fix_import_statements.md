# Step 4: Fix Import Statements and Module References

## Overview
Ensure all import statements throughout the codebase use the correct module paths after the restructuring. This step focuses on internal imports within the mcp_config package.

## Current Import Structure Analysis

### Expected Import Patterns
All internal imports should use relative imports within the `mcp_config` package:

```python
# Correct patterns:
from . import module_name
from .module_name import function_name
from .submodule.module_name import ClassName

# Avoid absolute imports for internal modules:
# from src.mcp_config.module_name import something  # Don't use this
# import mcp_config.module_name  # Don't use this for internal imports
```

## Files to Review and Update

### 1. src/mcp_config/main.py
**Expected imports:**
```python
from . import initialize_all_servers
from .cli_utils import create_full_parser, validate_setup_args
from .clients import get_client_handler
from .detection import detect_python_environment
from .integration import (
    build_server_config,
    remove_mcp_server,
    setup_mcp_server,
)
from .output import OutputFormatter
from .servers import registry
from .utils import validate_required_parameters
from .validation import (
    validate_client_installation,
    validate_parameter_combination,
    validate_server_configuration,
)
```

**Check for:**
- Incorrect absolute imports
- Missing relative import dots
- References to old module paths

### 2. src/mcp_config/__init__.py
**Expected imports:**
```python
from .discovery import initialize_external_servers
from .servers import registry
```

**Check for:**
- Proper relative imports
- No references to removed duplicate modules

### 3. All Other Module Files
Review each file in `src/mcp_config/` for import statements:

**Files to check:**
- `clients.py`
- `cli_utils.py`  
- `detection.py`
- `discovery.py`
- `errors.py`
- `help_system.py`
- `integration.py`
- `output.py`
- `paths.py`
- `python_detection.py`
- `servers.py`
- `utils.py`
- `validation.py`

### 4. Test Files
**Check test imports in tests/ directory:**

All test files should import from the correct source location:
```python
# Correct patterns:
from src.mcp_config.module_name import function_name
import src.mcp_config.module_name

# Check these files specifically:
# tests/test_config/*.py files
```

## Specific Import Issues to Fix

### 1. Cross-module Dependencies
Ensure all internal references use relative imports:

**Example fixes needed:**
```python
# If found:
from mcp_config.servers import registry
# Change to:
from .servers import registry

# If found:  
import src.mcp_config.utils
# Change to:
from . import utils
```

### 2. Circular Import Prevention
Check for potential circular import issues after restructuring:

**Common patterns that cause issues:**
- `main.py` importing from modules that import back from `main.py`
- `__init__.py` importing modules that import from `__init__.py`

### 3. External Dependencies
Verify external imports remain correct:
```python
# These should remain unchanged:
import argparse
import sys
from pathlib import Path
from typing import Any
import logging
# etc.
```

## Module Dependency Map
Based on the current structure, here's the expected dependency flow:

```
main.py
├── cli_utils (parser creation)
├── clients (client handlers)
├── detection (environment detection)
├── integration (server setup/remove)
├── output (formatting)
├── servers (registry)
├── utils (validation helpers)
└── validation (comprehensive validation)

__init__.py
├── discovery (external server discovery)
└── servers (registry access)

Other modules have their own internal dependencies
```

## Validation Steps

### 1. Static Analysis
Run these commands to check for import issues:
```bash
# Check for import errors
python -m py_compile src/mcp_config/__init__.py
python -m py_compile src/mcp_config/main.py

# Check each module can be imported
python -c "import src.mcp_config"
python -c "from src.mcp_config.main import main"
```

### 2. Import Testing
Create a simple test to verify all modules import correctly:
```python
# Test script content:
try:
    from src.mcp_config import initialize_all_servers
    from src.mcp_config.main import main
    from src.mcp_config.servers import registry
    print("✓ All critical imports successful")
except ImportError as e:
    print(f"✗ Import error: {e}")
```

### 3. CLI Functionality Test
```bash
# Test the CLI loads without import errors
python -m src.mcp_config.main --help
# or
mcp-config --help
```

## Common Import Error Patterns to Fix

### 1. Absolute imports within package
```python
# Wrong:
from src.mcp_config.servers import registry
# Right:
from .servers import registry
```

### 2. Missing relative import indicators
```python
# Wrong:
import servers
# Right:  
from . import servers
```

### 3. Old module path references
```python
# Wrong (references removed duplicate modules):
from src.servers import registry
# Right:
from .servers import registry
```

## Expected Result
- All internal imports use correct relative import patterns
- No references to removed duplicate modules
- No circular import issues
- All modules can be imported successfully
- CLI command loads without import errors
- Test files import from correct source paths

## Next Step
After completing this step, proceed to Step 5: Update Test Configuration and Run Validation.
