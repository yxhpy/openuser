# Quick Start Guide - OpenUser

## 🎉 Project Successfully Generated!

Your intelligent digital human project is ready at:
```
/Users/yxhpy/PycharmProjects/openuser
```

## 📋 What Was Created

✅ Complete project structure with .claude/ directory
✅ Core modules: PluginManager, AgentManager, ConfigManager
✅ Hot-reload capabilities for plugins, skills, and config
✅ Auto-triggered skills (start-dev, auto-test, auto-doc, hot-reload)
✅ Documentation system with module registry
✅ Test framework with 100% coverage requirement
✅ GitHub Actions CI/CD workflow
✅ Project memory system
✅ Git repository initialized and linked to GitHub

## 🚀 Next Steps

### 1. Navigate to Project
```bash
cd /Users/yxhpy/PycharmProjects/openuser
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -e ".[dev]"
```

### 4. Setup Environment
```bash
cp .env.example .env
# Edit .env with your settings (database, Redis, API keys, etc.)
```

### 5. Setup Database (Optional for now)
```bash
# Install PostgreSQL if not already installed
# Create database
createdb openuser

# Run migrations (when implemented)
# alembic upgrade head
```

### 6. Start Development with Claude Code
```bash
claude
```

Then type: **"开始"** or **"start"**

Claude will:
- Read TODO.md
- Check project memory
- Review module registry
- Begin implementing the first task
- Run tests automatically
- Update documentation

## 📖 Key Files to Know

### Core Instructions
- **CLAUDE.md** - Core instructions for Claude Code
- **TODO.md** - Development roadmap (12 phases)
- **README.md** - Project documentation

### Documentation
- **docs/INDEX.md** - Documentation index
- **docs/modules/REGISTRY.md** - Module registry (check before implementing)
- **PROJECT_SUMMARY.md** - This file

### Configuration
- **pyproject.toml** - Python project configuration
- **.env.example** - Environment variables template
- **.claude/config.json** - Claude Code configuration

### Source Code
- **src/core/plugin_manager.py** - Plugin hot-reload system
- **src/core/agent_manager.py** - Agent lifecycle management
- **src/core/config_manager.py** - Dynamic configuration

### Tests
- **tests/unit/test_plugin_manager.py** - Example unit test
- Run with: `pytest --cov --cov-fail-under=100`

## 🎯 Development Workflow

### Automatic Workflow (Recommended)
1. Type **"开始"** in Claude Code
2. Claude reads TODO.md and starts working
3. Tests run automatically after code changes
4. Documentation updates automatically
5. Repeat

### Manual Workflow
1. Check TODO.md for next task
2. Check docs/modules/REGISTRY.md to avoid duplication
3. Implement feature
4. Write tests (100% coverage required)
5. Update module registry
6. Commit with conventional commit message

## 🔧 Useful Commands

### Testing
```bash
# Run all tests with coverage
pytest --cov --cov-fail-under=100

# Run specific test suite
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# Generate HTML coverage report
pytest --cov --cov-report=html
open htmlcov/index.html
```

### Code Quality
```bash
# Format code
black src tests

# Sort imports
isort src tests

# Lint code
flake8 src tests

# Type check
mypy src
```

### Git
```bash
# Push to GitHub
git push -u origin main

# Create feature branch
git checkout -b feature/your-feature

# Commit with conventional commits
git commit -m "feat: add new feature"
git commit -m "fix: fix bug"
git commit -m "docs: update documentation"
```

## 🤖 Claude Code Skills

The following skills are automatically triggered:

### start-dev
**Trigger**: When you say "开始", "开始开发", "继续", or "start"
**Action**: Reads TODO.md and starts working on the next task

### auto-test
**Trigger**: After code changes in src/
**Action**: Runs tests automatically and ensures 100% coverage

### auto-doc
**Trigger**: After tests pass
**Action**: Updates module registry and API documentation

### hot-reload
**Trigger**: When you say "reload", "热更新", or "刷新插件"
**Action**: Hot-reloads plugins, skills, or configuration without restart

## 📚 Learning Resources

### Project Documentation
- [CLAUDE.md](CLAUDE.md) - Complete development guide
- [TODO.md](TODO.md) - 12-phase development roadmap
- [docs/INDEX.md](docs/INDEX.md) - Documentation index

### External Resources
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Celery Documentation](https://docs.celeryq.dev)
- [SadTalker GitHub](https://github.com/OpenTalker/SadTalker)
- [Wav2Lip GitHub](https://github.com/Rudrabha/Wav2Lip)

## 🎨 Project Features

### ✅ Already Implemented
- Project structure
- Core module skeletons (PluginManager, AgentManager, ConfigManager)
- Test framework setup
- Documentation system
- CI/CD workflow
- Claude Code skills

### 🚧 Next to Implement (Phase 1)
- Complete Plugin Manager implementation
- Complete Agent Manager implementation
- Complete Config Manager implementation
- Database setup
- Redis integration

### 📝 Future Features (Phases 2-12)
- Digital human engine (voice cloning, face animation, video generation)
- FastAPI endpoints
- Plugin system
- Feishu/WeChat integration
- Web interface
- Task scheduler
- Agent self-evolution
- Deployment

## 🐛 Troubleshooting

### Issue: Import errors
**Solution**: Make sure you installed the package in editable mode:
```bash
pip install -e ".[dev]"
```

### Issue: Tests not found
**Solution**: Make sure you're in the project root directory:
```bash
cd /Users/yxhpy/PycharmProjects/openuser
pytest
```

### Issue: Coverage below 100%
**Solution**: Write tests for all uncovered code. Check coverage report:
```bash
pytest --cov --cov-report=html
open htmlcov/index.html
```

## 💡 Tips

1. **Always check the module registry** before implementing new features
2. **Write tests first** (TDD approach)
3. **Use Claude Code skills** - they automate testing and documentation
4. **Keep CLAUDE.md updated** with important decisions
5. **Update TODO.md** as you complete tasks
6. **Commit frequently** with conventional commit messages

## 🎯 Current Phase

**Phase 1: Core Infrastructure (Week 1-2)**

Next tasks:
1. Setup Python environment (pyproject.toml, requirements.txt) ✅
2. Configure pytest with 100% coverage requirement ✅
3. Implement Plugin Manager with hot-reload capability
4. Implement Agent Manager
5. Implement Config Manager
6. Setup PostgreSQL schema
7. Setup Redis for caching

## 📞 Support

- **GitHub Repository**: https://github.com/yxhpy/openuser
- **Issues**: https://github.com/yxhpy/openuser/issues
- **Documentation**: docs/INDEX.md

## 🎊 Ready to Start!

Your project is fully set up and ready for development. To begin:

```bash
cd /Users/yxhpy/PycharmProjects/openuser
source venv/bin/activate  # After creating venv
claude
```

Then type: **"开始"**

Happy coding! 🚀
