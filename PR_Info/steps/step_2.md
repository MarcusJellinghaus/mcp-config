# Step 2: Update CLI Parser for Repeatable Parameters

## Objective
Modify the CLI argument parser to use `action="append"` for parameters marked as repeatable, allowing multiple values to be collected into a list.

## WHERE
- **File**: `src/mcp_config/cli_utils.py`
- **Function**: `add_parameter_to_parser(parser, param)` around line 85-120
- **Integration**: argparse argument addition logic

## WHAT
Main changes to function signature (no change) and logic:
- Detect when `param.repeatable` is True
- Set `action="append"` for repeatable parameters
- Ensure proper metavar for help display

## HOW
- Import: No new imports needed (argparse already imported)
- Integration: Modify kwargs dict before `parser.add_argument()`
- Conditional logic based on `param.repeatable` attribute

## ALGORITHM
```
1. Check if param.repeatable is True
2. If repeatable, set kwargs["action"] = "append"
3. Ensure metavar is appropriate for repeated values
4. Add argument with modified kwargs
5. Non-repeatable parameters use existing logic
```

## DATA
- **Input**: `param` with potential `repeatable=True`
- **Output**: argparse argument configured for multiple values
- **Structure**: kwargs dict with `"action": "append"` when repeatable

## LLM Prompt
Based on the summary in `pr_info/summary.md` and completing Step 1, implement Step 2 to update the CLI parser. In `src/mcp_config/cli_utils.py`, modify the `add_parameter_to_parser()` function to handle repeatable parameters. When `param.repeatable` is True, set `kwargs["action"] = "append"` before calling `parser.add_argument()`. This allows users to specify the same parameter multiple times and collect values into a list.

## Test Strategy
Write tests to verify:
- Repeatable parameters accept multiple values: `--param value1 --param value2`
- Non-repeatable parameters work unchanged
- Help text displays correctly for repeatable parameters
- Empty cases (no values provided) handled gracefully
