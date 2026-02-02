---
name: hot-reload
description: 热更新插件、技能和配置，无需重启系统。当用户请求更新插件或检测到配置变更时自动触发。
---

# Hot Reload Skill

This skill enables hot-reloading of plugins, skills, and configurations without system restart.

## Trigger Conditions

This skill is triggered when:
- User requests to reload a plugin
- Plugin files are modified
- Skill files are modified
- Configuration files are changed
- User says "reload", "热更新", "刷新插件"

## Behavior

When triggered, this skill will:

1. **Detect Changes** - Identify what needs to be reloaded
2. **Validate Changes** - Check syntax and dependencies
3. **Backup State** - Save current state before reload
4. **Reload Components** - Hot-reload plugins/skills/config
5. **Verify Reload** - Test that reload was successful
6. **Rollback if Failed** - Restore previous state if reload fails
7. **Update Registry** - Record reload in project memory

## Hot Reload Capabilities

### 1. Plugin Hot Reload

Reload plugins without restarting the system:

```python
from src.core.plugin_manager import PluginManager

pm = PluginManager()

# Reload single plugin
pm.reload_plugin("image-processor")

# Reload all plugins
pm.reload_all_plugins()

# Reload with dependency resolution
pm.reload_plugin("video-editor", resolve_deps=True)
```

**Process**:
1. Unload plugin (call `on_unload()` hook)
2. Clear module cache
3. Reimport plugin module
4. Load plugin (call `on_load()` hook)
5. Restore plugin state if needed

### 2. Skill Hot Reload

Reload Claude Code skills on-the-fly:

```python
from src.core.skill_manager import SkillManager

sm = SkillManager()

# Reload single skill
sm.reload_skill("auto-test")

# Reload all skills
sm.reload_all_skills()
```

**Process**:
1. Parse SKILL.md file
2. Validate skill configuration
3. Update skill registry
4. Reload skill logic

### 3. Configuration Hot Reload

Reload configuration without restart:

```python
from src.core.config_manager import ConfigManager

cm = ConfigManager()

# Reload configuration
cm.reload_config()

# Reload specific section
cm.reload_section("database")

# Watch for changes
cm.watch_config(auto_reload=True)
```

**Process**:
1. Read configuration file
2. Validate configuration
3. Apply new configuration
4. Notify dependent components

### 4. Agent Hot Reload

Reload AI agents with updated prompts:

```python
from src.core.agent_manager import AgentManager

am = AgentManager()

# Reload agent with new prompt
am.reload_agent("assistant", new_prompt="You are a helpful assistant")

# Reload agent capabilities
am.reload_agent_capabilities("assistant", ["plugin-install", "self-update"])
```

## Implementation

### Plugin Hot Reload Implementation

```python
# src/core/plugin_manager.py
import importlib
import sys

class PluginManager:
    def reload_plugin(self, plugin_name: str) -> bool:
        """Hot-reload a plugin without restart"""
        try:
            # 1. Get plugin instance
            plugin = self.plugins.get(plugin_name)
            if not plugin:
                raise ValueError(f"Plugin {plugin_name} not found")

            # 2. Call unload hook
            plugin.on_unload()

            # 3. Clear module cache
            module_name = plugin.__module__
            if module_name in sys.modules:
                del sys.modules[module_name]

            # 4. Reimport module
            module = importlib.import_module(module_name)
            importlib.reload(module)

            # 5. Get new plugin class
            plugin_class = getattr(module, plugin.__class__.__name__)

            # 6. Create new instance
            new_plugin = plugin_class()

            # 7. Call load hook
            new_plugin.on_load()

            # 8. Replace old plugin
            self.plugins[plugin_name] = new_plugin

            self.logger.info(f"Plugin {plugin_name} reloaded successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to reload plugin {plugin_name}: {e}")
            return False
```

### Configuration Hot Reload Implementation

```python
# src/core/config_manager.py
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ConfigManager:
    def __init__(self):
        self.config = {}
        self.watchers = []

    def reload_config(self) -> bool:
        """Reload configuration from file"""
        try:
            with open(".env", "r") as f:
                new_config = json.load(f)

            # Validate configuration
            self.validate_config(new_config)

            # Apply new configuration
            self.config = new_config

            # Notify listeners
            self.notify_config_change()

            return True
        except Exception as e:
            self.logger.error(f"Failed to reload config: {e}")
            return False

    def watch_config(self, auto_reload: bool = True):
        """Watch configuration file for changes"""
        class ConfigChangeHandler(FileSystemEventHandler):
            def __init__(self, config_manager):
                self.config_manager = config_manager

            def on_modified(self, event):
                if event.src_path.endswith(".env"):
                    if auto_reload:
                        self.config_manager.reload_config()

        handler = ConfigChangeHandler(self)
        observer = Observer()
        observer.schedule(handler, path=".", recursive=False)
        observer.start()
        self.watchers.append(observer)
```

## API Endpoints

### Reload Plugin
```http
POST /api/v1/plugins/{name}/reload
```

### Reload All Plugins
```http
POST /api/v1/plugins/reload-all
```

### Reload Configuration
```http
POST /api/v1/config/reload
```

### Reload Agent
```http
POST /api/v1/agents/{id}/reload
```

## Safety Mechanisms

### 1. State Backup

Before reloading, backup current state:

```python
def backup_state(self, plugin_name: str):
    """Backup plugin state before reload"""
    plugin = self.plugins[plugin_name]
    state = plugin.get_state()
    self.state_backup[plugin_name] = state
```

### 2. Rollback on Failure

If reload fails, restore previous state:

```python
def rollback(self, plugin_name: str):
    """Rollback to previous state if reload fails"""
    if plugin_name in self.state_backup:
        state = self.state_backup[plugin_name]
        plugin = self.plugins[plugin_name]
        plugin.restore_state(state)
```

### 3. Dependency Resolution

Reload dependent plugins in correct order:

```python
def reload_with_dependencies(self, plugin_name: str):
    """Reload plugin and its dependencies"""
    deps = self.get_dependencies(plugin_name)
    for dep in deps:
        self.reload_plugin(dep)
    self.reload_plugin(plugin_name)
```

## Example Usage

### Reload Plugin via CLI

```bash
# Reload single plugin
curl -X POST http://localhost:8000/api/v1/plugins/image-processor/reload

# Reload all plugins
curl -X POST http://localhost:8000/api/v1/plugins/reload-all
```

### Reload Plugin via Code

```python
from src.core.plugin_manager import PluginManager

pm = PluginManager()

# Modify plugin code
with open("src/plugins/image_processor.py", "w") as f:
    f.write(new_code)

# Hot-reload plugin
pm.reload_plugin("image-processor")

# Plugin is now using new code without restart!
```

### Auto-Reload on File Change

```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class PluginChangeHandler(FileSystemEventHandler):
    def __init__(self, plugin_manager):
        self.pm = plugin_manager

    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            plugin_name = self.extract_plugin_name(event.src_path)
            self.pm.reload_plugin(plugin_name)

handler = PluginChangeHandler(pm)
observer = Observer()
observer.schedule(handler, path="src/plugins", recursive=True)
observer.start()
```

## Testing Hot Reload

```python
# tests/integration/test_hot_reload.py
def test_plugin_hot_reload():
    """Test plugin hot reload"""
    pm = PluginManager()

    # Load plugin
    pm.load_plugin("test-plugin")
    original_version = pm.plugins["test-plugin"].version

    # Modify plugin code
    modify_plugin_code("test-plugin", new_version="2.0.0")

    # Hot-reload
    pm.reload_plugin("test-plugin")

    # Verify new version loaded
    assert pm.plugins["test-plugin"].version == "2.0.0"
    assert pm.plugins["test-plugin"].version != original_version
```

## Best Practices

1. **Backup Before Reload** - Always backup state before reloading
2. **Validate Changes** - Check syntax and dependencies before reload
3. **Test After Reload** - Verify reload was successful
4. **Rollback on Failure** - Restore previous state if reload fails
5. **Log Everything** - Record all reload operations
6. **Handle Dependencies** - Reload dependent plugins in correct order
7. **Graceful Degradation** - System should continue working if reload fails

## Integration with Other Skills

- **start-dev**: Reloads plugins after implementing changes
- **auto-test**: Tests plugins after reload
- **auto-doc**: Updates docs after successful reload
