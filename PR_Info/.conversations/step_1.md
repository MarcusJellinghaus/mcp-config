# Implementation Task: Implement `normalize_server_name()` function in `src/mcp_config/clients/claude_code.py`

## Prompt Sent to LLM:
You are implementing tasks from a task tracker. Follow these steps in order:

**STEP 1: SELECT TASK**
- Read `pr_info/TASK_TRACKER.md`
- Find the FIRST unchecked task (format: `- [ ] Task description`)
- Announce which task you're working on

**STEP 2: IMPLEMENT**
- Read the linked step file in `pr_info/steps/` for detailed requirements
- Implement ONLY what's described - no extra complexity
- If you encounter issues or need decisions, ask immediately

**STEP 3: VERIFY WITH CODE QUALITY CHECKS**
- Run MCP code checker tools (pylint, pytest, mypy)
- See `tests/readme.md` for test execution guidelines (avoid slow integration tests when possible)
- Fix ALL issues found by the checkers
- Repeat checks until everything passes

**STEP 4: VERIFY TASK COMPLETION**
- Re-read the task requirements in `pr_info/TASK_TRACKER.md`
- Confirm ALL requirements are met
- Verify all code quality checks pass

**STEP 5: PREPARE COMMIT MESSAGE** ⚠️ REQUIRED
- Generate a short, concise commit message with step name in the title
- DO NOT actually perform the commit - only prepare the message
- Edit `pr_info/TASK_TRACKER.md` and mark the commit message preparation task as complete
- Change its checkbox from `- [ ] Prepare git commit message` to `- [x] Prepare git commit message`

**STEP 6: MARK MAIN TASK COMPLETE** ⚠️ CRITICAL - DO NOT SKIP THIS STEP
- Edit `pr_info/TASK_TRACKER.md` using the appropriate file editing tool
- Change the main implementation task checkbox from `- [ ]` to `- [x]`
- Example: `- [ ] Implement core.py` becomes `- [x] Implement core.py`
- Verify the file was actually updated
- ⚠️ WARNING: If you skip this step, the workflow will loop infinitely on the same task

**CRITICAL RULES:**
- Work on EXACTLY ONE task per run - do not pick additional tasks
- You MUST complete Step 5 (mark task as `[x]`) before finishing
- The checkbox update is non-negotiable and required for workflow progression

Current task from TASK_TRACKER.md: Implement `normalize_server_name()` function in `src/mcp_config/clients/claude_code.py`

Please implement this task step by step.

## LLM Response:
Excellent! ✅ All tasks for Step 1 are now marked as complete in the TASK_TRACKER.md.

## Summary

I have successfully completed the implementation of the `normalize_server_name()` function in `src/mcp_config/clients/claude_code.py`. Here's what was accomplished:

### Files Created:
1. **src/mcp_config/clients/claude_code.py** - Contains the `normalize_server_name()` function that:
   - Replaces spaces with underscores
   - Removes invalid characters (keeps only a-zA-Z0-9_-)
   - Truncates to 64 characters maximum
   - Raises ValueError for names with only invalid characters
   - Returns tuple (normalized_name, was_modified)

2. **tests/test_config/test_claude_code_handler.py** - Comprehensive test suite with 6 tests covering:
   - Valid names (pass-through unchanged)
   - Space conversion
   - Invalid character removal
   - Length truncation
   - Combined transformations
   - Empty result edge case

### Code Quality:
- ✅ All 6 pytest tests pass
- ✅ Pylint check passed with no issues
- ✅ Mypy type checking passed with no errors
- ✅ All acceptance criteria met

### Commit Message Prepared:
```
Implement server name normalization for Claude Code

Add normalize_server_name() function in src/mcp_config/clients/claude_code.py
that validates and normalizes server names to meet Claude Code requirements
(pattern: ^[a-zA-Z0-9_-]{1,64}$).
```

The task has been marked as complete in pr_info/TASK_TRACKER.md, and the workflow can now proceed to Step 2: ClaudeCodeHandler Core Implementation.

---
Generated on: 2025-11-02T21:37:50.038842