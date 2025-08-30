# Step 1: Clean Up Duplicate Code Structure

## Overview
The mcp-config project currently has duplicate module structures from its separation from mcp-code-checker. This step removes the old duplicate files and ensures a clean, single module structure.

## Current Problematic Structure
```
src/
├── main.py (delegator - keep but modify)
├── __init__.py (old duplicate - remove)
├── clients.py (old duplicate - remove)
├── cli_utils.py (old duplicate - remove)
├── detection.py (old duplicate - remove)
├── discovery.py (old duplicate - remove)
├── help_system.py (old duplicate - remove)
├── output.py (old duplicate - remove)
├── servers.py (old duplicate - remove)
├── utils.py (old duplicate - remove)
├── validation.py (old duplicate - remove)
└── mcp_config/ (correct structure - keep all)
    ├── __init__.py
    ├── main.py
    ├── clients.py
    ├── cli_utils.py
    ├── detection.py
    ├── discovery.py
    ├── errors.py
    ├── help_system.py
    ├── integration.py
    ├── output.py
    ├── paths.py
    ├── python_detection.py
    ├── servers.py
    ├── utils.py
    └── validation.py
```

## Target Structure
```
src/
├── main.py (simple delegator)
└── mcp_config/ (all functionality here)
    ├── __init__.py
    ├── main.py (actual CLI entry point)
    └── [all other modules]
```

## Files to Remove
The following duplicate files in `src/` should be deleted:
- `src/__init__.py`
- `src/clients.py`
- `src/cli_utils.py`
- `src/detection.py`
- `src/discovery.py`
- `src/help_system.py`
- `src/output.py`
- `src/servers.py`
- `src/utils.py`
- `src/validation.py`

## File to Update
Update `src/main.py` to be a simple delegator:

```python
"""Main entry point for MCP Config tool."""

import sys
from .mcp_config.main import main

if __name__ == "__main__":
    sys.exit(main())
```

## Validation Steps
1. Verify all duplicate files are removed
2. Verify `src/main.py` correctly delegates to `src.mcp_config.main:main`
3. Verify `src/mcp_config/` contains all required modules:
   - `__init__.py`
   - `main.py` (actual CLI implementation)
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

## Expected Result
- Clean module structure with no duplicates
- All functionality in `src/mcp_config/` directory
- Simple delegator in `src/main.py`
- Entry point in pyproject.toml still works: `src.mcp_config.main:main`

## Next Step
After completing this step, proceed to Step 2: Update Documentation and References.
