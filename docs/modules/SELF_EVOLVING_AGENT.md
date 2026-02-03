# Self-Evolving Agent System

## Overview

The Self-Evolving Agent System provides advanced AI agent capabilities that enable agents to adapt, learn, and improve autonomously. This system is a key component of the OpenUser project's agent self-evolution features.

## Features

### 1. Prompt-Based Self-Update
Agents can update their own system prompts based on interactions and requirements.

```python
from src.core.self_evolving_agent import SelfEvolvingAgent

agent = SelfEvolvingAgent(
    name="my_agent",
    system_prompt="Initial prompt",
    capabilities=["basic"]
)

# Agent updates its own prompt
result = agent.self_update_prompt(
    new_prompt="Enhanced prompt with new capabilities",
    reason="User requested more detailed responses"
)
```

### 2. Auto-Install Plugins
Agents can automatically install plugins when they need new capabilities.

```python
# Agent detects it needs image processing capability
result = agent.auto_install_plugin(
    plugin_name="image_processor",
    reason="User requested image manipulation"
)

# Plugin capabilities are automatically added to agent
print(agent.capabilities)  # Now includes image processing capabilities
```

### 3. Create Custom Plugins Programmatically
Agents can create new plugins on-the-fly to meet specific needs.

```python
# Agent creates a custom plugin
result = agent.create_custom_plugin(
    name="custom_analyzer",
    version="1.0.0",
    description="Custom data analyzer",
    capabilities=["analyze_data", "generate_report"]
)

# Or with custom code
result = agent.create_custom_plugin(
    name="custom_plugin",
    version="1.0.0",
    description="Custom plugin",
    capabilities=["custom_cap"],
    custom_code="""
from src.core.plugin_manager import Plugin

class CustomPlugin(Plugin):
    def execute(self, action, params):
        # Custom implementation
        return {"status": "success"}
"""
)
```

### 4. Environment Parameter Adjustment
Agents can adjust their environment parameters dynamically.

```python
# Agent adjusts its environment
result = agent.adjust_environment(
    key="response_style",
    value="detailed",
    reason="User prefers detailed explanations"
)

# Later, agent uses this parameter
style = agent.context.get_environment("response_style")
```

### 5. Context Awareness
Agents maintain context of interactions and learn from patterns.

```python
# Agent automatically tracks interactions
await agent.process({"input": "Hello, how are you?"})

# Get recent interactions
recent = agent.context.get_recent_interactions(count=5)

# Agent learns patterns
agent.context.learn_pattern("greeting_style", {
    "formal": False,
    "friendly": True
})

# Retrieve learned patterns
style = agent.context.get_pattern("greeting_style")
```

### 6. Learning from Interactions
Agents analyze interaction patterns and adapt their behavior.

```python
# Agent automatically analyzes patterns
patterns = agent._analyze_interaction_patterns(interactions)

# Patterns include frequent topics and user preferences
print(patterns["frequent_topics"])  # ["testing", "development", "deployment"]
```

### 7. Decision Making
Agents make autonomous decisions based on context and input.

```python
# Agent processes input and makes decisions
result = await agent.process({
    "input": "I need to install the video editor plugin"
})

# Agent automatically decides to install the plugin
# Decision history is tracked
print(agent.decision_history[-1])
```

### 8. Error Recovery
Agents handle errors gracefully and learn from them.

```python
# Agent encounters an error
try:
    result = await agent.process({"input": "problematic input"})
except Exception as e:
    # Agent records error and attempts recovery
    pass

# Check error history
print(agent.error_history)

# Agent provides recovery suggestions for known errors
```

## Architecture

### AgentContext
Manages agent's interaction history, learned patterns, and environment parameters.

**Key Methods:**
- `add_interaction()` - Record user interactions
- `learn_pattern()` - Store learned patterns
- `get_pattern()` - Retrieve learned patterns
- `update_environment()` - Update environment parameters
- `to_dict()` / `from_dict()` - Persistence

### PluginCreator
Helper class for creating custom plugins programmatically.

**Key Methods:**
- `generate_plugin_template()` - Generate plugin code template
- `create_plugin()` - Create plugin file

### SelfEvolvingAgent
Main agent class with self-evolution capabilities.

**Key Methods:**
- `self_update_prompt()` - Update system prompt
- `auto_install_plugin()` - Install plugins automatically
- `create_custom_plugin()` - Create custom plugins
- `adjust_environment()` - Adjust environment parameters
- `process()` - Process user input with context awareness
- `get_learning_stats()` - Get learning statistics

## Usage Examples

### Basic Agent Creation

```python
from src.core.self_evolving_agent import SelfEvolvingAgent
from src.core.plugin_manager import PluginManager

# Create agent with plugin manager
plugin_manager = PluginManager()
agent = SelfEvolvingAgent(
    name="assistant",
    system_prompt="You are a helpful AI assistant",
    capabilities=["conversation", "task_execution"],
    plugin_manager=plugin_manager,
    context_file=".agent_context.json"
)
```

### Processing User Input

```python
# Agent processes input with context awareness
result = await agent.process({
    "input": "Can you help me process images?"
})

# Agent may automatically:
# 1. Detect need for image processing capability
# 2. Install image_processor plugin
# 3. Add image processing to capabilities
# 4. Process the request
```

### Monitoring Agent Learning

```python
# Get learning statistics
stats = agent.get_learning_stats()

print(f"Total interactions: {stats['total_interactions']}")
print(f"Learned patterns: {stats['learned_patterns']}")
print(f"Environment params: {stats['environment_params']}")
print(f"Total errors: {stats['total_errors']}")
print(f"Total decisions: {stats['total_decisions']}")
print(f"Capabilities: {stats['capabilities']}")
```

### Context Persistence

```python
# Context is automatically saved to file
agent._save_context()

# Load context in new session
new_agent = SelfEvolvingAgent(
    name="assistant",
    system_prompt="You are a helpful AI assistant",
    context_file=".agent_context.json"  # Loads previous context
)

# Agent remembers previous interactions and learned patterns
```

## API Integration

The self-evolving agent system integrates with the existing Agent API:

```python
# In src/api/agents.py
from src.core.self_evolving_agent import SelfEvolvingAgent

@router.post("/api/v1/agents/create-evolving")
async def create_evolving_agent(request: AgentCreateRequest):
    """Create a self-evolving agent."""
    agent = SelfEvolvingAgent(
        name=request.name,
        system_prompt=request.system_prompt,
        capabilities=request.capabilities
    )
    return {"status": "success", "agent": agent.name}
```

## Testing

Comprehensive test suite with 40 tests covering all features:

```bash
# Run tests
pytest tests/test_self_evolving_agent.py -v

# Run with coverage
pytest tests/test_self_evolving_agent.py --cov=src/core/self_evolving_agent
```

## Configuration

### Context File
Agents store their context in JSON files:

```json
{
  "context": {
    "interactions": [...],
    "learned_patterns": {...},
    "environment": {...}
  },
  "error_history": [...],
  "decision_history": [...]
}
```

### Environment Parameters
Common environment parameters:
- `response_style` - Agent's response style (brief, detailed, technical)
- `learning_rate` - How quickly agent adapts to patterns
- `error_tolerance` - How agent handles errors
- `plugin_auto_install` - Whether to auto-install plugins

## Best Practices

1. **Context Management**
   - Set appropriate `max_history` to balance memory and context
   - Regularly save context for persistence
   - Clean up old context files periodically

2. **Plugin Management**
   - Use descriptive plugin names
   - Document plugin capabilities clearly
   - Test plugins before auto-installation

3. **Error Handling**
   - Monitor error history for patterns
   - Implement recovery strategies for common errors
   - Log errors for debugging

4. **Learning**
   - Review learned patterns periodically
   - Validate pattern accuracy
   - Remove outdated patterns

5. **Security**
   - Validate plugin code before creation
   - Restrict plugin installation to trusted sources
   - Monitor agent behavior for anomalies

## Performance Considerations

- **Context Size**: Limit interaction history to prevent memory issues
- **Pattern Storage**: Clean up unused patterns periodically
- **Plugin Loading**: Cache loaded plugins to avoid repeated loading
- **File I/O**: Batch context saves to reduce disk operations

## Troubleshooting

### Agent Not Learning
- Check if context is being saved properly
- Verify `max_history` is not too small
- Ensure patterns are being recorded

### Plugin Installation Fails
- Verify plugin exists in plugin directory
- Check plugin dependencies
- Review error logs

### High Memory Usage
- Reduce `max_history` value
- Clean up old context files
- Limit number of learned patterns

## Future Enhancements

- **Advanced Pattern Recognition**: ML-based pattern analysis
- **Multi-Agent Collaboration**: Agents sharing learned patterns
- **Automatic Capability Discovery**: Agents discovering new capabilities
- **Performance Optimization**: Caching and indexing for faster lookups
- **Security Enhancements**: Sandboxed plugin execution

## Related Documentation

- [Agent Manager](./AGENT_MANAGER.md)
- [Plugin System](../plugins/PLUGIN_SYSTEM.md)
- [API Documentation](../api/AGENTS.md)

## Last Updated

2026-02-03 - Initial implementation of self-evolving agent system
