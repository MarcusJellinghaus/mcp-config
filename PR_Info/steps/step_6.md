# Step 6: Documentation Updates

## Objective
Add simple documentation for the new `--reference-project` parameter to ensure users understand how to use the feature.

## Step 6a: Verify CLI Help Text

### WHERE
- **Generated**: CLI help text from `build_setup_parser()`
- **Verification**: Manual testing and automated test coverage

### WHAT TO VERIFY
- `--reference-project` parameter appears in help output
- Help text clearly explains the format and repeatability
- Help text is concise and user-friendly

### VERIFICATION STEPS
```bash
# Test CLI help includes the parameter
mcp-config setup mcp-server-filesystem --help

# Should show:
# --reference-project REFERENCE_PROJECT
#                     Reference project (format: name=path). Repeatable.
#                     Example: --reference-project docs=/path/to/docs
```

## Step 6b: Update Parameter Help Text (if needed)

### WHERE
- **File**: `src/mcp_config/servers.py`
- **Section**: `MCP_FILESYSTEM_SERVER` parameter definition

### IMPLEMENTATION
Ensure the help text in the ParameterDef is clear and concise:
```python
ParameterDef(
    name="reference-project",
    arg_name="--reference-project",
    param_type="string",
    required=False,
    repeatable=True,
    help="Reference project (format: name=path). Repeatable. "
         "Example: --reference-project docs=/path/to/docs"
),
```

## Step 6c: Add Usage Example to README (Optional)

### WHERE
- **File**: `README.md` or `USER_GUIDE.md`
- **Section**: Usage examples or filesystem server documentation

### WHAT TO ADD (SIMPLE)
Add a brief example showing the new parameter:

```markdown
### MCP Filesystem Server with Reference Projects

```bash
mcp-config setup mcp-server-filesystem myfs \
  --project-dir /path/to/main/project \
  --reference-project docs=/path/to/documentation \
  --reference-project examples=/path/to/examples
```

This allows the filesystem server to access multiple project directories.
```

## VERIFICATION
- CLI help displays reference-project parameter correctly
- Help text is clear and includes example usage
- Optional: README includes basic usage example
- No extensive documentation needed (KISS principle)

## TDD ALGORITHM
```
1. Run CLI help command and verify output
2. Check help text clarity and completeness
3. Update help text if needed (simple changes only)
4. Optionally add brief usage example to documentation
5. Final verification that users can understand how to use the feature
```

## DATA
- **Input**: Implemented reference-project parameter
- **Output**: Clear, simple documentation for users
- **Structure**: Concise help text + optional usage example

## LLM Prompt
Implement Step 6 for simple documentation updates. Verify that CLI help text for the --reference-project parameter is clear and includes the format and repeatability information. Make any necessary updates to help text to be user-friendly. Optionally add a brief usage example to README.md or USER_GUIDE.md. Keep documentation simple and focused on essential usage information (KISS principle).

## Notes
- **Keep it simple**: Focus on essential information only
- **User-focused**: Help text should be immediately actionable
- **No extensive guides**: Brief, practical examples only
- **Verify help display**: Actual CLI help should be clear and complete
