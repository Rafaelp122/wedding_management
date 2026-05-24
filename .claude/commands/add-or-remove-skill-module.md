---
name: add-or-remove-skill-module
description: Workflow command scaffold for add-or-remove-skill-module in wedding_management.
allowed_tools: ["Bash", "Read", "Write", "Grep", "Glob"]
---

# /add-or-remove-skill-module

Use this workflow when working on **add-or-remove-skill-module** in `wedding_management`.

## Goal

Adds or removes a skill module, which includes a SKILL.md and related reference, data, or script files under .agents/skills/ or similar directories.

## Common Files

- `.agents/skills/*/SKILL.md`
- `.agents/skills/*/references/*.md`
- `.agents/skills/*/data/*.csv`
- `.agents/skills/*/scripts/*`
- `.agents/skills/*/templates/*`

## Suggested Sequence

1. Understand the current state and failure mode before editing.
2. Make the smallest coherent change that satisfies the workflow goal.
3. Run the most relevant verification for touched files.
4. Summarize what changed and what still needs review.

## Typical Commit Signals

- Add or remove the main SKILL.md file under the appropriate .agents/skills/<skill-name>/ directory.
- Add or remove supporting files such as references, data, scripts, or templates within the same skill directory.
- Optionally update higher-level documentation or index files if needed.

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.