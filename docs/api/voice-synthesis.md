# Voice Synthesis API

API documentation for the voice synthesis module.

## Overview

The voice synthesis module provides text-to-speech (TTS) functionality with support for multiple backends:
- **Coqui TTS**: High-quality neural TTS with voice cloning
- **pyttsx3**: Offline TTS engine
- **gTTS**: Google Text-to-Speech API

## Installation

```bash
# Install with TTS support
pip install -e ".[dev]"

# Optional: Install specific TTS backends
pip install TTS  # Coqui TTS (requires Python < 3.12)
pip install pyttsx3  # Offline TTS
pip install gTTS  # Google TTS
```

## Basic Usage

### Initialize Synthesizer

```python
from src.models.voice_synthesis import VoiceSynthesizer, TTSBackend

# Using Coqui TTS (default)
synth = VoiceSynthesizer(
    backend=TTSBackend.COQUI,
    device="cuda",  # or "cpu"
    sample_rate=22050
)

# Using pyttsx3 (offline)
synth = VoiceSynthesizer(
    backend=TTSBackend.PYTTSX3
)

# Using gTTS (online)
synth = VoiceSynthesizer(
    backend=TTSBackend.GTTS
)
```

### Synthesize Speech

```python
# Basic synthesis
audio_path = synth.synthesize(
    text="Hello, world!",
    output_path="/path/to/output.wav"
)

# Auto-generate temporary file
audio_path = synth.synthesize(text="Hello, world!")
print(f"Audio saved to: {audio_path}")
```

### Voice Cloning (Coqui TTS only)

```python
# Clone voice from speaker sample
audio_path = synth.synthesize(
    text="This is my cloned voice",
    output_path="/path/to/output.wav",
    speaker_wav="/path/to/speaker_sample.wav"
)
```

### Custom Model

```python
# Use custom Coqui TTS model
synth = VoiceSynthesizer(
    backend=TTSBackend.COQUI,
    model_path="/path/to/custom/model",
    device="cuda"
)
```

### List Available Models

```python
# List available models for current backend
models = synth.list_available_models()
for model in models:
    print(model)
```

### Cleanup

```python
# Clean up resources
synth.cleanup()
```

## API Reference

### VoiceSynthesizer

#### `__init__(backend, device, model_path, sample_rate)`

Initialize voice synthesizer.

**Parameters:**
- `backend` (TTSBackend): TTS backend to use (COQUI, PYTTSX3, GTTS)
- `device` (str): Device for inference ("cpu" or "cuda"). Default: "cpu"
- `model_path` (str, optional): Path to custom TTS model (Coqui only)
- `sample_rate` (int): Audio sample rate. Default: 22050

**Raises:**
- `ValueError`: If backend is not supported
- `RuntimeError`: If model initialization fails

#### `synthesize(text, output_path, speaker_wav)`

Synthesize speech from text.

**Parameters:**
- `text` (str): Text to synthesize
- `output_path` (str, optional): Path to save audio file. If None, creates temp file
- `speaker_wav` (str, optional): Path to speaker audio for voice cloning (Coqui only)

**Returns:**
- `str`: Path to generated audio file

**Raises:**
- `ValueError`: If text is empty
- `RuntimeError`: If synthesis fails

**Example:**
```python
audio_path = synth.synthesize(
    text="Hello, world!",
    output_path="/tmp/output.wav"
)
```

#### `list_available_models()`

List available TTS models for the current backend.

**Returns:**
- `list[str]`: List of available model names

**Raises:**
- `RuntimeError`: If backend doesn't support model listing

**Example:**
```python
models = synth.list_available_models()
print(f"Available models: {models}")
```

#### `cleanup()`

Clean up resources and stop engines.

**Example:**
```python
synth.cleanup()
```

### TTSBackend

Enum of supported TTS backends.

**Values:**
- `COQUI`: Coqui TTS (neural TTS with voice cloning)
- `PYTTSX3`: pyttsx3 (offline TTS)
- `GTTS`: gTTS (Google Text-to-Speech)

## Advanced Usage

### Context Manager

```python
from src.models.voice_synthesis import VoiceSynthesizer, TTSBackend

# Use as context manager (auto cleanup)
with VoiceSynthesizer(backend=TTSBackend.COQUI) as synth:
    audio = synth.synthesize("Hello!")
# Automatically cleaned up
```

### Batch Processing

```python
texts = [
    "First sentence",
    "Second sentence",
    "Third sentence"
]

synth = VoiceSynthesizer(backend=TTSBackend.COQUI, device="cuda")

audio_files = []
for i, text in enumerate(texts):
    audio_path = synth.synthesize(
        text=text,
        output_path=f"/tmp/audio_{i}.wav"
    )
    audio_files.append(audio_path)

synth.cleanup()
```

### Error Handling

```python
from src.models.voice_synthesis import VoiceSynthesizer, TTSBackend

try:
    synth = VoiceSynthesizer(backend=TTSBackend.COQUI)
    audio = synth.synthesize("Hello, world!")
except ValueError as e:
    print(f"Invalid input: {e}")
except RuntimeError as e:
    print(f"Synthesis failed: {e}")
finally:
    synth.cleanup()
```

## Performance Tips

1. **Use GPU**: Set `device="cuda"` for faster synthesis with Coqui TTS
2. **Reuse Synthesizer**: Create one instance and reuse for multiple syntheses
3. **Choose Backend**:
   - Coqui TTS: Best quality, supports voice cloning, requires GPU for speed
   - pyttsx3: Fast, offline, lower quality
   - gTTS: Good quality, requires internet, rate limited

## Limitations

- **Coqui TTS**: Requires Python < 3.12, GPU recommended for real-time
- **pyttsx3**: Limited voice options, platform-dependent
- **gTTS**: Requires internet connection, rate limited by Google

## See Also

- [Module Registry](../modules/REGISTRY.md#voice-synthesis)
- [Voice Cloning Guide](voice-cloning.md) (coming soon)
- [Audio Preprocessing](audio-preprocessing.md) (coming soon)
