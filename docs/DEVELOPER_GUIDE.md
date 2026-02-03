# OpenUser Developer Guide

Welcome to the OpenUser Developer Guide! This guide will help you understand the architecture, contribute to the project, and extend OpenUser with custom plugins and integrations.

## Table of Contents

1. [Development Setup](#development-setup)
2. [Architecture Overview](#architecture-overview)
3. [Core Systems](#core-systems)
4. [Plugin Development](#plugin-development)
5. [Agent Development](#agent-development)
6. [API Development](#api-development)
7. [Testing](#testing)
8. [Contributing](#contributing)
9. [Best Practices](#best-practices)

## Development Setup

### Prerequisites

- Python 3.10 or higher
- PostgreSQL 12+
- Redis 6+
- Git
- (Optional) CUDA-capable GPU

### Clone and Setup

```bash
# Clone repository
git clone https://github.com/yxhpy/openuser.git
cd openuser

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Pre-commit Hooks

The project uses pre-commit hooks to ensure code quality:

- **black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **Type generation**: Auto-generates TypeScript types from Pydantic schemas

When you modify `src/api/schemas.py`, TypeScript types are automatically regenerated in `frontend/src/types/generated.ts`.

### Environment Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit with your settings
vim .env
```

Key environment variables:

```bash
# Application
OPENUSER_ENV=development
OPENUSER_DEBUG=true
OPENUSER_API_HOST=0.0.0.0
OPENUSER_API_PORT=8000

# Database
DATABASE_URL=postgresql://user:pass@localhost/openuser

# Redis
REDIS_URL=redis://localhost:6379/0

# Models
MODEL_PATH=./models
DEVICE=cuda  # or cpu

# Integrations
FEISHU_APP_ID=your_app_id
FEISHU_APP_SECRET=your_app_secret
```

### Running Tests

```bash
# Run all tests with coverage
pytest --cov --cov-fail-under=100

# Run specific test file
pytest tests/test_plugin_manager.py

# Run with verbose output
pytest -v

# Run performance tests
bash scripts/run_performance_tests.sh
```

### Starting Development Server

```bash
# Start API server with hot reload
uvicorn src.api.main:app --reload

# Start with custom host/port
uvicorn src.api.main:app --host 0.0.0.0 --port 8080 --reload

# Start Celery worker (for background tasks)
celery -A src.core.celery_app worker --loglevel=info
```

## Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (React)                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │Dashboard │  │ Digital  │  │ Plugins  │  │Scheduler│ │
│  │          │  │  Human   │  │          │  │         │ │
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘ │
└─────────────────────────────────────────────────────────┘
                          │
                          │ HTTP/WebSocket
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │   Auth   │  │ Digital  │  │ Plugins  │  │Scheduler│ │
│  │          │  │  Human   │  │          │  │         │ │
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘ │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                     Core Systems                         │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐ │
│  │   Plugin     │  │    Agent     │  │   Scheduler   │ │
│  │   Manager    │  │   Manager    │  │               │ │
│  └──────────────┘  └──────────────┘  └───────────────┘ │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐ │
│  │   Config     │  │    Event     │  │     Cache     │ │
│  │   Manager    │  │   Dispatcher │  │    Manager    │ │
│  └──────────────┘  └──────────────┘  └───────────────┘ │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  Digital Human Engine                    │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐ │
│  │   Wav2Lip    │  │  SadTalker   │  │    GFPGAN     │ │
│  │  (Lip Sync)  │  │(Talking Head)│  │(Enhancement)  │ │
│  └──────────────┘  └──────────────┘  └───────────────┘ │
│  ┌──────────────┐  ┌──────────────┐                    │
│  │     TTS      │  │Voice Cloning │                    │
│  │  (Synthesis) │  │              │                    │
│  └──────────────┘  └──────────────┘                    │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  Storage & Services                      │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐ │
│  │  PostgreSQL  │  │    Redis     │  │  File Storage │ │
│  │  (Database)  │  │   (Cache)    │  │   (Videos)    │ │
│  └──────────────┘  └──────────────┘  └───────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Directory Structure

```
openuser/
├── src/
│   ├── api/                    # FastAPI endpoints
│   │   ├── main.py            # Application entry point
│   │   ├── routes/            # API route handlers
│   │   ├── schemas.py         # Pydantic schemas
│   │   └── dependencies.py    # Dependency injection
│   ├── core/                  # Core systems
│   │   ├── plugin_manager.py # Plugin hot-reload
│   │   ├── agent_manager.py  # Agent lifecycle
│   │   ├── config_manager.py # Dynamic config
│   │   ├── event_dispatcher.py # Event system
│   │   └── cache_manager.py  # Caching
│   ├── plugins/               # Plugin implementations
│   │   ├── base.py           # Plugin base class
│   │   └── builtin/          # Built-in plugins
│   ├── agents/                # Agent definitions
│   │   ├── base.py           # Agent base class
│   │   └── builtin/          # Built-in agents
│   ├── models/                # Digital human models
│   │   ├── wav2lip/          # Lip sync
│   │   ├── sadtalker/        # Talking head
│   │   ├── gfpgan/           # Face enhancement
│   │   └── tts/              # Text-to-speech
│   ├── integrations/          # Platform integrations
│   │   ├── feishu/           # Feishu integration
│   │   └── wechat/           # WeChat Work
│   ├── db/                    # Database models
│   │   ├── models.py         # SQLAlchemy models
│   │   └── session.py        # Database session
│   └── utils/                 # Utilities
├── tests/                     # Test suites
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   └── e2e/                  # End-to-end tests
├── frontend/                  # React frontend
├── docs/                      # Documentation
├── scripts/                   # Deployment scripts
└── .claude/                   # Claude Code extensions
```

## Core Systems

### Plugin Manager

The Plugin Manager enables hot-reloading of plugins without restarting the server.

**Key Features**:
- Dynamic plugin loading/unloading
- Dependency resolution
- Version management
- Auto-installation from registry

**Example**:

```python
from src.core.plugin_manager import PluginManager

# Initialize plugin manager
pm = PluginManager()

# Load a plugin
pm.load_plugin("image-processor")

# Reload a plugin (hot-reload)
pm.reload_plugin("image-processor")

# Unload a plugin
pm.unload_plugin("image-processor")

# List all plugins
plugins = pm.list_plugins()
```

**Plugin Lifecycle**:

```
┌─────────┐
│ Install │
└────┬────┘
     │
     ▼
┌─────────┐
│  Load   │ ◄──────┐
└────┬────┘        │
     │             │
     ▼             │
┌─────────┐        │
│ Active  │        │
└────┬────┘        │
     │             │
     ▼             │
┌─────────┐        │
│ Reload  │────────┘
└────┬────┘
     │
     ▼
┌─────────┐
│ Unload  │
└─────────┘
```

### Agent Manager

The Agent Manager handles AI agent lifecycle and self-evolution.

**Key Features**:
- Agent creation and management
- Self-update via prompts
- Environment parameterization
- Plugin creation capabilities

**Example**:

```python
from src.core.agent_manager import AgentManager

# Initialize agent manager
am = AgentManager()

# Create an agent
agent = am.create_agent(
    name="my-agent",
    system_prompt="You are a helpful assistant",
    capabilities=["plugin-install", "self-update"]
)

# Process input
response = await agent.process("Install the image-processing plugin")

# Agent can self-update
await agent.update_prompt("You are now a specialized image processing assistant")
```

### Event Dispatcher

The Event Dispatcher enables event-driven architecture.

**Key Features**:
- Publish-subscribe pattern
- Async event handling
- Event filtering
- Priority-based dispatch

**Example**:

```python
from src.core.event_dispatcher import EventDispatcher

# Initialize dispatcher
dispatcher = EventDispatcher()

# Subscribe to events
@dispatcher.on("plugin.loaded")
async def on_plugin_loaded(event):
    print(f"Plugin {event.data['name']} loaded")

# Publish events
await dispatcher.publish("plugin.loaded", {"name": "image-processor"})
```

### Config Manager

The Config Manager provides dynamic configuration management.

**Key Features**:
- Hot-reload configuration
- Environment-based config
- Validation
- Type safety

**Example**:

```python
from src.core.config_manager import ConfigManager

# Initialize config manager
cm = ConfigManager()

# Get configuration
api_host = cm.get("api.host", default="0.0.0.0")

# Update configuration (hot-reload)
cm.set("api.port", 8080)

# Watch for changes
@cm.watch("api.port")
def on_port_change(old_value, new_value):
    print(f"Port changed from {old_value} to {new_value}")
```

## Plugin Development

### Creating a Plugin

1. **Create plugin file**:

```python
# src/plugins/my_plugin.py
from src.core.plugin_base import Plugin
from typing import Dict, Any

class MyPlugin(Plugin):
    """My custom plugin"""

    name = "my-plugin"
    version = "1.0.0"
    description = "A custom plugin"
    author = "Your Name"
    dependencies = []  # List of required plugins

    def __init__(self):
        super().__init__()
        self.config = {}

    def on_load(self):
        """Called when plugin is loaded"""
        print(f"Loading {self.name} v{self.version}")
        # Initialize resources
        self.config = self.load_config()

    def on_unload(self):
        """Called when plugin is unloaded"""
        print(f"Unloading {self.name}")
        # Cleanup resources
        self.cleanup()

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Main processing logic"""
        # Your plugin logic here
        result = self.do_something(data)
        return result

    def do_something(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Custom method"""
        # Implementation
        return {"status": "success", "data": data}
```

2. **Register plugin**:

```python
# src/plugins/__init__.py
from .my_plugin import MyPlugin

__all__ = ["MyPlugin"]
```

3. **Test plugin**:

```python
# tests/test_my_plugin.py
import pytest
from src.plugins.my_plugin import MyPlugin

def test_plugin_load():
    plugin = MyPlugin()
    plugin.on_load()
    assert plugin.name == "my-plugin"

def test_plugin_process():
    plugin = MyPlugin()
    result = plugin.process({"input": "test"})
    assert result["status"] == "success"
```

### Plugin Best Practices

1. **Keep plugins focused**: One plugin, one responsibility
2. **Handle errors gracefully**: Don't crash the system
3. **Clean up resources**: Implement proper cleanup in `on_unload()`
4. **Document your plugin**: Add docstrings and README
5. **Version your plugin**: Use semantic versioning
6. **Test thoroughly**: Write unit and integration tests

## Agent Development

### Creating an Agent

```python
# src/agents/my_agent.py
from src.core.agent_base import Agent
from typing import Dict, Any

class MyAgent(Agent):
    """My custom agent"""

    def __init__(self):
        super().__init__(
            name="my-agent",
            system_prompt="You are a specialized assistant",
            capabilities=[
                "plugin-install",
                "self-update",
                "code-generation"
            ]
        )

    async def process(self, input_data: str) -> str:
        """Process user input"""
        # Your agent logic here
        response = await self.generate_response(input_data)
        return response

    async def generate_response(self, input_data: str) -> str:
        """Generate response using LLM"""
        # Call LLM API
        # Process response
        # Return result
        return "Response"

    async def install_plugin(self, plugin_name: str):
        """Install a plugin"""
        from src.core.plugin_manager import PluginManager
        pm = PluginManager()
        await pm.install_plugin(plugin_name)

    async def update_self(self, new_prompt: str):
        """Update agent's system prompt"""
        self.system_prompt = new_prompt
        await self.reload()
```

### Agent Capabilities

Agents can have various capabilities:

- **plugin-install**: Install plugins dynamically
- **self-update**: Update their own prompts
- **code-generation**: Generate code
- **plugin-creation**: Create new plugins
- **task-scheduling**: Schedule tasks

## API Development

### Adding a New Endpoint

1. **Define schema**:

```python
# src/api/schemas.py
from pydantic import BaseModel

class MyRequest(BaseModel):
    input: str
    options: dict = {}

class MyResponse(BaseModel):
    result: str
    status: str
```

2. **Create route**:

```python
# src/api/routes/my_route.py
from fastapi import APIRouter, Depends
from src.api.schemas import MyRequest, MyResponse
from src.api.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/my-feature", tags=["my-feature"])

@router.post("/process", response_model=MyResponse)
async def process_data(
    request: MyRequest,
    current_user = Depends(get_current_user)
):
    """Process data"""
    # Your logic here
    result = do_processing(request.input, request.options)
    return MyResponse(result=result, status="success")
```

3. **Register route**:

```python
# src/api/main.py
from src.api.routes import my_route

app.include_router(my_route.router)
```

4. **Write tests**:

```python
# tests/test_my_route.py
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_process_endpoint():
    response = client.post(
        "/api/v1/my-feature/process",
        json={"input": "test", "options": {}},
        headers={"Authorization": "Bearer token"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"
```

## Testing

### Test Structure

```
tests/
├── unit/                  # Unit tests
│   ├── test_plugin_manager.py
│   ├── test_agent_manager.py
│   └── test_config_manager.py
├── integration/           # Integration tests
│   ├── test_api_integration.py
│   ├── test_plugin_integration.py
│   └── test_agent_integration.py
├── e2e/                   # End-to-end tests
│   ├── test_video_generation.py
│   └── test_scheduler.py
├── performance/           # Performance tests
│   ├── test_load.py
│   └── locustfile.py
└── conftest.py           # Pytest configuration
```

### Writing Tests

```python
# tests/unit/test_my_feature.py
import pytest
from src.my_module import MyClass

@pytest.fixture
def my_instance():
    """Fixture for MyClass instance"""
    return MyClass()

def test_basic_functionality(my_instance):
    """Test basic functionality"""
    result = my_instance.do_something()
    assert result == expected_value

@pytest.mark.asyncio
async def test_async_functionality(my_instance):
    """Test async functionality"""
    result = await my_instance.do_async_something()
    assert result is not None

@pytest.mark.parametrize("input,expected", [
    ("test1", "result1"),
    ("test2", "result2"),
])
def test_multiple_inputs(my_instance, input, expected):
    """Test with multiple inputs"""
    result = my_instance.process(input)
    assert result == expected
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov --cov-fail-under=100

# Run specific test file
pytest tests/unit/test_my_feature.py

# Run specific test
pytest tests/unit/test_my_feature.py::test_basic_functionality

# Run with markers
pytest -m "not slow"

# Run in parallel
pytest -n auto
```

## Contributing

### Contribution Workflow

1. **Fork the repository**
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/my-feature
   ```

3. **Make your changes**:
   - Write code
   - Add tests
   - Update documentation

4. **Run tests**:
   ```bash
   pytest --cov --cov-fail-under=100
   ```

5. **Commit changes**:
   ```bash
   git add .
   git commit -m "feat: Add my feature"
   ```

6. **Push to your fork**:
   ```bash
   git push origin feature/my-feature
   ```

7. **Create pull request**

### Commit Message Convention

Follow conventional commits:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test changes
- `refactor:` Code refactoring
- `perf:` Performance improvements
- `chore:` Build/tooling changes

Examples:
```
feat: Add voice cloning support
fix: Resolve memory leak in video generation
docs: Update API documentation
test: Add integration tests for plugins
```

### Code Review Process

1. **Automated checks**: CI/CD runs tests and linters
2. **Peer review**: At least one approval required
3. **Documentation**: Ensure docs are updated
4. **Testing**: 100% coverage required

## Best Practices

### Code Style

- Follow PEP 8
- Use type hints
- Write docstrings
- Keep functions small and focused
- Use meaningful variable names

### Error Handling

```python
# Good
try:
    result = risky_operation()
except SpecificException as e:
    logger.error(f"Operation failed: {e}")
    raise CustomException("Friendly error message") from e

# Bad
try:
    result = risky_operation()
except:
    pass
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

# Use appropriate log levels
logger.debug("Detailed information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred")
logger.critical("Critical error")
```

### Performance

- Use async/await for I/O operations
- Cache expensive computations
- Use database indexes
- Profile before optimizing
- Monitor memory usage

### Security

- Validate all inputs
- Use parameterized queries
- Don't log sensitive data
- Keep dependencies updated
- Follow OWASP guidelines

## Resources

- **Project Documentation**: [docs/](../docs/)
- **API Reference**: [docs/api/INDEX.md](api/INDEX.md)
- **Module Registry**: [docs/modules/REGISTRY.md](modules/REGISTRY.md)
- **GitHub Repository**: https://github.com/yxhpy/openuser
- **Issue Tracker**: https://github.com/yxhpy/openuser/issues

## Getting Help

- Check [Known Issues](troubleshooting/KNOWN_ISSUES.md)
- Search existing GitHub issues
- Ask in discussions
- Read the documentation

## License

See [LICENSE](../LICENSE) for details.
