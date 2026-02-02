---
name: start-dev
description: 当用户说"开始"、"开始开发"、"继续"、"start"时自动触发。读取 TODO.md 并开始执行任务。
---

# Start Development Skill

This skill is automatically triggered when the user says "开始", "开始开发", "继续", or "start".

## Behavior

When triggered, this skill will:

1. **Read TODO.md** - Load the current task list
2. **Check Project Memory** - Review `.claude-memory/context.json` for historical context
3. **Review Module Registry** - Check `docs/modules/REGISTRY.md` to avoid duplication
4. **Check Known Issues** - Review `docs/troubleshooting/KNOWN_ISSUES.md`
5. **Identify Next Task** - Find the first uncompleted task in TODO.md
6. **Start Implementation** - Begin working on the task
7. **Run Tests** - Ensure 100% coverage after changes
8. **Update Documentation** - Update module registry and API docs
9. **Record Progress** - Update project memory

## Workflow

```
User says "开始"
  ↓
Read TODO.md
  ↓
Check .claude-memory/context.json
  ↓
Review docs/modules/REGISTRY.md
  ↓
Find next uncompleted task
  ↓
Implement task
  ↓
Run tests (pytest --cov --cov-fail-under=100)
  ↓
Update documentation
  ↓
Update project memory
  ↓
Ask user: "Task completed. Continue to next task?"
```

## Example

**User**: "开始"

**Claude**:
```
Reading TODO.md...
Current phase: Phase 1 - Core Infrastructure
Next task: Setup Python environment (pyproject.toml, requirements.txt)

Checking project memory...
No previous context found. Starting fresh.

Checking module registry...
No modules implemented yet.

Starting implementation of: Setup Python environment
...
```

## Implementation

This skill should:
- Be proactive and autonomous
- Follow the development workflow in CLAUDE.md
- Ensure 100% test coverage
- Update all relevant documentation
- Record decisions in project memory
- Ask for clarification when needed

## Related Skills

- `auto-test` - Runs tests automatically after code changes
- `auto-doc` - Updates documentation automatically
- `hot-reload` - Hot-reloads plugins and skills
