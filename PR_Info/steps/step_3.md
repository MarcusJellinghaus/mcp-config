# Step 3: Update Argument Generation for Lists

## Objective
Modify the `ServerConfig.generate_args()` method to handle parameters that produce list values from repeatable CLI arguments.

## WHERE
- **File**: `src/mcp_config/servers.py` 
- **Method**: `ServerConfig.generate_args()` around line 150-200
- **Section**: Parameter processing loop

## WHAT
Enhance argument generation logic:
- Detect when parameter value is a list (from `action="append"`)
- Generate multiple `--param value` pairs for each list item
- Maintain existing behavior for single values

## HOW
- Integration: Modify existing parameter processing loop
- Add isinstance(value, list) check
- Use for loop to add multiple arg/value pairs

## ALGORITHM
```
1. Get parameter value from user_params
2. If param.repeatable and value is list:
3.   For each item in list: add arg_name, then item
4. Else: use existing single value logic
5. Continue with remaining parameters
```

## DATA
- **Input**: `user_params` dict potentially containing lists for repeatable params
- **Output**: `args` list with repeated `--param value` entries
- **Structure**: `["--reference-project", "docs=/path", "--reference-project", "examples=/path"]`

## LLM Prompt
Based on the summary in `pr_info/summary.md` and completing Steps 1-2, implement Step 3 to update argument generation. In `src/mcp_config/servers.py`, modify the `ServerConfig.generate_args()` method to handle list values from repeatable parameters. When a parameter is repeatable and its value is a list, generate multiple `--param value` pairs in the args list. Keep the existing logic for single values unchanged.

## Test Strategy
Write tests to verify:
- Single values generate single arg pairs as before
- List values generate multiple arg pairs correctly
- Empty lists are handled gracefully (no args added)
- Mixed repeatable and non-repeatable parameters work together
- Order of arguments is preserved
