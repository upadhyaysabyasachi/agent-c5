# Installation Guide

## Quick Start

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install System Dependencies (for Audio Playback)

#### macOS

```bash
# Install PortAudio (required for pyaudio)
brew install portaudio

# Then install pyaudio
pip install pyaudio
```

**Alternative (Easier)**: Use `sounddevice` instead of `pyaudio`:

```bash
pip install sounddevice
```

#### Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio
```

#### Linux (Fedora)

```bash
sudo dnf install portaudio-devel
pip install pyaudio
```

#### Windows

```bash
# pyaudio should work directly, but if you get errors:
# Download and install PortAudio from: http://files.portaudio.com/download.html
pip install pyaudio
```

### 3. Set Up Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```bash
GROQ_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
SUPABASE_URL=your_url_here
SUPABASE_KEY=your_key_here
ELEVENLABS_API_KEY=your_key_here  # Optional for voice features
```

## Audio Playback Options

The voice tool supports multiple audio backends. You only need **one** of these:

### Option 1: PyAudio (Requires System Library)

**Pros**: Full-featured, widely used
**Cons**: Requires system library installation

```bash
# macOS
brew install portaudio
pip install pyaudio

# Linux
sudo apt-get install portaudio19-dev
pip install pyaudio
```

### Option 2: SoundDevice (Recommended - Easier)

**Pros**: No system dependencies, simpler installation
**Cons**: Slightly less control

```bash
pip install sounddevice
```

### Option 3: SimpleAudio

**Pros**: Very simple, no dependencies
**Cons**: Basic functionality

```bash
pip install simpleaudio
```

### Option 4: No Audio Playback

You can use the voice tool without audio playback. Audio will be generated and can be saved to files, but won't play automatically.

## Troubleshooting

### "portaudio.h file not found" (macOS)

```bash
brew install portaudio
pip install pyaudio
```

### "pyaudio installation fails"

Try using an alternative:

```bash
pip install sounddevice
```

The voice tool will automatically detect and use available audio backends.

### "No audio playback available"

This is okay! The voice tool will still:
- Generate audio files
- Stream audio data
- Save audio to files

You just won't hear it automatically. You can:
- Save audio and play manually: `voice.save_audio(audio_data, "output.mp3")`
- Use the audio data with other tools
- Integrate with web-based audio APIs

### "ELEVENLABS_API_KEY not found"

Voice features are optional. The agent will work without it, but voice call features will be disabled.

## Verify Installation

```bash
python -c "from tools.voice_tool import VoiceTool; print('✅ Voice tool imports successfully')"
```

## Minimal Installation (No Audio Playback)

If you don't need audio playback, you can skip audio libraries entirely:

```bash
# Install core dependencies only
pip install groq python-dotenv rich tavily-python supabase elevenlabs requests
```

The voice tool will generate audio but won't play it automatically. You can still:
- Save audio to files
- Use audio data programmatically
- Integrate with other audio systems

