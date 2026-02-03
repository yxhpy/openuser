# Known Issues

This document tracks known issues, limitations, and workarounds for the OpenUser project.

## Type Checking

### Mypy Type Errors

**Issue**: 33 mypy type errors remain in the codebase after initial type checking improvements

**Impact**: Pre-commit hook may fail on mypy check

**Affected Files**:
- `src/models/voice_synthesis.py` (7 errors) - object attribute access issues
- `src/scheduler/tasks.py` (5 errors) - enum type mismatches
- `src/api/scheduler.py` (5 errors) - dict attribute access
- `src/api/auth.py` (3 errors) - None assignment issues
- `src/scheduler/schedule_manager.py` (3 errors) - type mismatches
- `src/api/plugins.py` (3 errors) - None attribute access
- `src/api/digital_human.py` (2 errors) - None attribute access
- `src/integrations/wechat/bot.py` (1 error) - return type mismatch
- `src/integrations/feishu/bot.py` (1 error) - return type mismatch
- `src/models/voice_cloning.py` (1 error) - None assignment
- `src/api/dependencies.py` (1 error) - enum type mismatch
- `src/api/voice.py` (1 error) - None type mismatch
- `src/scheduler/monitor.py` (1 error) - type mismatch

**Workaround**:
- Mypy strict settings have been relaxed in `pyproject.toml`
- Type stubs installed for external libraries
- Remaining errors can be fixed incrementally
- To commit without mypy check: `SKIP=mypy git commit`

**Status**: In progress - reduced from 113 to 33 errors (71% improvement)

**Last Updated**: 2026-02-03

---

## Voice Synthesis Module

### Python Version Compatibility

**Issue**: Coqui TTS requires Python < 3.12

**Impact**: Cannot use Coqui TTS backend with Python 3.12+

**Workaround**:
- Use Python 3.10 or 3.11 for Coqui TTS support
- Or use alternative backends (pyttsx3, gTTS) with Python 3.12+

**Status**: Known limitation, no fix planned

---

### GPU Memory Usage

**Issue**: Coqui TTS models can consume significant GPU memory (2-4GB)

**Impact**: May cause OOM errors on GPUs with limited memory

**Workaround**:
- Use `device="cpu"` for CPU inference
- Reduce batch size
- Use smaller TTS models

**Status**: Expected behavior

---

### gTTS Rate Limiting

**Issue**: Google Text-to-Speech API has rate limits

**Impact**: May fail with too many requests in short time

**Workaround**:
- Implement request throttling
- Use alternative backends for high-volume synthesis
- Cache synthesized audio

**Status**: External service limitation

---

### pyttsx3 Voice Quality

**Issue**: pyttsx3 voices are platform-dependent and may have lower quality

**Impact**: Inconsistent voice quality across platforms

**Workaround**:
- Use Coqui TTS or gTTS for better quality
- Install additional system voices

**Status**: Known limitation

---

## Database

### Migration Conflicts

**Issue**: Alembic migrations may conflict if multiple developers create migrations simultaneously

**Impact**: Migration errors during `alembic upgrade head`

**Workaround**:
- Coordinate migration creation
- Use `alembic merge` to resolve conflicts
- Always pull latest migrations before creating new ones

**Status**: Standard Alembic behavior

---

## Redis

### Connection Pooling

**Issue**: Redis connection pool may exhaust under high load

**Impact**: Connection timeout errors

**Workaround**:
- Increase `max_connections` in Redis configuration
- Implement connection retry logic
- Monitor connection usage

**Status**: Configuration issue

---

## Testing

### Coverage Calculation

**Issue**: Coverage tool may report incorrect coverage for mocked imports

**Impact**: False coverage warnings

**Workaround**:
- Use `sys.modules` mocking before imports
- Verify actual test execution
- Check coverage HTML report for details

**Status**: Known pytest-cov behavior

---

## General

### Virtual Environment

**Issue**: Commands fail if virtual environment is not activated

**Impact**: Module not found errors

**Workaround**:
- Always activate venv: `source venv/bin/activate`
- Add activation to shell profile
- Use absolute paths to venv Python

**Status**: Expected behavior - documented in workflow

---

## Reporting Issues

If you encounter a new issue:

1. Check this document first
2. Search [GitHub Issues](https://github.com/yxhpy/openuser/issues)
3. Create a new issue with:
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)
   - Error messages and logs

## Last Updated

2026-02-02 - Initial version with voice synthesis known issues
