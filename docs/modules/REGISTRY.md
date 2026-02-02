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
- **Dependencies**: plugin_config, plugin_dependency
- **API**:
  - `PluginManager.load_plugin(name: str) -> Plugin`
  - `PluginManager.reload_plugin(name: str) -> bool`
  - `PluginManager.unload_plugin(name: str) -> bool`
  - `PluginManager.list_plugins() -> List[Plugin]`
  - `PluginManager.get_plugin(name: str) -> Optional[Plugin]`
  - `PluginManager.check_dependencies(name: str) -> tuple[bool, List[str]]`
  - `PluginManager.get_load_order() -> tuple[bool, List[str], List[str]]`
  - `PluginManager.get_dependency_tree(name: str) -> Dict[str, List[str]]`
- **Features**:
  - Hot-reload plugins without restart
  - State backup and rollback
  - Plugin lifecycle hooks (on_load, on_unload)
  - Error handling and recovery
  - Dependency resolution and validation
  - Automatic load order determination
  - Version constraint checking

### Plugin Configuration
- **Path**: `src/core/plugin_config.py`
- **Purpose**: Configuration schema and management for plugins
- **Status**: ✅ Implemented (100% test coverage)
- **Test Coverage**: 100%
- **Dependencies**: None
- **API**:
  - `ConfigField` - Configuration field definition with type and validation
  - `PluginConfigSchema` - Schema definition for plugin configuration
  - `PluginConfig` - Configuration manager with hot-reload
  - `PluginConfig.get(key: str, default: Any) -> Any`
  - `PluginConfig.set(key: str, value: Any) -> None`
  - `PluginConfig.reload() -> bool`
  - `PluginConfig.save(format: str) -> bool`
  - `PluginConfig.validate() -> tuple[bool, List[str]]`
- **Features**:
  - Type-safe configuration fields (string, integer, float, boolean, list, dict)
  - Required and optional fields
  - Default values
  - Custom validators
  - JSON and YAML file support
  - Hot-reload configuration
  - Validation with error messages

### Plugin Dependency Management
- **Path**: `src/core/plugin_dependency.py`
- **Purpose**: Dependency resolution and version management for plugins
- **Status**: ✅ Implemented (99% test coverage)
- **Test Coverage**: 99%
- **Dependencies**: None
- **API**:
  - `PluginDependency.parse(dep_string: str) -> PluginDependency`
  - `PluginDependency.check_version(version: str) -> bool`
  - `DependencyResolver.add_plugin(name: str, version: str, dependencies: List[str]) -> None`
  - `DependencyResolver.check_dependencies(plugin_name: str) -> tuple[bool, List[str]]`
  - `DependencyResolver.resolve_load_order() -> tuple[bool, List[str], List[str]]`
  - `DependencyResolver.get_dependency_tree(plugin_name: str) -> Dict[str, List[str]]`
- **Features**:
  - Semantic version parsing and comparison
  - Version constraints (==, >=, <=, >, <)
  - Dependency validation
  - Topological sort for load order
  - Circular dependency detection
  - Dependency tree visualization
  - Missing dependency detection

### Plugin Registry
- **Path**: `src/core/plugin_registry.py`
- **Purpose**: Plugin discovery, search, and management system
- **Status**: ✅ Implemented (100% test coverage)
- **Test Coverage**: 100%
- **Dependencies**: requests
- **API**:
  - `PluginRegistry.register(metadata: PluginMetadata) -> None`
  - `PluginRegistry.unregister(name: str) -> bool`
  - `PluginRegistry.get(name: str) -> Optional[PluginMetadata]`
  - `PluginRegistry.list_all() -> List[PluginMetadata]`
  - `PluginRegistry.search(query, tags, author) -> List[PluginMetadata]`
  - `PluginRegistry.sync_from_remote(remote_url, merge) -> tuple[bool, str]`
  - `PluginRegistry.check_updates(remote_url) -> List[tuple[str, str, str]]`
  - `PluginRegistry.export_to_file(output_path) -> None`
  - `PluginRegistry.import_from_file(input_path, merge) -> tuple[bool, str]`
  - `PluginRegistry.get_stats() -> Dict[str, Any]`
  - `PluginMetadata` - Plugin metadata dataclass
- **Features**:
  - Local plugin registry with JSON persistence
  - Plugin metadata management (name, version, description, author, tags, etc.)
  - Search and discovery (by query, tags, author)
  - Remote registry synchronization (merge or replace)
  - Auto-update checking with semantic versioning
  - Import/export registry to files
  - Registry statistics (plugins by author, by tag)
  - Version comparison and update detection
  - Corrupted registry recovery

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
- **Purpose**: Voice profile management and voice cloning pipeline
- **Status**: ✅ Implemented (100% test coverage)
- **Test Coverage**: 100%
- **Dependencies**: torch, numpy
- **API**:
  - `VoiceCloner.__init__(profile_dir, device, min_samples, sample_rate) -> None`
  - `VoiceCloner.validate_audio_samples(sample_paths) -> bool`
  - `VoiceCloner.create_profile(name, sample_paths, description, metadata) -> VoiceProfile`
  - `VoiceCloner.save_profile(profile) -> None`
  - `VoiceCloner.load_profile(name) -> VoiceProfile`
  - `VoiceCloner.list_profiles() -> List[str]`
  - `VoiceCloner.delete_profile(name) -> bool`
  - `VoiceCloner.update_profile(name, description, sample_paths, metadata) -> VoiceProfile`
  - `VoiceCloner.get_profile_info(name) -> Dict[str, Any]`
- **Features**:
  - Voice profile creation and management
  - Multi-sample voice validation
  - Profile persistence (JSON)
  - Metadata support
  - Audio format validation (.wav, .mp3, .flac, .ogg)
  - Device management (CPU/GPU)

### Audio Preprocessing
- **Path**: `src/models/audio_preprocessing.py`
- **Purpose**: Audio preprocessing and enhancement for voice processing
- **Status**: ✅ Implemented (100% test coverage)
- **Test Coverage**: 100%
- **Dependencies**: librosa, soundfile, numpy, noisereduce (optional)
- **API**:
  - `AudioPreprocessor.__init__(sample_rate, device, normalize) -> None`
  - `AudioPreprocessor.load_audio(audio_path) -> Tuple[np.ndarray, int]`
  - `AudioPreprocessor.convert_sample_rate(audio_data, original_sr, target_sr) -> np.ndarray`
  - `AudioPreprocessor.normalize_audio(audio_data, target_db) -> np.ndarray`
  - `AudioPreprocessor.trim_silence(audio_data, threshold_db, frame_length) -> np.ndarray`
  - `AudioPreprocessor.reduce_noise(audio_data, sr, noise_reduce_strength) -> np.ndarray`
  - `AudioPreprocessor.save_audio(audio_data, output_path, sr) -> str`
  - `AudioPreprocessor.convert_format(input_path, output_path, target_format) -> str`
  - `AudioPreprocessor.validate_audio_quality(audio_data, sr) -> Dict[str, Any]`
  - `AudioPreprocessor.preprocess(input_path, output_path, ...) -> Tuple[str, Dict]`
- **Features**:
  - Audio format conversion (wav, mp3, flac, ogg)
  - Sample rate conversion
  - Audio normalization to target dB
  - Silence trimming
  - Noise reduction (optional)
  - Audio quality validation
  - Full preprocessing pipeline
  - Device management (CPU/GPU)

### Wav2Lip Integration
- **Path**: `src/models/wav2lip.py`
- **Purpose**: Lip-sync video generation using Wav2Lip model
- **Status**: ✅ Implemented (100% test coverage)
- **Test Coverage**: 100%
- **Dependencies**: torch, opencv-python, numpy
- **API**:
  - `Wav2LipModel.__init__(device, model_path, face_det_batch_size, wav2lip_batch_size, fps, resize_factor) -> None`
  - `Wav2LipModel.detect_faces(image) -> list[Tuple[int, int, int, int]]`
  - `Wav2LipModel.preprocess_image(image_path) -> Tuple[np.ndarray, list[Tuple[int, int, int, int]]]`
  - `Wav2LipModel.generate_video(face_path, audio_path, output_path) -> str`
  - `Wav2LipModel.cleanup() -> None`
- **Features**:
  - Lip-sync video generation from images or videos
  - Face detection and preprocessing
  - Video frame extraction and processing
  - Audio-video synchronization
  - Device management (CPU/GPU)
  - Lazy model loading
  - Automatic output path generation
  - Resource cleanup

### GFPGAN Integration
- **Path**: `src/models/gfpgan.py`
- **Purpose**: Face enhancement using GFPGAN model
- **Status**: ✅ Implemented (100% test coverage)
- **Test Coverage**: 100%
- **Dependencies**: torch, opencv-python, numpy
- **API**:
  - `GFPGANModel.__init__(device, model_path, upscale_factor, bg_upsampler, face_size) -> None`
  - `GFPGANModel.detect_faces(image) -> list[Tuple[int, int, int, int]]`
  - `GFPGANModel.enhance_face(image_path, output_path) -> str`
  - `GFPGANModel.enhance_video(video_path, output_path, fps) -> str`
  - `GFPGANModel.cleanup() -> None`
- **Features**:
  - Face enhancement for images and videos
  - Face detection and preprocessing
  - Configurable upscaling (1-4x)
  - Optional background upsampler support
  - Device management (CPU/GPU)
  - Lazy model loading
  - Automatic output path generation
  - Resource cleanup

### SadTalker Integration
- **Path**: `src/models/sadtalker.py`
- **Purpose**: Talking head generation using SadTalker model
- **Status**: ✅ Implemented (100% test coverage)
- **Test Coverage**: 100%
- **Dependencies**: torch, opencv-python, numpy
- **API**:
  - `SadTalkerModel.__init__(device, model_path, fps, still_mode, preprocess, expression_scale) -> None`
  - `SadTalkerModel.detect_faces(image) -> list[Tuple[int, int, int, int]]`
  - `SadTalkerModel.preprocess_image(image_path) -> Tuple[np.ndarray, list[Tuple[int, int, int, int]]]`
  - `SadTalkerModel.generate_video(image_path, audio_path, output_path) -> str`
  - `SadTalkerModel.cleanup() -> None`
- **Features**:
  - Talking head video generation from static images
  - Face detection and preprocessing
  - Configurable FPS and expression scale
  - Still mode for less head movement
  - Multiple preprocessing methods (crop, resize, full)
  - Device management (CPU/GPU)
  - Lazy model loading
  - Automatic output path generation
  - Resource cleanup

### Video Generation Pipeline
- **Path**: `src/models/video_generator.py`
- **Purpose**: Unified pipeline integrating all digital human components
- **Status**: ✅ Implemented (100% test coverage)
- **Test Coverage**: 100%
- **Dependencies**: VoiceSynthesizer, Wav2LipModel, GFPGANModel, SadTalkerModel
- **API**:
  - `VideoGenerator.__init__(device, mode, voice_config, wav2lip_config, gfpgan_config, sadtalker_config) -> None`
  - `VideoGenerator.generate_from_text(text, image_path, output_path, speaker_wav) -> str`
  - `VideoGenerator.generate_from_audio(image_path, audio_path, output_path) -> str`
  - `VideoGenerator.cleanup() -> None`
- **Generation Modes**:
  - `LIPSYNC`: Wav2Lip only
  - `TALKING_HEAD`: SadTalker only
  - `ENHANCED_LIPSYNC`: Wav2Lip + GFPGAN
  - `ENHANCED_TALKING_HEAD`: SadTalker + GFPGAN
- **Features**:
  - Text-to-video generation
  - Audio-to-video generation
  - Multiple generation modes
  - Component orchestration
  - Automatic cleanup
  - Configurable pipeline stages

### Model Manager
- **Path**: `src/models/model_manager.py`
- **Purpose**: Centralized model management with caching and device management
- **Status**: ✅ Implemented (100% test coverage)
- **Test Coverage**: 100%
- **Dependencies**: torch
- **API**:
  - `ModelManager.__init__(cache_dir, device, max_cache_size_gb) -> None`
  - `ModelManager.register_model(model_info) -> None`
  - `ModelManager.get_model_path(name, version) -> Optional[Path]`
  - `ModelManager.is_model_cached(name, version) -> bool`
  - `ModelManager.list_models() -> List[ModelInfo]`
  - `ModelManager.get_model_info(name, version) -> Optional[ModelInfo]`
  - `ModelManager.delete_model(name, version) -> bool`
  - `ModelManager.get_device() -> str`
  - `ModelManager.set_device(device) -> None`
  - `ModelManager.get_device_info() -> Dict[str, Any]`
  - `ModelManager.clear_cache() -> None`
  - `ModelManager.get_cache_stats() -> Dict[str, Any]`
  - `ModelInfo.to_dict() -> Dict[str, Any]`
  - `ModelInfo.from_dict(data) -> ModelInfo`
- **Features**:
  - Model registry with versioning
  - Model caching with size limits
  - LRU cache cleanup (removes oldest models first)
  - GPU/CPU device management
  - Device information (CUDA memory, device count)
  - SHA256 checksum calculation
  - Cache statistics
  - Model metadata (name, version, URL, size, dependencies)

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
- **Purpose**: Main FastAPI application with CORS and routing
- **Status**: ✅ Implemented (100% test coverage)
- **Test Coverage**: 100%
- **Dependencies**: fastapi, voice endpoints
- **API**:
  - `GET /` - Root endpoint with API info
  - `GET /health` - Health check endpoint
  - `GET /docs` - OpenAPI documentation
  - `GET /redoc` - ReDoc documentation
- **Features**:
  - CORS middleware configuration
  - Router registration
  - OpenAPI documentation
  - Health check endpoint

### Voice API
- **Path**: `src/api/voice.py`
- **Purpose**: Voice synthesis and cloning REST API endpoints
- **Status**: ✅ Implemented (100% test coverage)
- **Test Coverage**: 100%
- **Dependencies**: VoiceSynthesizer, VoiceCloner
- **API**:
  - `POST /api/v1/voice/synthesize` - Synthesize speech from text
  - `POST /api/v1/voice/profiles` - Create voice profile
  - `GET /api/v1/voice/profiles` - List all voice profiles
  - `GET /api/v1/voice/profiles/{name}` - Get profile information
  - `DELETE /api/v1/voice/profiles/{name}` - Delete voice profile
- **Features**:
  - Real-time voice synthesis
  - Multiple TTS backend support (Coqui, pyttsx3, gTTS)
  - Voice profile management
  - Error handling and validation
  - Pydantic request/response models

### API Schemas
- **Path**: `src/api/schemas.py`
- **Purpose**: Pydantic models for API request/response validation
- **Status**: ✅ Implemented (100% test coverage)
- **Test Coverage**: 100%
- **Dependencies**: pydantic
- **Models**:
  - `VoiceSynthesizeRequest` - Voice synthesis request
  - `VoiceSynthesizeResponse` - Voice synthesis response
  - `VoiceProfileCreateRequest` - Profile creation request
  - `VoiceProfileResponse` - Profile information response
  - `VoiceProfileListResponse` - Profile list response
  - `ErrorResponse` - Error response
- **Features**:
  - Field validation
  - Type checking
  - Custom validators
  - Documentation strings

### API Dependencies
- **Path**: `src/api/dependencies.py`
- **Purpose**: Dependency injection for FastAPI endpoints
- **Status**: ✅ Implemented (100% test coverage)
- **Test Coverage**: 100%
- **Dependencies**: VoiceSynthesizer, VoiceCloner
- **API**:
  - `get_voice_synthesizer()` - Get or create VoiceSynthesizer instance
  - `get_voice_cloner()` - Get or create VoiceCloner instance
- **Features**:
  - LRU caching for instance reuse
  - Configurable parameters
  - Default value handling

### Authentication
- **Path**: `src/api/auth.py`
- **Purpose**: JWT-based authentication system
- **Status**: ✅ Implemented (100% test coverage)
- **Test Coverage**: 95%+
- **Dependencies**: python-jose, passlib, argon2-cffi, email-validator
- **API**:
  - `POST /api/v1/auth/register` - Register new user
  - `POST /api/v1/auth/login` - Login and get tokens
  - `POST /api/v1/auth/refresh` - Refresh access token
  - `GET /api/v1/auth/me` - Get current user info
- **Features**:
  - JWT access and refresh tokens
  - Argon2 password hashing
  - Email validation
  - Password strength validation
  - OAuth2 bearer token authentication
  - User registration and login
  - Token refresh mechanism
  - Protected route dependencies

### Authentication Utilities
- **Path**: `src/api/auth_utils.py`
- **Purpose**: JWT token management and password hashing utilities
- **Status**: ✅ Implemented (100% test coverage)
- **Test Coverage**: 100%
- **Dependencies**: python-jose, passlib, argon2-cffi
- **API**:
  - `verify_password(plain_password: str, hashed_password: str) -> bool`
  - `get_password_hash(password: str) -> str`
  - `create_access_token(data: dict, expires_delta: Optional[timedelta]) -> str`
  - `create_refresh_token(data: dict) -> str`
  - `decode_token(token: str) -> Optional[dict]`
- **Features**:
  - Argon2 password hashing (Python 3.13 compatible)
  - JWT token creation and validation
  - Configurable token expiration
  - Timezone-aware datetime handling

### Digital Human API
- **Path**: `src/api/digital_human.py`
- **Purpose**: REST API endpoints for digital human management and video generation
- **Status**: ✅ Implemented (100% test coverage)
- **Test Coverage**: 100%
- **Dependencies**: DigitalHuman model, VideoGenerator, authentication
- **API**:
  - `POST /api/v1/digital-human/create` - Create new digital human with image upload
  - `POST /api/v1/digital-human/generate` - Generate video from text or audio
  - `GET /api/v1/digital-human/list` - List all digital humans for current user
  - `GET /api/v1/digital-human/{id}` - Get digital human details
  - `DELETE /api/v1/digital-human/{id}` - Delete digital human and associated files
- **Features**:
  - File upload handling for images and audio
  - Multiple video generation modes (lipsync, talking_head, enhanced_lipsync, enhanced_talking_head)
  - Text-to-video and audio-to-video generation
  - Authentication and authorization
  - File cleanup on deletion
  - Comprehensive error handling

### Plugin API
- **Path**: `src/api/plugins.py`
- **Purpose**: REST API endpoints for plugin management
- **Status**: ✅ Implemented (100% test coverage)
- **Test Coverage**: 100%
- **Dependencies**: PluginManager, authentication
- **API**:
  - `GET /api/v1/plugins/list` - List all loaded plugins
  - `POST /api/v1/plugins/install` - Install a new plugin
  - `POST /api/v1/plugins/reload` - Hot-reload a plugin without restart
- **Features**:
  - Plugin listing with version and dependency information
  - Plugin installation with validation
  - Hot-reload capability without system restart
  - Authentication and authorization
  - Comprehensive error handling

### Agent API
- **Path**: `src/api/agents.py`
- **Purpose**: REST API endpoints for AI agent management
- **Status**: ✅ Implemented (100% test coverage)
- **Test Coverage**: 100%
- **Dependencies**: AgentManager, authentication
- **API**:
  - `POST /api/v1/agents/create` - Create new agent
  - `GET /api/v1/agents/list` - List all agents
  - `GET /api/v1/agents/{name}` - Get agent details
  - `PUT /api/v1/agents/{name}` - Update agent
  - `DELETE /api/v1/agents/{name}` - Delete agent
- **Features**:
  - Agent lifecycle management (CRUD operations)
  - System prompt and capabilities management
  - Authentication and authorization
  - Comprehensive error handling
  - Exception handling for all operations

### Scheduler API
- **Path**: `src/api/scheduler.py`
- **Purpose**: REST API endpoints for task scheduling and management
- **Status**: ✅ Implemented (100% test coverage)
- **Test Coverage**: 100%
- **Dependencies**: Task model, authentication, database
- **API**:
  - `POST /api/v1/scheduler/create` - Create new scheduled task
  - `GET /api/v1/scheduler/list` - List all tasks (with filters)
  - `GET /api/v1/scheduler/{task_id}` - Get task details
  - `PUT /api/v1/scheduler/{task_id}` - Update task
  - `DELETE /api/v1/scheduler/{task_id}` - Delete task
- **Features**:
  - Full CRUD operations for task management
  - Task filtering by status and type
  - Cron schedule support
  - Task parameters and results storage (JSON)
  - Task status tracking (pending, running, completed, failed, cancelled)
  - Task types (video_generation, voice_synthesis, face_animation, etc.)
  - Authentication and authorization
  - Comprehensive error handling

### WebSocket API
- **Path**: `src/api/websocket.py`
- **Purpose**: Real-time bidirectional communication via WebSocket
- **Status**: ✅ Implemented (95% test coverage)
- **Test Coverage**: 95%
- **Dependencies**: FastAPI WebSocket, authentication
- **API**:
  - `WS /api/v1/ws/progress` - Real-time progress updates for tasks
  - `WS /api/v1/ws/agent` - Agent communication channel
  - `GET /api/v1/ws/connections` - Connection statistics
- **Features**:
  - Connection management with user authentication
  - Task progress subscription and broadcasting
  - Agent bidirectional communication
  - Automatic connection cleanup
  - Ping/pong heartbeat support
  - JWT token authentication for WebSocket connections
  - Connection statistics endpoint

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

### Cache Manager Plugin
- **Path**: `src/plugins/cache_manager.py`
- **Purpose**: Cache management utilities with TTL and size limits
- **Status**: ✅ Implemented (94% test coverage)
- **Test Coverage**: 94%
- **Dependencies**: None
- **API**:
  - `CacheManager.set(key, value, ttl) -> bool`
  - `CacheManager.get(key) -> Optional[Any]`
  - `CacheManager.delete(key) -> bool`
  - `CacheManager.exists(key) -> bool`
  - `CacheManager.clear() -> int`
  - `CacheManager.cleanup_expired() -> int`
  - `CacheManager.get_size() -> int`
  - `CacheManager.get_stats() -> Dict[str, Any]`
  - `CacheManager.enforce_size_limit() -> int`
- **Configuration**:
  - `cache_dir` (string, default: "cache") - Cache storage directory
  - `max_size_mb` (integer, default: 1024) - Maximum cache size in MB
  - `default_ttl` (integer, default: 3600) - Default TTL in seconds
- **Features**:
  - Key-value cache with JSON serialization
  - TTL (Time To Live) support with automatic expiration
  - Cache size management with LRU eviction
  - Cache statistics (hits, misses, hit rate)
  - Cleanup expired entries
  - Enforce size limits
  - SHA256 key hashing
  - Configuration schema with validation

### Image Processor Plugin
- **Path**: `src/plugins/image_processor.py`
- **Purpose**: Image preprocessing and enhancement capabilities
- **Status**: ✅ Implemented (100% test coverage)
- **Test Coverage**: 100%
- **Dependencies**: PIL (Pillow)
- **API**:
  - `ImageProcessor.resize(input_path, output_path, size, keep_aspect_ratio) -> str`
  - `ImageProcessor.crop(input_path, output_path, box) -> str`
  - `ImageProcessor.enhance(input_path, output_path, brightness, contrast, sharpness, color) -> str`
  - `ImageProcessor.convert_format(input_path, output_path, format) -> str`
  - `ImageProcessor.apply_filter(input_path, output_path, filter_type) -> str`
  - `ImageProcessor.get_stats() -> dict`
- **Configuration**:
  - `default_format` (string, default: "PNG") - Default output format
  - `default_quality` (integer, default: 95) - JPEG quality (1-100)
  - `max_size` (integer, default: 4096) - Maximum image dimension
- **Features**:
  - Resize images with/without aspect ratio preservation
  - Crop images to specified dimensions
  - Enhance brightness, contrast, sharpness, and color
  - Convert between image formats (PNG, JPEG, etc.)
  - Apply filters (BLUR, SHARPEN, SMOOTH, EDGE_ENHANCE)
  - Automatic RGBA to RGB conversion for JPEG
  - Configuration schema with validation
  - Processing statistics tracking

### Image Processor
- **Path**: `src/plugins/image_processor.py`
- **Purpose**: Image preprocessing and enhancement
- **Status**: 📝 Planned
- **Test Coverage**: N/A
- **Dependencies**: PIL, OpenCV
- **API**:
  - `ImageProcessor.resize(image: str, size: tuple) -> str`
  - `ImageProcessor.enhance(image: str) -> str`

### Video Editor Plugin
- **Path**: `src/plugins/video_editor.py`
- **Purpose**: Video editing utilities using ffmpeg
- **Status**: ✅ Implemented (100% test coverage)
- **Test Coverage**: 100%
- **Dependencies**: ffmpeg (external)
- **API**:
  - `VideoEditor.trim(input_path, output_path, start, end, duration) -> str`
  - `VideoEditor.concat(input_paths, output_path, method) -> str`
  - `VideoEditor.convert_format(input_path, output_path, codec, audio_codec, quality, fps) -> str`
  - `VideoEditor.extract_audio(input_path, output_path, audio_codec) -> str`
  - `VideoEditor.add_audio(video_path, audio_path, output_path, replace) -> str`
  - `VideoEditor.get_video_info(video_path) -> Optional[dict]`
  - `VideoEditor.get_stats() -> dict`
- **Configuration**:
  - `ffmpeg_path` (string, default: "ffmpeg") - Path to ffmpeg executable
  - `default_codec` (string, default: "libx264") - Default video codec
  - `default_audio_codec` (string, default: "aac") - Default audio codec
  - `default_quality` (integer, default: 23) - Default CRF quality (0-51, lower is better)
  - `default_fps` (integer, default: 30) - Default frames per second
- **Features**:
  - Trim videos to specified time ranges
  - Concatenate multiple videos (filter or demuxer method)
  - Convert video formats and codecs
  - Extract audio from videos
  - Add or replace audio in videos
  - Get video information using ffprobe
  - Processing statistics tracking
  - Configuration schema with validation
  - Comprehensive error handling

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
- **Status**: ✅ Implemented (99% test coverage)
- **Test Coverage**: 99%
- **Dependencies**: AudioPreprocessor
- **API**:
  - `AudioEnhancer.denoise(input_path, output_path, strength) -> str`
  - `AudioEnhancer.normalize(input_path, output_path, target_db) -> str`
  - `AudioEnhancer.enhance(input_path, output_path, denoise, normalize, trim_silence, noise_strength, target_db) -> Dict[str, Any]`
  - `AudioEnhancer.get_stats() -> Dict[str, Any]`
- **Configuration**:
  - `sample_rate` (integer, default: 22050) - Target sample rate for audio processing
  - `normalize` (boolean, default: true) - Whether to normalize audio by default
  - `noise_reduce_strength` (float, default: 0.5) - Default noise reduction strength (0.0 to 1.0)
- **Features**:
  - Audio denoising with configurable strength
  - Audio normalization to target dB level
  - Full audio enhancement pipeline (denoise + normalize + trim silence)
  - Processing statistics tracking
  - Configuration schema with validation
  - Automatic output path generation

### Model Downloader Plugin
- **Path**: `src/plugins/model_downloader.py`
- **Purpose**: Auto-download AI models with progress tracking and verification
- **Status**: ✅ Implemented (100% test coverage)
- **Test Coverage**: 100%
- **Dependencies**: requests, tqdm
- **API**:
  - `ModelDownloader.download(url, output_path, checksum, progress_callback) -> str`
  - `ModelDownloader.download_with_progress(url, output_path, checksum) -> str`
  - `ModelDownloader.list_models() -> List[Dict[str, Any]]`
  - `ModelDownloader.delete_model(name) -> bool`
  - `ModelDownloader.get_model_path(name) -> Optional[str]`
  - `ModelDownloader.get_stats() -> Dict[str, Any]`
- **Configuration**:
  - `download_dir` (string, default: "models") - Directory to store downloaded models
  - `chunk_size` (integer, default: 8192) - Download chunk size in bytes
  - `verify_checksum` (boolean, default: true) - Verify file checksum after download
  - `timeout` (integer, default: 300) - Download timeout in seconds
- **Features**:
  - Download models from URLs with progress tracking
  - SHA256 checksum verification
  - Resume downloads (skip if file exists with valid checksum)
  - Progress bar support with tqdm
  - Model listing and management
  - Download statistics tracking
  - Automatic directory creation
  - Error handling and cleanup

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

2026-02-03 - Phase 4.3 Plugin Registry completed
- Plugin Manager: ✅ Implemented
- Agent Manager: ✅ Implemented
- Config Manager: ✅ Implemented
- Redis Manager: ✅ Implemented
- Database Models: ✅ Implemented (User, DigitalHuman, Task)
- Database Initialization: ✅ Implemented
- Voice Synthesis: ✅ Implemented
- Voice Cloning: ✅ Implemented
- Audio Preprocessing: ✅ Implemented
- Voice API: ✅ Implemented (Real-time synthesis endpoints)
- FastAPI Application: ✅ Implemented
- Wav2Lip Integration: ✅ Implemented (Lip-sync video generation)
- GFPGAN Integration: ✅ Implemented (Face enhancement)
- SadTalker Integration: ✅ Implemented (Talking head generation)
- Video Generation Pipeline: ✅ Implemented (Unified digital human pipeline)
- Model Manager: ✅ Implemented (Model caching, versioning, device management)
- Authentication System: ✅ Implemented (JWT auth, user registration, login, token refresh)
- Authentication Utilities: ✅ Implemented (Password hashing, JWT token management)
- Digital Human API: ✅ Implemented (Create, generate, list, get, delete endpoints with 100% test coverage)
- Plugin API: ✅ Implemented (List, install, reload endpoints with 100% test coverage)
- Agent API: ✅ Implemented (Create, list, get, update, delete endpoints with 100% test coverage)
- Scheduler API: ✅ Implemented (Create, list, get, update, delete endpoints with 100% test coverage)
- WebSocket API: ✅ Implemented (Real-time progress updates, agent communication with 95% test coverage)
- Cache Manager Plugin: ✅ Implemented (Cache management with TTL and size limits, 94% test coverage)
- Image Processor Plugin: ✅ Implemented (Image preprocessing and enhancement, 100% test coverage)
- Video Editor Plugin: ✅ Implemented (Video editing utilities with ffmpeg, 100% test coverage)
- Audio Enhancer Plugin: ✅ Implemented (Audio enhancement and noise reduction, 99% test coverage)
- Model Downloader Plugin: ✅ Implemented (Auto-download models with progress tracking and verification, 100% test coverage)
- **Plugin Registry: ✅ Implemented (Plugin discovery, search, and management with remote sync, 100% test coverage)**

