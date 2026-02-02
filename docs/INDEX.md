# Documentation Index

Welcome to the OpenUser documentation!

## Quick Links

- **[Module Registry](modules/REGISTRY.md)** - All implemented features (check before implementing)
- **[API Documentation](api/INDEX.md)** - REST API endpoints and schemas
- **[Integration Guides](integrations/)** - Platform integration documentation
- **[Troubleshooting](troubleshooting/KNOWN_ISSUES.md)** - Known issues and solutions

## Getting Started

1. **Installation**: See [README.md](../README.md#installation)
2. **Quick Start**: See [README.md](../README.md#quick-start)
3. **Architecture**: See [CLAUDE.md](../CLAUDE.md#architecture)
4. **Development**: See [CLAUDE.md](../CLAUDE.md#development-workflow)

## Core Concepts

### Plugin System
OpenUser uses a hot-reloadable plugin system. Plugins can be installed, updated, and removed without restarting the system.

- **Plugin Development**: See [modules/REGISTRY.md](modules/REGISTRY.md)
- **Hot Reload**: See [../CLAUDE.md](../CLAUDE.md#plugin-development)

### Agent System
AI agents can update themselves via natural language prompts, install plugins, and adjust their own parameters.

- **Agent Development**: See [../CLAUDE.md](../CLAUDE.md#agent-development)
- **Self-Update**: See [modules/REGISTRY.md](modules/REGISTRY.md)

### Digital Human Engine
Create personalized digital humans from images and voice samples.

- **Voice Cloning**: TTS model integration
- **Face Animation**: Wav2Lip, SadTalker
- **Video Generation**: Full pipeline

### Integrations
Multi-platform support for Feishu, WeChat Work, and Web.

- **Feishu**: See [integrations/FEISHU.md](integrations/FEISHU.md)
- **WeChat Work**: See [integrations/WECHAT.md](integrations/WECHAT.md)
- **Web Interface**: See [integrations/WEB.md](integrations/WEB.md)

## API Documentation

Full REST API documentation with examples:

- **[Digital Human API](api/digital-human.md)** - Create and manage digital humans
- **[Plugin API](api/plugins.md)** - Plugin management
- **[Agent API](api/agents.md)** - Agent management
- **[Scheduler API](api/scheduler.md)** - Task scheduling

## Development Guide

### Before Starting
1. Read [TODO.md](../TODO.md) for current tasks
2. Check [modules/REGISTRY.md](modules/REGISTRY.md) to avoid duplication
3. Review [.claude-memory/context.json](../.claude-memory/context.json) for context

### Development Process
1. Plan: Update TODO.md
2. Implement: Write code
3. Test: 100% coverage required
4. Document: Update registry and docs
5. Commit: Conventional commits

### Testing
- **Unit Tests**: `pytest tests/unit/`
- **Integration Tests**: `pytest tests/integration/`
- **E2E Tests**: `pytest tests/e2e/`
- **Coverage**: `pytest --cov --cov-fail-under=100`

## Troubleshooting

Common issues and solutions:

- **[Known Issues](troubleshooting/KNOWN_ISSUES.md)** - Known bugs and workarounds
- **[FAQ](troubleshooting/FAQ.md)** - Frequently asked questions

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines.

## License

MIT License - See [LICENSE](../LICENSE) for details.
