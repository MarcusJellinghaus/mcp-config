# Add Reference Project Parameter Support

## Overview
Add support for the `--reference-project` parameter to the mcp-server-filesystem configuration in mcp-config. This parameter allows users to specify multiple reference projects using `--reference-project name=/path/to/dir` syntax.

## Key Changes
- Extend `ParameterDef` class to support repeatable parameters
- Update CLI parser to handle `action="append"` for repeatable parameters  
- Modify argument generation to process list values from repeatable parameters
- Add `reference-project` parameter to `MCP_FILESYSTEM_SERVER` configuration

## Implementation Philosophy
- **Keep it simple**: Treat reference projects as plain strings, no special parsing
- **Pass-through approach**: Config layer doesn't validate name=path format - let filesystem server handle it
- **Minimal changes**: Reuse existing string parameter type and infrastructure
- **No client changes**: All handlers already support arbitrary argument lists

## Expected Behavior
After implementation, users can run:
```bash
mcp-config setup mcp-server-filesystem myfs \
  --project-dir /main/project \
  --reference-project docs=/path/to/docs \
  --reference-project examples=/path/to/examples
```

This generates a configuration with repeated `--reference-project` arguments that the filesystem server processes directly.

## Scope
- **IN SCOPE**: Parameter definition, CLI parsing, argument generation
- **OUT OF SCOPE**: Path validation, name=path parsing, client handler modifications
