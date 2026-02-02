---
name: auto-doc
description: 代码变更后自动更新文档和模块注册表。当检测到新功能实现或 API 变更时自动触发。
---

# Auto Documentation Skill

This skill automatically updates documentation and module registry after code changes.

## Trigger Conditions

This skill is triggered when:
- New feature is implemented
- API endpoints are added/modified
- Module structure changes
- Tests pass successfully
- User explicitly requests documentation update

## Behavior

When triggered, this skill will:

1. **Detect Changes** - Identify what was modified
2. **Update Module Registry** - Add new modules to `docs/modules/REGISTRY.md`
3. **Update API Docs** - Regenerate API documentation
4. **Update Integration Docs** - Update integration guides if needed
5. **Update CHANGELOG** - Record changes in CHANGELOG.md
6. **Verify Links** - Check all documentation links are valid
7. **Record in Memory** - Update project memory with changes

## Documentation Structure

```
docs/
├── INDEX.md                      # Main documentation index
├── modules/
│   └── REGISTRY.md              # Module registry (prevent duplication)
├── api/
│   ├── INDEX.md                 # API overview
│   ├── digital-human.md         # Digital human endpoints
│   ├── plugins.md               # Plugin endpoints
│   ├── agents.md                # Agent endpoints
│   └── scheduler.md             # Scheduler endpoints
├── integrations/
│   ├── FEISHU.md               # Feishu integration guide
│   ├── WECHAT.md               # WeChat Work integration guide
│   └── WEB.md                  # Web interface guide
└── troubleshooting/
    ├── KNOWN_ISSUES.md         # Known issues and solutions
    └── FAQ.md                  # Frequently asked questions
```

## Module Registry Format

`docs/modules/REGISTRY.md` tracks all implemented modules to prevent duplication:

```markdown
# Module Registry

## Core Modules

### Plugin Manager
- **Path**: `src/core/plugin_manager.py`
- **Purpose**: Hot-reload plugin system
- **Status**: ✅ Implemented
- **Test Coverage**: 100%
- **Dependencies**: None
- **API**: `PluginManager.load_plugin()`, `PluginManager.reload_plugin()`

### Agent Manager
- **Path**: `src/core/agent_manager.py`
- **Purpose**: AI agent lifecycle management
- **Status**: ✅ Implemented
- **Test Coverage**: 100%
- **Dependencies**: Plugin Manager
- **API**: `AgentManager.create_agent()`, `AgentManager.update_agent()`

## Plugins

### Image Processor
- **Path**: `src/plugins/image_processor.py`
- **Purpose**: Image preprocessing and enhancement
- **Status**: ✅ Implemented
- **Test Coverage**: 100%
- **Dependencies**: PIL, OpenCV
- **API**: `ImageProcessor.process()`

## Integrations

### Feishu Integration
- **Path**: `src/integrations/feishu/`
- **Purpose**: Feishu bot integration
- **Status**: 🚧 In Progress
- **Test Coverage**: 80%
- **Dependencies**: httpx
- **API**: `FeishuBot.send_message()`, `FeishuBot.handle_webhook()`
```

## API Documentation Format

API docs are auto-generated from FastAPI schemas:

```markdown
# Digital Human API

## Create Digital Human

**Endpoint**: `POST /api/v1/digital-human/create`

**Description**: Create a new digital human from image and voice samples.

**Request Body**:
```json
{
  "name": "string",
  "image_path": "string",
  "voice_samples": ["string"],
  "options": {
    "model": "sadtalker",
    "quality": "high"
  }
}
```

**Response**:
```json
{
  "id": "string",
  "name": "string",
  "status": "created",
  "created_at": "2024-01-01T00:00:00Z"
}
```

**Example**:
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/digital-human/create",
    json={
        "name": "My Avatar",
        "image_path": "avatar.jpg",
        "voice_samples": ["sample1.wav", "sample2.wav"]
    }
)
```
```

## Update Process

### 1. Update Module Registry

When a new module is implemented:

```python
# Auto-detect new modules
new_modules = detect_new_modules("src/")

# Update registry
for module in new_modules:
    add_to_registry(
        name=module.name,
        path=module.path,
        purpose=module.docstring,
        status="✅ Implemented",
        coverage=get_coverage(module.path)
    )
```

### 2. Update API Documentation

When API endpoints change:

```python
# Extract OpenAPI schema
schema = app.openapi()

# Generate markdown docs
for path, methods in schema["paths"].items():
    generate_api_doc(path, methods)
```

### 3. Update Integration Docs

When integration code changes:

```python
# Check integration changes
if "src/integrations/feishu" in changed_files:
    update_doc("docs/integrations/FEISHU.md")
```

## Automation Script

`.claude/skills/auto-doc/update-docs.sh`:

```bash
#!/bin/bash

echo "Updating documentation..."

# Update module registry
python .claude/scripts/update-registry.py

# Generate API docs from OpenAPI schema
python .claude/scripts/generate-api-docs.py

# Update CHANGELOG
python .claude/scripts/update-changelog.py

# Verify all links
python .claude/scripts/verify-links.py

echo "Documentation updated successfully!"
```

## CHANGELOG Format

`CHANGELOG.md` follows Keep a Changelog format:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- Plugin hot-reload capability
- Agent self-update mechanism
- Feishu integration

### Changed
- Improved test coverage to 100%
- Optimized digital human generation speed

### Fixed
- Fixed plugin dependency resolution bug
- Fixed memory leak in agent manager

## [0.1.0] - 2024-01-01

### Added
- Initial project structure
- Core plugin system
- Basic API endpoints
```

## Integration with Other Skills

- **start-dev**: Updates docs after completing a task
- **auto-test**: Updates docs after tests pass
- **hot-reload**: Updates docs after plugin reload

## Verification

After updating documentation:

1. **Check Links** - Ensure all internal links work
2. **Validate Markdown** - Check markdown syntax
3. **Verify Examples** - Test code examples
4. **Check Coverage** - Ensure all modules are documented

## Example Output

```
Updating documentation...

✅ Module Registry updated
   - Added: src/core/plugin_manager.py
   - Added: src/core/agent_manager.py

✅ API Documentation updated
   - Generated: docs/api/digital-human.md
   - Generated: docs/api/plugins.md

✅ CHANGELOG updated
   - Added 3 new entries

✅ Link verification passed
   - Checked 45 links, all valid

Documentation update complete!
```

## Best Practices

1. **Keep Registry Updated** - Always update after implementing features
2. **Document APIs** - Use OpenAPI schemas for consistency
3. **Include Examples** - Provide code examples for all APIs
4. **Track Changes** - Maintain detailed CHANGELOG
5. **Verify Links** - Check links before committing
6. **Use Templates** - Consistent documentation format
7. **Auto-Generate** - Generate docs from code when possible
