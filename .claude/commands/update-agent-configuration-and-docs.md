---
name: update-agent-configuration-and-docs
description: Workflow command scaffold for update-agent-configuration-and-docs in wedding_management.
allowed_tools: ["Bash", "Read", "Write", "Grep", "Glob"]
---

# /update-agent-configuration-and-docs

Use this workflow when working on **update-agent-configuration-and-docs** in `wedding_management`.

## Goal

Updates agent configuration files and related documentation to reflect changes in agent architecture or available agents.

## Common Files

- `.antigravity/agents/*.md`
- `.opencode/agents/*.md`
- `.antigravity/settings.json`
- `.opencode/settings.json`
- `AGENTS.md`
- `opencode.json`

## Suggested Sequence

1. Understand the current state and failure mode before editing.
2. Make the smallest coherent change that satisfies the workflow goal.
3. Run the most relevant verification for touched files.
4. Summarize what changed and what still needs review.

## Typical Commit Signals

- Edit or add agent definition files in .antigravity/agents/, .opencode/agents/, or similar directories.
- Update settings.json or equivalent configuration files.
- Update AGENTS.md and other related documentation.
- Optionally update lock/config files (e.g., opencode.json, skills-lock.json).

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.