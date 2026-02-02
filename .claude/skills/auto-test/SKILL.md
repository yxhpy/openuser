---
name: auto-test
description: 代码变更后自动运行测试，确保 100% 覆盖率。当检测到 src/ 目录下的 Python 文件变更时自动触发。
---

# Auto Test Skill

This skill automatically runs tests after code changes to ensure 100% test coverage.

## Trigger Conditions

This skill is triggered when:
- Any Python file in `src/` is modified
- User explicitly requests to run tests
- After completing a feature implementation
- Before committing code

## Behavior

When triggered, this skill will:

1. **Detect Changes** - Identify which files were modified
2. **Run Relevant Tests** - Run tests for the modified modules
3. **Check Coverage** - Ensure 100% coverage (`pytest --cov --cov-fail-under=100`)
4. **Report Results** - Display test results and coverage report
5. **Handle Failures** - If tests fail, provide debugging guidance
6. **Update Status** - Record test results in project memory

## Test Commands

### Run All Tests
```bash
pytest --cov --cov-fail-under=100
```

### Run Specific Test Suite
```bash
pytest tests/unit/ --cov=src
pytest tests/integration/ --cov=src
pytest tests/e2e/ --cov=src
```

### Run Tests for Specific Module
```bash
pytest tests/unit/test_plugin_manager.py --cov=src.core.plugin_manager
```

### Generate HTML Coverage Report
```bash
pytest --cov --cov-report=html
open htmlcov/index.html
```

## Coverage Requirements

- **Minimum Coverage**: 100%
- **Branch Coverage**: Required
- **Function Coverage**: Required
- **Line Coverage**: Required

## Test Structure

```
tests/
├── unit/                  # Unit tests (fast, isolated)
│   ├── test_plugin_manager.py
│   ├── test_agent_manager.py
│   └── test_config_manager.py
├── integration/           # Integration tests (multiple components)
│   ├── test_api_endpoints.py
│   ├── test_plugin_integration.py
│   └── test_agent_integration.py
└── e2e/                   # End-to-end tests (full workflows)
    ├── test_digital_human_creation.py
    ├── test_plugin_hot_reload.py
    └── test_agent_self_update.py
```

## Test Patterns

### Unit Test Example
```python
# tests/unit/test_plugin_manager.py
import pytest
from src.core.plugin_manager import PluginManager

def test_plugin_manager_init():
    """Test PluginManager initialization"""
    pm = PluginManager()
    assert pm is not None
    assert pm.plugins == {}

def test_load_plugin():
    """Test loading a plugin"""
    pm = PluginManager()
    pm.load_plugin("test-plugin")
    assert "test-plugin" in pm.plugins

def test_reload_plugin():
    """Test hot-reloading a plugin"""
    pm = PluginManager()
    pm.load_plugin("test-plugin")
    pm.reload_plugin("test-plugin")
    assert "test-plugin" in pm.plugins
```

### Integration Test Example
```python
# tests/integration/test_api_endpoints.py
import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_create_digital_human():
    """Test digital human creation endpoint"""
    response = client.post(
        "/api/v1/digital-human/create",
        json={
            "name": "Test Avatar",
            "image_path": "test.jpg",
            "voice_samples": ["sample1.wav"]
        }
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"
```

## Failure Handling

If tests fail:

1. **Display Error Details** - Show which tests failed and why
2. **Suggest Fixes** - Provide guidance on how to fix the issue
3. **Check Coverage** - Identify uncovered lines
4. **Prevent Commit** - Block commit if tests fail (via pre-commit hook)

## Example Output

```
Running tests...

============================= test session starts ==============================
platform darwin -- Python 3.10.0, pytest-7.4.0, pluggy-1.0.0
rootdir: /Users/yxhpy/PycharmProjects/openuser
plugins: cov-4.1.0, asyncio-0.21.0
collected 45 items

tests/unit/test_plugin_manager.py ........                              [ 17%]
tests/unit/test_agent_manager.py ........                               [ 35%]
tests/integration/test_api_endpoints.py ........                        [ 53%]
tests/e2e/test_digital_human_creation.py ........                       [ 71%]

---------- coverage: platform darwin, python 3.10.0-final-0 -----------
Name                                Stmts   Miss  Cover
-------------------------------------------------------
src/core/plugin_manager.py            120      0   100%
src/core/agent_manager.py             95       0   100%
src/api/main.py                       80       0   100%
-------------------------------------------------------
TOTAL                                 295      0   100%

============================== 45 passed in 2.34s ===============================

✅ All tests passed with 100% coverage!
```

## Integration with Other Skills

- **start-dev**: Runs tests after implementing a task
- **auto-doc**: Updates documentation after tests pass
- **hot-reload**: Runs tests after reloading plugins

## Configuration

Test configuration in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--cov=src",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-fail-under=100",
    "-v"
]
```

## Best Practices

1. **Write Tests First** - TDD approach
2. **Test Edge Cases** - Cover all scenarios
3. **Mock External Dependencies** - Use pytest fixtures
4. **Keep Tests Fast** - Unit tests should run in milliseconds
5. **Descriptive Names** - Test names should describe what they test
6. **One Assert Per Test** - Keep tests focused
7. **Use Fixtures** - Share setup code across tests
