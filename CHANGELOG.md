# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Voice synthesis module with multiple TTS backend support (Coqui TTS, pyttsx3, gTTS)
- Device management (CPU/GPU) with automatic detection
- Voice cloning support via speaker wav files
- Model caching and management
- Comprehensive test suite with 100% coverage

## [0.1.0] - 2026-02-02

### Added
- Initial project setup with Python 3.10+ support
- Hot-reloadable plugin system with dependency resolution
- AI agent manager with self-update capability
- Dynamic configuration manager with hot-reload
- Redis cache manager with connection pooling
- PostgreSQL database models (User, DigitalHuman, Task)
- Alembic database migrations
- Comprehensive test suite with 100% coverage requirement
- Project documentation structure
- Claude Code integration for AI-assisted development

### Infrastructure
- pytest with coverage reporting
- pre-commit hooks
- Black code formatting
- flake8 linting
- mypy type checking
- GitHub repository setup

[Unreleased]: https://github.com/yxhpy/openuser/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yxhpy/openuser/releases/tag/v0.1.0
