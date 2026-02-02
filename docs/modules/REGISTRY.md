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
- **Status**: ✅ Implemented (100% test coverage)
- **Test Coverage**: 100%
- **Dependencies**: None
- **API**:
  - `PluginManager.load_plugin(name: str) -> Plugin`
  - `PluginManager.reload_plugin(name: str) -> bool`
  - `PluginManager.unload_plugin(name: str) -> bool`
  - `PluginManager.list_plugins() -> List[Plugin]`
  - `PluginManager.get_plugin(name: str) -> Optional[Plugin]`
- **Features**:
  - Hot-reload plugins without restart
  - State backup and rollback
  - Plugin lifecycle hooks (on_load, on_unload)
  - Error handling and recovery

### Agent Manager
- **Path**: `src/core/agent_manager.py`
- **Purpose**: AI agent lifecycle management with self-update capability
- **Status**: ✅ Implemented (100% test coverage)
- **Test Coverage**: 100%
- **Dependencies**: None
- **API**:
  - `AgentManager.create_agent(name: str, system_prompt: str, capabilities: List[str]) -> Agent`
  - `AgentManager.update_agent(name: str, system_prompt: str, capabilities: List[str]) -> Agent`
  - `AgentManager.delete_agent(name: str) -> bool`
  - `AgentManager.list_agents() -> List[str]`
  - `AgentManager.get_agent(name: str) -> Optional[Agent]`
  - `Agent.update_prompt(new_prompt: str) -> None`
  - `Agent.add_capability(capability: str) -> None`
  - `Agent.remove_capability(capability: str) -> None`
- **Features**:
  - Agent lifecycle management
  - Dynamic prompt updates
  - Capability management
  - Memory tracking

### Config Manager
- **Path**: `src/core/config_manager.py`
- **Purpose**: Dynamic configuration with hot-reload
- **Status**: ✅ Implemented (100% test coverage)
- **Test Coverage**: 100%
- **Dependencies**: None
- **API**:
  - `ConfigManager.get(key: str, default: Any) -> Any`
  - `ConfigManager.set(key: str, value: Any) -> None`
  - `ConfigManager.reload_config() -> bool`
  - `ConfigManager.load_config() -> bool`
  - `ConfigManager.get_all() -> Dict[str, Any]`
- **Features**:
  - Load configuration from .env files
  - Hot-reload configuration
  - Key-value storage
  - Comment and empty line handling

### Redis Manager
- **Path**: `src/core/redis_manager.py`
- **Purpose**: Redis connection and cache management
- **Status**: ✅ Implemented (100% test coverage)
- **Test Coverage**: 100%
- **Dependencies**: redis
- **API**:
  - `RedisManager.get(key: str) -> Optional[str]`
  - `RedisManager.set(key: str, value: str, ex: Optional[int], nx: bool) -> bool`
  - `RedisManager.delete(*keys: str) -> int`
  - `RedisManager.exists(*keys: str) -> int`
  - `RedisManager.expire(key: str, seconds: int) -> bool`
  - `RedisManager.ttl(key: str) -> int`
  - `RedisManager.get_json(key: str) -> Optional[Any]`
  - `RedisManager.set_json(key: str, value: Any, ex: Optional[int], nx: bool) -> bool`
  - `RedisManager.hget(name: str, key: str) -> Optional[str]`
  - `RedisManager.hset(name: str, key: str, value: str) -> int`
  - `RedisManager.hgetall(name: str) -> dict`
  - `RedisManager.hdel(name: str, *keys: str) -> int`
  - `RedisManager.ping() -> bool`
  - `RedisManager.flushdb() -> bool`
  - `RedisManager.close() -> None`
- **Features**:
  - Connection pooling
  - JSON serialization/deserialization
  - Hash operations
  - Key expiration management
  - Health check (ping)

---

## Database Models

### Base Models
- **Path**: `src/models/base.py`
- **Purpose**: Base database configuration and declarative base
- **Status**: ✅ Implemented (100% test coverage)
- **Test Coverage**: 100%
- **Dependencies**: sqlalchemy
- **API**:
  - `DatabaseManager.__init__(database_url: str, echo: bool) -> None`
  - `DatabaseManager.create_tables() -> None`
  - `DatabaseManager.drop_tables() -> None`
  - `DatabaseManager.get_session() -> Session`
- **Features**:
  - SQLAlchemy declarative base
  - Timestamp mixin (created_at, updated_at)
  - Database connection management
  - Session management

### User Model
- **Path**: `src/models/user.py`
- **Purpose**: User authentication and management
- **Status**: ✅ Implemented (100% test coverage)
- **Test Coverage**: 100%
- **Dependencies**: sqlalchemy
- **Fields**: id, username, email, password_hash, is_active, is_superuser, created_at, updated_at
- **Relationships**: digital_humans, tasks
- **Features**:
  - Unique username and email constraints
  - Cascade delete for related records
  - Active/superuser flags

### Digital Human Model
- **Path**: `src/models/digital_human.py`
- **Purpose**: Digital human configuration storage
- **Status**: ✅ Implemented (100% test coverage)
- **Test Coverage**: 100%
- **Dependencies**: sqlalchemy
- **Fields**: id, user_id, name, description, image_path, voice_model_path, video_path, is_active, created_at, updated_at
- **Relationships**: user
- **Features**:
  - Foreign key to user
  - Cascade delete with user
  - Optional media paths

### Task Model
- **Path**: `src/models/task.py`
- **Purpose**: Scheduled task and automation
- **Status**: ✅ Implemented (100% test coverage)
- **Test Coverage**: 100%
- **Dependencies**: sqlalchemy
- **Fields**: id, user_id, name, description, task_type, schedule, params, status, result, error_message, started_at, completed_at, created_at, updated_at
- **Relationships**: user
- **Enums**: TaskStatus (pending, running, completed, failed, cancelled), TaskType (video_generation, voice_synthesis, face_animation, report_generation, batch_processing, custom)
- **Features**:
  - Foreign key to user
  - Cascade delete with user
  - JSON params and result storage
  - Task status tracking

### Database Initialization
- **Path**: `src/models/db_init.py`
- **Purpose**: Database initialization and migration utilities
- **Status**: ✅ Implemented (100% test coverage)
- **Test Coverage**: 100%
- **Dependencies**: alembic
- **API**:
  - `get_alembic_config() -> Config`
  - `init_database(database_url: str) -> None`
  - `create_migration(message: str) -> None`
  - `run_migrations() -> None`
  - `rollback_migration(revision: str) -> None`
- **Features**:
  - Alembic integration
  - Migration creation and execution
  - Database initialization
  - Migration rollback

---

## Digital Human Modules

### Voice Synthesis
- **Path**: `src/models/voice_synthesis.py`
- **Purpose**: Text-to-speech synthesis with multiple backend support
- **Status**: ✅ Implemented (100% test coverage)
- **Test Coverage**: 100%
- **Dependencies**: torch, TTS (optional), pyttsx3 (optional), gTTS (optional)
- **API**:
  - `VoiceSynthesizer.__init__(backend, device, model_path, sample_rate) -> None`
  - `VoiceSynthesizer.synthesize(text, output_path, speaker_wav) -> str`
  - `VoiceSynthesizer.list_available_models() -> list[str]`
  - `VoiceSynthesizer.cleanup() -> None`
- **Features**:
  - Multiple TTS backends (Coqui TTS, pyttsx3, gTTS)
  - Device management (CPU/GPU)
  - Voice cloning support (Coqui TTS)
  - Model caching
  - Automatic temporary file generation

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

2026-02-02 - Phase 1.3 Database & Cache completed with 100% test coverage
- Plugin Manager: ✅ Implemented
- Agent Manager: ✅ Implemented
- Config Manager: ✅ Implemented
- Redis Manager: ✅ Implemented
- Database Models: ✅ Implemented (User, DigitalHuman, Task)
- Database Initialization: ✅ Implemented
