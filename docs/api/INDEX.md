# API Documentation

Complete API reference for OpenUser modules.

## Voice Processing

### Voice Synthesis
- **[Voice Synthesis API](voice-synthesis.md)** - Text-to-speech with multiple backends
  - Coqui TTS (neural TTS with voice cloning)
  - pyttsx3 (offline TTS)
  - gTTS (Google Text-to-Speech)

### Voice Cloning (Coming Soon)
- Voice sample collection
- Voice model training
- Voice profile management

### Audio Processing (Coming Soon)
- Audio preprocessing
- Noise reduction
- Audio normalization

## Core System

### Plugin Management (Coming Soon)
- Plugin installation and removal
- Hot-reload functionality
- Dependency resolution
- Plugin marketplace

### Agent Management (Coming Soon)
- Agent creation and configuration
- Self-update mechanism
- Capability management
- Memory tracking

### Configuration (Coming Soon)
- Dynamic configuration
- Hot-reload
- Environment variables
- Secrets management

## Database

### Models (Coming Soon)
- User model
- Digital Human model
- Task model

### Cache (Coming Soon)
- Redis operations
- Session management
- Key-value storage

## REST API (Coming Soon)

### Digital Human Endpoints
- `POST /api/v1/digital-human/create` - Create digital human
- `POST /api/v1/digital-human/generate` - Generate video
- `GET /api/v1/digital-human/:id` - Get digital human details

### Voice Endpoints
- `POST /api/v1/voice/synthesize` - Synthesize speech
- `POST /api/v1/voice/clone` - Clone voice
- `GET /api/v1/voice/models` - List available models

### Plugin Endpoints
- `GET /api/v1/plugins/list` - List plugins
- `POST /api/v1/plugins/install` - Install plugin
- `POST /api/v1/plugins/reload` - Hot-reload plugin
- `DELETE /api/v1/plugins/:name` - Uninstall plugin

### Agent Endpoints
- `GET /api/v1/agents/list` - List agents
- `POST /api/v1/agents/create` - Create agent
- `PUT /api/v1/agents/:name` - Update agent
- `DELETE /api/v1/agents/:name` - Delete agent

### Scheduler Endpoints
- `POST /api/v1/scheduler/create` - Create scheduled task
- `GET /api/v1/scheduler/list` - List tasks
- `GET /api/v1/scheduler/:id` - Get task details
- `DELETE /api/v1/scheduler/:id` - Cancel task

## WebSocket API (Coming Soon)

### Real-time Endpoints
- `ws://api/v1/voice/stream` - Real-time voice synthesis
- `ws://api/v1/video/stream` - Live video streaming
- `ws://api/v1/agent/chat` - Agent communication

## Authentication (Coming Soon)

### Auth Endpoints
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/refresh` - Refresh token
- `POST /api/v1/auth/logout` - User logout

## Status

✅ **Implemented**: Voice Synthesis API
🚧 **In Progress**: Voice Cloning, Audio Processing
📝 **Planned**: REST API, WebSocket API, Authentication

## Quick Links

- [Module Registry](../modules/REGISTRY.md) - All implemented modules
- [Documentation Index](../INDEX.md) - Main documentation
- [README](../../README.md) - Project overview
