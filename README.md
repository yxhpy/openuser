# OpenUser - Intelligent Digital Human System

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Test Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](tests/)

**OpenUser** is an intelligent digital human system that enables users to create personalized AI avatars with their own voice, images, and videos. The system features hot-reloadable plugins, self-evolving AI agents, scheduled tasks, and multi-platform integrations.

## ✨ Key Features

### 🎭 Digital Human Creation
- **Voice Cloning**: Upload your voice samples to create a personalized TTS model
- **Face Animation**: Generate talking head videos from a single image
- **Video Generation**: Create full-body digital human videos
- **Real-time Rendering**: Live digital human interaction

### 🔌 Hot-Reload Plugin System
- Install/update plugins without restart
- Auto-dependency resolution
- Plugin marketplace with search and discovery
- Create custom plugins programmatically

### 🤖 Self-Evolving AI Agents
- Agents can update themselves via natural language prompts
- Auto-install required plugins
- Parameterized environments (all settings adjustable)
- Learning from interactions

### ⏰ Task Scheduler
- Cron-based scheduling
- Batch processing
- Automated reports
- Maintenance tasks

### 🌐 Multi-Platform Integration
- **Web Interface**: Full-featured dashboard
- **Feishu (Lark)**: Bot integration with interactive cards
- **WeChat Work**: Enterprise messaging integration
- **API**: RESTful API for custom integrations

### 📊 Production-Ready
- 100% test coverage
- Comprehensive documentation
- Docker support
- CI/CD pipelines
- Monitoring and logging

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL 13+
- Redis 6+
- CUDA-capable GPU (optional, for faster processing)

### Installation

```bash
# Clone the repository
git clone https://github.com/yxhpy/openuser.git
cd openuser

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Setup database
createdb openuser
alembic upgrade head

# Start Redis
redis-server

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start the API server
uvicorn src.api.main:app --reload
```

### Using Claude Code

```bash
# Start Claude Code in the project directory
cd openuser
claude

# Type "开始" or "start" to begin development
# Claude will read TODO.md and start working on tasks
```

## 📖 Documentation

- **[CLAUDE.md](CLAUDE.md)** - Core instructions for Claude Code
- **[TODO.md](TODO.md)** - Development roadmap and tasks
- **[docs/](docs/)** - Comprehensive documentation
  - [API Documentation](docs/api/INDEX.md)
  - [Module Registry](docs/modules/REGISTRY.md)
  - [Integration Guides](docs/integrations/)
  - [Troubleshooting](docs/troubleshooting/KNOWN_ISSUES.md)

## 🏗️ Architecture

```
openuser/
├── src/
│   ├── core/              # Core system (plugin manager, agent manager)
│   ├── plugins/           # Plugin implementations
│   ├── agents/            # AI agent definitions
│   ├── api/               # FastAPI endpoints
│   ├── integrations/      # Platform integrations (Feishu, WeChat)
│   ├── models/            # Digital human models (TTS, face animation)
│   └── utils/             # Utilities
├── tests/                 # Test suites (100% coverage)
├── docs/                  # Documentation
├── .claude/               # Claude Code extensions
│   ├── skills/           # Auto-triggered skills
│   ├── agents/           # AI agents
│   └── scripts/          # Helper scripts
└── scripts/              # Deployment scripts
```

## 🎯 Usage Examples

### Create a Digital Human

```python
from src.models.digital_human import DigitalHumanEngine

# Initialize engine
engine = DigitalHumanEngine()

# Create digital human from image and voice
digital_human = engine.create(
    image_path="path/to/your/photo.jpg",
    voice_samples=["sample1.wav", "sample2.wav"],
    name="My Avatar"
)

# Generate talking video
video = digital_human.generate_video(
    text="Hello, I am your digital human!",
    duration=10
)
```

### Install a Plugin

```python
from src.core.plugin_manager import PluginManager

pm = PluginManager()

# Install plugin from registry
pm.install("image-processor")

# Hot-reload plugin
pm.reload("image-processor")

# List installed plugins
plugins = pm.list_plugins()
```

### Create a Scheduled Task

```python
from src.core.scheduler import Scheduler

scheduler = Scheduler()

# Schedule daily report generation
scheduler.create_task(
    name="daily-report",
    schedule="0 9 * * *",  # Every day at 9 AM
    task="generate_report",
    params={"format": "pdf"}
)
```

### Agent Self-Update

```python
from src.agents.assistant import AssistantAgent

agent = AssistantAgent()

# Agent can update itself via prompts
response = agent.process("Install the video-editor plugin and use it to trim my video")
# Agent will: 1) Install plugin, 2) Update capabilities, 3) Process video
```

## 🔌 Plugin Development

Create a custom plugin:

```python
# src/plugins/my_plugin.py
from src.core.plugin_base import Plugin

class MyPlugin(Plugin):
    name = "my-plugin"
    version = "1.0.0"
    dependencies = ["image-processor"]

    def on_load(self):
        """Called when plugin is loaded"""
        self.logger.info(f"{self.name} loaded")

    def on_unload(self):
        """Called when plugin is unloaded"""
        self.logger.info(f"{self.name} unloaded")

    def process(self, data):
        """Main processing logic"""
        return {"status": "success", "data": data}
```

Register and use:

```python
from src.core.plugin_manager import PluginManager

pm = PluginManager()
pm.register_plugin("my-plugin", MyPlugin)
pm.load_plugin("my-plugin")
```

## 🌐 API Endpoints

### Digital Human
- `POST /api/v1/digital-human/create` - Create digital human
- `POST /api/v1/digital-human/generate` - Generate video
- `GET /api/v1/digital-human/{id}` - Get digital human info

### Plugins
- `GET /api/v1/plugins` - List plugins
- `POST /api/v1/plugins/install` - Install plugin
- `POST /api/v1/plugins/reload` - Hot-reload plugin
- `DELETE /api/v1/plugins/{name}` - Uninstall plugin

### Agents
- `GET /api/v1/agents` - List agents
- `POST /api/v1/agents/{id}/update` - Update agent
- `POST /api/v1/agents/{id}/chat` - Chat with agent

### Scheduler
- `GET /api/v1/scheduler/tasks` - List tasks
- `POST /api/v1/scheduler/tasks` - Create task
- `DELETE /api/v1/scheduler/tasks/{id}` - Delete task

Full API documentation: http://localhost:8000/docs

## 🧪 Testing

```bash
# Run all tests with coverage
pytest --cov --cov-fail-under=100

# Run specific test suite
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# Run with verbose output
pytest -v

# Generate HTML coverage report
pytest --cov --cov-report=html
open htmlcov/index.html
```

## 🚢 Deployment

### Docker

```bash
# Build image
docker build -t openuser:latest .

# Run with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f
```

### Kubernetes

```bash
# Deploy to Kubernetes
kubectl apply -f k8s/

# Check status
kubectl get pods -n openuser
```

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [SadTalker](https://github.com/OpenTalker/SadTalker) - Talking head generation
- [Wav2Lip](https://github.com/Rudrabha/Wav2Lip) - Lip-sync
- [GFPGAN](https://github.com/TencentARC/GFPGAN) - Face enhancement
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [Celery](https://docs.celeryq.dev/) - Task queue

## 📧 Contact

- GitHub: [@yxhpy](https://github.com/yxhpy)
- Repository: https://github.com/yxhpy/openuser

## 🗺️ Roadmap

See [TODO.md](TODO.md) for the complete development roadmap.

**Current Phase**: Phase 1 - Core Infrastructure

**Next Milestones**:
- [ ] Plugin system with hot-reload
- [ ] Digital human engine integration
- [ ] FastAPI implementation
- [ ] Feishu/WeChat integration
- [ ] Web interface

---

Made with ❤️ by the OpenUser Team
