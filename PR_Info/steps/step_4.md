# Step 4: Add Reference Project Parameter Definition

## Objective
Add the `reference-project` parameter to the `MCP_FILESYSTEM_SERVER` configuration to enable users to specify multiple reference projects.

## WHERE
- **File**: `src/mcp_config/servers.py`
- **Variable**: `MCP_FILESYSTEM_SERVER` configuration around line 350-400
- **Section**: `parameters` list

## WHAT
Add new ParameterDef to parameters list:
- `name`: "reference-project"
- `arg_name`: "--reference-project"
- `param_type`: "string" (treat as simple string, no special parsing)
- `required`: False
- `repeatable`: True (use new field from Step 1)
- `help`: Descriptive help text

## HOW
- Integration: Append to existing `parameters` list in MCP_FILESYSTEM_SERVER
- Import: No new imports needed
- Position: Add after existing parameters (log-file is currently last)

## ALGORITHM
```
1. Locate MCP_FILESYSTEM_SERVER.parameters list
2. Add new ParameterDef for reference-project
3. Set repeatable=True to enable multiple values
4. Use param_type="string" for simple pass-through
5. Verify parameter appears in help output
```

## DATA
- **Input**: Existing MCP_FILESYSTEM_SERVER configuration
- **Output**: Enhanced config with reference-project parameter
- **Structure**: ParameterDef with name="reference-project", repeatable=True

## LLM Prompt
Based on the summary in `pr_info/summary.md` and completing Steps 1-3, implement Step 4 to add the parameter definition. In `src/mcp_config/servers.py`, add a new `ParameterDef` to the `MCP_FILESYSTEM_SERVER.parameters` list for the `reference-project` parameter. Set `repeatable=True` to enable multiple values, use `param_type="string"` for simple pass-through, and make it optional with `required=False`. The help text should explain the name=path format and that it can be repeated.

## Test Strategy
Write tests to verify:
- Parameter appears in CLI help for mcp-server-filesystem
- Parameter accepts multiple values via `--reference-project name=path`
- Generated arguments include repeated `--reference-project` entries
- Integration test with full setup command works end-to-end
- Dry-run shows correct argument structure
