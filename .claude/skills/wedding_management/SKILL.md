```markdown
# wedding_management Development Patterns

> Auto-generated skill from repository analysis

## Overview
The `wedding_management` repository is a Python-based project focused on managing wedding-related tasks and data. While it does not use a specific web framework, it follows clear coding conventions and workflow patterns to ensure maintainability and collaboration. This skill outlines the repository's development patterns, including file organization, coding style, workflows for managing skills and agents, and testing practices.

## Coding Conventions

### File Naming
- Use **kebab-case** for file names.
  - Example: `guest-list-manager.py`, `event-scheduler.py`

### Import Style
- Use **relative imports** within modules.
  - Example:
    ```python
    from .utils import format_date
    ```

### Export Style
- Mixed export patterns are used. Functions and classes are typically defined at the module level and imported as needed.
  - Example:
    ```python
    # In guest-list-manager.py
    class GuestListManager:
        ...

    # In another file
    from .guest-list-manager import GuestListManager
    ```

### Commit Messages
- Follow **conventional commit** style.
- Common prefixes: `chore`, `feat`
- Example:
  ```
  feat: add RSVP tracking to guest-list-manager
  chore: update dependencies for event scheduler
  ```

## Workflows

### Add or Remove Skill Module
**Trigger:** When introducing a new skill or removing an obsolete skill from the project  
**Command:** `/manage-skill <add|remove> <skill-name>`

1. Add or remove the main `SKILL.md` file under `.agents/skills/<skill-name>/`.
2. Add or remove supporting files (references, data, scripts, templates) within the same skill directory.
3. Optionally update higher-level documentation or index files as needed.

**Example:**
```bash
/manage-skill add guest-management
```

**Files Involved:**
- `.agents/skills/*/SKILL.md`
- `.agents/skills/*/references/*.md`
- `.agents/skills/*/data/*.csv`
- `.agents/skills/*/scripts/*`
- `.agents/skills/*/templates/*`

---

### Update Agent Configuration and Docs
**Trigger:** When updating agent system, adding/removing agents, or syncing docs with config  
**Command:** `/update-agents`

1. Edit or add agent definition files in `.antigravity/agents/`, `.opencode/agents/`, or similar directories.
2. Update `settings.json` or equivalent configuration files.
3. Update `AGENTS.md` and other related documentation.
4. Optionally update lock/config files (e.g., `opencode.json`, `skills-lock.json`).

**Example:**
```bash
/update-agents
```

**Files Involved:**
- `.antigravity/agents/*.md`
- `.opencode/agents/*.md`
- `.antigravity/settings.json`
- `.opencode/settings.json`
- `AGENTS.md`
- `opencode.json`
- `skills-lock.json`

## Testing Patterns

- Test files follow the pattern: `*.test.*`
  - Example: `guest-list-manager.test.py`
- The testing framework is not explicitly specified; ensure tests are discoverable by your chosen test runner.
- Example test file structure:
  ```python
  # guest-list-manager.test.py
  from .guest-list-manager import GuestListManager

  def test_add_guest():
      manager = GuestListManager()
      manager.add_guest("Alice")
      assert "Alice" in manager.guests
  ```

## Commands

| Command                        | Purpose                                                      |
|--------------------------------|--------------------------------------------------------------|
| /manage-skill <add|remove> <skill-name> | Add or remove a skill module and its supporting files         |
| /update-agents                 | Update agent configuration files and related documentation    |
```
