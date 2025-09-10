# Task Status Tracker

## Instructions for LLM

This is a simple task tracker for an LLM to track task status and maintain it. Keep it simple - no extensions or complications needed.

**Context:** User wants to create task status tracking for an LLM to track status of tasks, maintain it, and check out new tasks by itself. User chose a simple markdown file approach over MCP servers with GitHub issues or databases. Tasks are based on files in PR_Info/ folder for IntelliJ MCP client support.

**How to update tasks:**
1. Change [ ] to [x] when task is completed
2. Change [x] to [ ] if task needs to be reopened
3. Add brief notes in the linked detail files if needed
4. No dates, special characters, priority levels, or other complications
5. Just use GitHub issues style checkboxes

**Task format:**
- [x] = Done
- [ ] = Not done
- Each task links to a detail file in PR_Info/ folder

---

## Tasks

### [ ] IntelliJ Handler Path Detection (TDD)
**Background:** [summary.md](./summary.md) | **Details:** [step_1.md](./step_1.md)

### [ ] IntelliJ Handler Implementation (TDD)
**Background:** [summary.md](./summary.md) | **Details:** [step_2.md](./step_2.md)

### [ ] Complete IntelliJ Handler CRUD Operations
**Background:** [summary.md](./summary.md) | **Details:** [step_3.md](./step_3.md)

### [ ] CLI Integration for IntelliJ Support
**Background:** [summary.md](./summary.md) | **Details:** [step_4.md](./step_4.md)
