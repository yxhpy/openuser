# Module Registry

This registry tracks all implemented modules to prevent duplication and facilitate code reuse.

**Before implementing a new feature, check this registry first!**

## Status Legend
- ✅ Implemented (100% test coverage)
- 🚧 In Progress
- 📝 Planned
- ❌ Deprecated

---

## Core Modules

### Plugin Manager
- **Path**: `src/core/plugin_manager.py`
- **Purpose**: Hot-reload plugin system with dependency resolution
- **Status**: 📝 Planned
- **Test Coverage**: N/A
- **Dependencies**: None
- **API**:
  - `PluginManager.load_plugin(name: str) -> Plugin`
  - `PluginManager.reload_plugin(name: str) -> bool`
  - `PluginManager.unload_plugin(name: str) -> bool`
  - `PluginManager.list_plugins() -> List[Plugin]`
  - `PluginManager.install_plugin(name: str, source: str) -> bool`

### Agent Manager
- **Path**: `src/core/agent_manager.py`
- **Purpose**: AI agent lifecycle management with self-update capability
- **Status**: 📝 Planned
- **Test Coverage**: N/A
- **Dependencies**: Plugin Manager
- **API**:
  - `AgentManager.create_agent(name: str, config: dict) -> Agent`
  - `AgentManager.update_agent(id: str, updates: dict) -> Agent`
  - `AgentManager.delete_agent(id: str) -> bool`
  - `AgentManager.list_agents() -> List[Agent]`

### Config Manager
- **Path**: `src/core/config_manager.py`
- **Purpose**: Dynamic configuration with hot-reload
- **Status**: 📝 Planned
- **Test Coverage**: N/A
- **Dependencies**: None
- **API**:
  - `ConfigManager.get(key: str) -> Any`
  - `ConfigManager.set(key: str, value: Any) -> bool`
  - `ConfigManager.reload() -> bool`
  - `ConfigManager.watch(auto_reload: bool) -> None`

---

## Digital Human Modules

### Voice Cloning
- **Path**: `src/models/voice_cloning.py`
- **Purpose**: TTS model integration for voice cloning
- **Status**: 📝 Planned
- **Test Coverage**: N/A
- **Dependencies**: torch, librosa
- **API**:
  - `VoiceCloner.train(samples: List[str]) -> Model`
  - `VoiceCloner.synthesize(text: str, model: Model) -> bytes`

### Face Animation
- **Path**: `src/models/face_animation.py`
- **Purpose**: Wav2Lip and SadTalker integration
- **Status**: 📝 Planned
- **Test Coverage**: N/A
- **Dependencies**: torch, opencv
- **API**:
  - `FaceAnimator.animate(image: str, audio: str) -> str`
  - `FaceAnimator.enhance(video: str) -> str`

### Video Generation
- **Path**: `src/models/video_generation.py`
- **Purpose**: Full digital human video generation pipeline
- **Status**: 📝 Planned
- **Test Coverage**: N/A
- **Dependencies**: Face Animation, Voice Cloning
- **API**:
  - `VideoGenerator.generate(config: dict) -> str`

---

## API Modules

### FastAPI Application
- **Path**: `src/api/main.py`
- **Purpose**: Main FastAPI application
- **Status**: 📝 Planned
- **Test Coverage**: N/A
- **Dependencies**: All core modules
- **Endpoints**: See [api/INDEX.md](../api/INDEX.md)

### Authentication
- **Path**: `src/api/auth.py`
- **Purpose**: JWT authentication
- **Status**: 📝 Planned
- **Test Coverage**: N/A
- **Dependencies**: python-jose
- **API**:
  - `POST /api/v1/auth/login`
  - `POST /api/v1/auth/register`
  - `POST /api/v1/auth/refresh`

---

## Integration Modules

### Feishu Integration
- **Path**: `src/integrations/feishu/`
- **Purpose**: Feishu bot integration
- **Status**: 📝 Planned
- **Test Coverage**: N/A
- **Dependencies**: httpx
- **API**:
  - `FeishuBot.send_message(chat_id: str, content: str) -> bool`
  - `FeishuBot.handle_webhook(data: dict) -> dict`

### WeChat Work Integration
- **Path**: `src/integrations/wechat/`
- **Purpose**: WeChat Work bot integration
- **Status**: 📝 Planned
- **Test Coverage**: N/A
- **Dependencies**: httpx
- **API**:
  - `WeChatBot.send_message(user_id: str, content: str) -> bool`
  - `WeChatBot.handle_webhook(data: dict) -> dict`

---

## Plugin Modules

### Image Processor
- **Path**: `src/plugins/image_processor.py`
- **Purpose**: Image preprocessing and enhancement
- **Status**: 📝 Planned
- **Test Coverage**: N/A
- **Dependencies**: PIL, OpenCV
- **API**:
  - `ImageProcessor.resize(image: str, size: tuple) -> str`
  - `ImageProcessor.enhance(image: str) -> str`

### Video Editor
- **Path**: `src/plugins/video_editor.py`
- **Purpose**: Video editing utilities
- **Status**: 📝 Planned
- **Test Coverage**: N/A
- **Dependencies**: ffmpeg
- **API**:
  - `VideoEditor.trim(video: str, start: float, end: float) -> str`
  - `VideoEditor.concat(videos: List[str]) -> str`

### Audio Enhancer
- **Path**: `src/plugins/audio_enhancer.py`
- **Purpose**: Audio enhancement and noise reduction
- **Status**: 📝 Planned
- **Test Coverage**: N/A
- **Dependencies**: librosa
- **API**:
  - `AudioEnhancer.denoise(audio: str) -> str`
  - `AudioEnhancer.normalize(audio: str) -> str`

---

## Utility Modules

### File Manager
- **Path**: `src/utils/file_manager.py`
- **Purpose**: File upload/download management
- **Status**: 📝 Planned
- **Test Coverage**: N/A
- **Dependencies**: None
- **API**:
  - `FileManager.upload(file: bytes, filename: str) -> str`
  - `FileManager.download(path: str) -> bytes`

### Logger
- **Path**: `src/utils/logger.py`
- **Purpose**: Centralized logging
- **Status**: 📝 Planned
- **Test Coverage**: N/A
- **Dependencies**: logging
- **API**:
  - `Logger.info(message: str) -> None`
  - `Logger.error(message: str, exc: Exception) -> None`

---

## Database Models

### User Model
- **Path**: `src/models/user.py`
- **Purpose**: User data model
- **Status**: 📝 Planned
- **Test Coverage**: N/A
- **Dependencies**: SQLAlchemy
- **Fields**: id, username, email, password_hash, created_at

### Digital Human Model
- **Path**: `src/models/digital_human.py`
- **Purpose**: Digital human data model
- **Status**: 📝 Planned
- **Test Coverage**: N/A
- **Dependencies**: SQLAlchemy
- **Fields**: id, user_id, name, image_path, voice_model_path, created_at

### Task Model
- **Path**: `src/models/task.py`
- **Purpose**: Scheduled task data model
- **Status**: 📝 Planned
- **Test Coverage**: N/A
- **Dependencies**: SQLAlchemy
- **Fields**: id, name, schedule, task_type, params, status, created_at

---

## Notes

- Update this registry after implementing each module
- Include test coverage percentage
- Document all public APIs
- Mark deprecated modules with ❌
- Link to detailed documentation when available

## Last Updated

2026-02-02 - Initial registry created
