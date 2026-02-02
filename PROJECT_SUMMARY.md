# Project Generation Summary

## Project Information

- **Name**: openuser
- **Description**: Intelligent Digital Human System
- **Language**: Python 3.10+
- **Framework**: FastAPI
- **Repository**: https://github.com/yxhpy/openuser.git
- **Created**: 2026-02-02

## Generated Structure

```
openuser/
├── .claude/                          # Claude Code extensions
│   ├── skills/                      # Auto-triggered skills
│   │   ├── start-dev/              # Start development skill
│   │   ├── auto-test/              # Auto-test skill
│   │   ├── auto-doc/               # Auto-documentation skill
│   │   ├── hot-reload/             # Hot-reload skill
│   │   ├── plugin-manager/         # Plugin management skill
│   │   └── scheduler/              # Scheduler skill
│   ├── hooks/                       # Event hooks
│   ├── agents/                      # AI agents
│   ├── scripts/                     # Helper scripts
│   └── config.json                  # Claude configuration
├── .claude-memory/                  # Project memory
│   ├── context.json                # Project context
│   ├── decisions/                  # Decision records
│   └── archives/                   # Historical data
├── docs/                            # Documentation
│   ├── INDEX.md                    # Documentation index
│   ├── modules/
│   │   └── REGISTRY.md            # Module registry
│   ├── api/                        # API documentation
│   ├── integrations/               # Integration guides
│   └── troubleshooting/            # Troubleshooting guides
├── src/                             # Source code
│   ├── __init__.py
│   ├── core/                       # Core system
│   │   ├── __init__.py
│   │   ├── plugin_manager.py      # Plugin hot-reload
│   │   ├── agent_manager.py       # Agent lifecycle
│   │   └── config_manager.py      # Dynamic config
│   ├── plugins/                    # Plugin implementations
│   ├── agents/                     # Agent definitions
│   ├── api/                        # FastAPI endpoints
│   ├── integrations/               # Platform integrations
│   │   ├── feishu/                # Feishu integration
│   │   └── wechat/                # WeChat Work integration
│   ├── models/                     # Digital human models
│   └── utils/                      # Utilities
├── tests/                           # Test suites
│   ├── __init__.py
│   ├── unit/                       # Unit tests
│   │   ├── __init__.py
│   │   └── test_plugin_manager.py
│   ├── integration/                # Integration tests
│   └── e2e/                        # End-to-end tests
├── scripts/                         # Deployment scripts
├── .github/
│   └── workflows/
│       └── test.yml                # CI/CD workflow
├── CLAUDE.md                        # Core instructions
├── TODO.md                          # Task list
├── README.md                        # Project documentation
├── pyproject.toml                   # Python configuration
├── .env.example                     # Environment template
└── .gitignore                       # Git ignore rules
```

## Core Features

### 1. Hot-Reload System
- **Plugin Hot-Reload**: Reload plugins without restart
- **Skill Hot-Reload**: Update skills on-the-fly
- **Config Hot-Reload**: Dynamic configuration updates
- **Agent Hot-Reload**: Update agents with new prompts

### 2. Self-Evolving Agents
- Agents can update themselves via prompts
- Auto-install required plugins
- Create custom plugins programmatically
- Parameterized environments

### 3. Digital Human Engine
- Voice cloning (TTS integration)
- Face animation (Wav2Lip, SadTalker)
- Video generation pipeline
- Real-time rendering

### 4. Multi-Platform Integration
- **Web Interface**: Full-featured dashboard
- **Feishu**: Bot integration
- **WeChat Work**: Enterprise messaging
- **API**: RESTful API

### 5. Task Scheduler
- Cron-based scheduling
- Batch processing
- Automated tasks
- Celery integration

## Next Steps

### 1. Initialize Git Repository
```bash
cd /Users/yxhpy/PycharmProjects/openuser
git init
git remote add origin https://github.com/yxhpy/openuser.git
```

### 2. Install Dependencies
```bash
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

### 3. Setup Environment
```bash
cp .env.example .env
# Edit .env with your settings
```

### 4. Start Development
```bash
claude
# Type "开始" or "start"
```

## Claude Code Skills

The following skills are automatically triggered:

1. **start-dev**: When you say "开始" or "start"
   - Reads TODO.md
   - Checks project memory
   - Reviews module registry
   - Begins first task

2. **auto-test**: After code changes
   - Runs tests automatically
   - Ensures 100% coverage
   - Reports results

3. **auto-doc**: After tests pass
   - Updates module registry
   - Generates API docs
   - Updates CHANGELOG

4. **hot-reload**: When plugins/skills change
   - Hot-reloads components
   - Validates changes
   - Rollback on failure

## Development Workflow

1. **Plan**: Update TODO.md with task breakdown
2. **Implement**: Write code following architecture
3. **Test**: Ensure 100% coverage
4. **Document**: Update registry and docs
5. **Commit**: Use conventional commits

## Testing

```bash
# Run all tests
pytest --cov --cov-fail-under=100

# Run specific test suite
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# Generate HTML coverage report
pytest --cov --cov-report=html
open htmlcov/index.html
```

## Documentation

- **CLAUDE.md**: Core instructions for Claude Code
- **TODO.md**: Development roadmap
- **docs/INDEX.md**: Documentation index
- **docs/modules/REGISTRY.md**: Module registry
- **docs/api/**: API documentation

## Project Memory

The `.claude-memory/` directory tracks:
- Project context
- Implementation decisions
- Reusable components
- Common patterns
- Lessons learned

## Key Principles

1. **Hot Reload Everything**: No restart required
2. **Agent Self-Evolution**: Agents update themselves
3. **Maximum Extensibility**: Plugin-based architecture
4. **Documentation-Driven**: Check registry before implementing
5. **Test-Driven**: 100% coverage required

## Support

- **GitHub**: https://github.com/yxhpy/openuser
- **Issues**: https://github.com/yxhpy/openuser/issues
- **Documentation**: docs/INDEX.md

---

Generated by AI Project Generator on 2026-02-02
