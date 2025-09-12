# Step 1: Add Repeatable Parameter Support to ParameterDef

## Objective
Extend the `ParameterDef` dataclass to support parameters that can be specified multiple times on the command line.

## WHERE
- **File**: `src/mcp_config/servers.py`
- **Class**: `ParameterDef` dataclass
- **Lines**: Around line 15-35 (dataclass definition)

## WHAT
Add a new field to enable repeatable parameters:
- `repeatable: bool = False` - field to mark parameters as repeatable

## HOW
- Add field to existing `@dataclass` definition
- Set default value to maintain backward compatibility
- No additional imports or decorators needed

## ALGORITHM
```
1. Locate ParameterDef dataclass definition
2. Add repeatable field after existing fields
3. Set default value to False
4. Verify no breaking changes to existing parameters
5. Update docstring to document new field
```

## DATA
- **Input**: Existing ParameterDef with current fields
- **Output**: Enhanced ParameterDef with repeatable support
- **Structure**: `repeatable: bool = False` added to dataclass fields

## LLM Prompt
Based on the summary in `pr_info/summary.md`, implement Step 1 of adding reference-project parameter support. Extend the `ParameterDef` dataclass in `src/mcp_config/servers.py` to include a `repeatable: bool = False` field. This field will indicate whether a parameter can be specified multiple times on the command line. Keep the change minimal and ensure backward compatibility by using a default value of False.

## Test Strategy
Write a simple unit test to verify that:
- New ParameterDef instances can be created with repeatable=True
- Default value is False when not specified
- Existing parameter definitions continue to work unchanged
