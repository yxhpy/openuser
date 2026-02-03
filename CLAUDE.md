# CLAUDE.md

This file provides guidance to Claude Code when working with the OpenUser project.

## Project Overview

**OpenUser** is an intelligent digital human system that enables users to create personalized AI avatars with their own voice, images, and videos. The system features hot-reloadable plugins, skills, scheduled tasks, and multi-platform integrations.

**Core Components**:
- **Digital Human Engine** - Custom solution integrating Wav2Lip, GFPGAN, SadTalker
- **Plugin System** - Hot-reloadable plugins with auto-installation
- **Agent System** - Self-updating AI agents with parameterized environments
- **Integration Layer** - Feishu, WeChat Work, Web interface
- **Scheduler** - Cron-based task automation

**Tech Stack**: Python 3.10+, FastAPI, SQLAlchemy, Redis, Celery

## Core Principles

### 1. Hot Reload Everything
- Plugins can be installed/updated without restart
- Skills can be modified on-the-fly
- System prompts are dynamically reloadable
- Configuration changes apply immediately

### 2. Agent Self-Evolution
- Agents can update themselves via prompts
- Auto-install required plugins
- Create custom plugins programmatically
- All environments are parameterized

### 3. Maximum Extensibility
- Plugin-based architecture
- Event-driven design
- API-first approach
- Modular components

### 4. Documentation-Driven Development
- All features documented in `docs/modules/REGISTRY.md`
- API docs auto-generated from code
- Known issues tracked in `docs/troubleshooting/`
- Check registry before implementing new features

### 5. Test-Driven Development
- 100% test coverage required
- Tests run automatically after code changes
- Integration tests for all plugins
- E2E tests for critical workflows

## Architecture

### Directory Structure
```
openuser/
├── .claude/                    # Claude Code extensions
│   ├── skills/                # Project-specific skills
│   ├── hooks/                 # Event hooks
│   ├── agents/                # AI agents
│   └── scripts/               # Helper scripts
├── src/
│   ├── core/                  # Core system
│   │   ├── plugin_manager.py # Plugin hot-reload
│   │   ├── agent_manager.py  # Agent lifecycle
│   │   └── config_manager.py # Dynamic config
│   ├── plugins/               # Plugin implementations
│   ├── agents/                # Agent definitions
│   ├── api/                   # FastAPI endpoints
│   ├── integrations/          # Platform integrations
│   │   ├── feishu/
│   │   └── wechat/
│   ├── models/                # Digital human models
│   └── utils/                 # Utilities
├── tests/                     # Test suites
├── docs/                      # Documentation
└── scripts/                   # Deployment scripts
```

### Key Modules

**Plugin Manager** (`src/core/plugin_manager.py`):
- Hot-reload plugins without restart
- Dependency resolution
- Version management
- Auto-installation from registry

**Agent Manager** (`src/core/agent_manager.py`):
- Agent lifecycle management
- Self-update via prompts
- Environment parameterization
- Plugin creation capabilities

**Digital Human Engine** (`src/models/`):
- Voice cloning (integrate TTS models)
- Face animation (Wav2Lip, SadTalker)
- Video generation
- Real-time rendering

**Integration Layer** (`src/integrations/`):
- Feishu bot integration
- WeChat Work integration
- Webhook handlers
- Event dispatching

## Development Workflow

### Before Starting Development
1. Read `TODO.md` for current tasks
2. Check `docs/modules/REGISTRY.md` to avoid duplication
3. Review `.claude-memory/context.json` for project context
4. Check `docs/troubleshooting/KNOWN_ISSUES.md` for known problems

### Development Process
1. **Plan**: Update TODO.md with task breakdown
2. **Implement**: Write code following architecture
3. **Test**: Ensure 100% coverage (`pytest --cov --cov-fail-under=100`)
4. **Document**: Update module registry and API docs
5. **Commit**: Use conventional commits

### After Code Changes
- Auto-test skill runs tests automatically
- Auto-doc skill updates documentation
- Module registry is updated
- Project memory is recorded

## Quick Start

### Installation
```bash
cd /Users/yxhpy/PycharmProjects/openuser
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
pre-commit install  # Install pre-commit hooks
```

### Pre-commit Hooks
The project uses pre-commit hooks to ensure code quality:
- **Code formatting**: Black, isort
- **Linting**: flake8
- **Type checking**: mypy
- **Type generation**: Automatically generates TypeScript types from Pydantic schemas

When you modify `src/api/schemas.py`, the pre-commit hook will automatically regenerate `frontend/src/types/generated.ts`. If types are regenerated, you'll need to stage the generated file and commit again.

### Start Development
```bash
claude
# Then type: "开始" or "start"
```

The `start-dev` skill will:
1. Read TODO.md
2. Check project memory
3. Review module registry
4. Begin first task
5. Run tests after changes
6. Update documentation

### Run Tests
```bash
# Run all tests with coverage
pytest --cov --cov-fail-under=100

# Run performance tests (without coverage)
bash scripts/run_performance_tests.sh

# Run load tests
# 1. Start API server: uvicorn src.api.main:app --reload
# 2. Run locust: locust -f tests/performance/locustfile.py --host=http://localhost:8000
# 3. Open http://localhost:8089 in browser
```

### Start API Server
```bash
uvicorn src.api.main:app --reload
```

## Documentation Navigation

- **Module Registry**: `docs/modules/REGISTRY.md` - All implemented features
- **API Documentation**: `docs/api/INDEX.md` - API endpoints and schemas
- **Integration Guides**: `docs/integrations/` - Platform integration docs
- **Troubleshooting**: `docs/troubleshooting/KNOWN_ISSUES.md` - Known issues
- **Project Memory**: `.claude-memory/` - Historical context and decisions

## Plugin Development

### Creating a Plugin
```python
# src/plugins/my_plugin.py
from src.core.plugin_base import Plugin

class MyPlugin(Plugin):
    name = "my-plugin"
    version = "1.0.0"

    def on_load(self):
        """Called when plugin is loaded"""
        pass

    def on_unload(self):
        """Called when plugin is unloaded"""
        pass
```

### Hot Reload
```python
from src.core.plugin_manager import PluginManager

pm = PluginManager()
pm.reload_plugin("my-plugin")  # Hot reload without restart
```

## Agent Development

### Creating an Agent
```python
# src/agents/my_agent.py
from src.core.agent_base import Agent

class MyAgent(Agent):
    def __init__(self):
        super().__init__(
            name="my-agent",
            system_prompt="You are a helpful assistant",
            capabilities=["plugin-install", "self-update"]
        )

    async def process(self, input_data):
        """Process user input"""
        pass
```

### Agent Self-Update
Agents can update themselves via prompts:
```
User: "Install the image-processing plugin"
Agent: [Auto-installs plugin and updates capabilities]
```

## Integration Development

### Feishu Integration
See `docs/integrations/FEISHU.md` for webhook setup and event handling.

### WeChat Work Integration
See `docs/integrations/WECHAT.md` for API configuration and message handling.

## Common Tasks

### Add New Feature
1. Check `docs/modules/REGISTRY.md` - feature might exist
2. Update TODO.md with task breakdown
3. Implement in appropriate module
4. Write tests (100% coverage)
5. Update registry and docs
6. Commit with conventional commit message

### Fix Bug
1. Check `docs/troubleshooting/KNOWN_ISSUES.md`
2. Write failing test first
3. Fix the bug
4. Ensure all tests pass
5. Update known issues if needed

### Add Integration
1. Create integration module in `src/integrations/`
2. Implement webhook handlers
3. Add integration tests
4. Document in `docs/integrations/`
5. Update module registry

## Environment Variables

```bash
# .env
OPENUSER_ENV=development
OPENUSER_DEBUG=true
OPENUSER_API_HOST=0.0.0.0
OPENUSER_API_PORT=8000

# Database
DATABASE_URL=postgresql://user:pass@localhost/openuser

# Redis
REDIS_URL=redis://localhost:6379/0

# Integrations
FEISHU_APP_ID=your_app_id
FEISHU_APP_SECRET=your_app_secret
WECHAT_CORP_ID=your_corp_id
WECHAT_CORP_SECRET=your_corp_secret

# Digital Human Models
MODEL_PATH=/path/to/models
DEVICE=cuda  # or cpu
```

## Reference Resources

- **Project Docs**: `docs/INDEX.md`
- **Module Registry**: `docs/modules/REGISTRY.md`
- **API Docs**: `docs/api/INDEX.md`
- **GitHub Repo**: https://github.com/yxhpy/openuser.git
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Celery Docs**: https://docs.celeryq.dev
