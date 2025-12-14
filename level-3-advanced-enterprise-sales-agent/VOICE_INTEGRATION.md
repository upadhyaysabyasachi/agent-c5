# Voice Agent Integration Guide

This document explains the ElevenLabs voice integration implementation for the Enterprise Sales Agent.

## Overview

The voice integration enables real-time voice conversations with leads using:
- **ElevenLabs TTS (Text-to-Speech)**: Converts agent responses to natural voice
- **Audio Streaming**: Real-time audio playback for seamless conversations
- **Call Management**: Full call lifecycle with transcript tracking

## Architecture

### Components

1. **`tools/voice_tool.py`** - Core voice functionality
   - ElevenLabs SDK integration
   - Audio streaming (input/output)
   - Voice call orchestration
   - Audio playback management

2. **`agent/engagement.py`** - Engagement engine
   - Email generation
   - Voice call script generation
   - Call execution and management
   - Integration with LLM for dynamic responses

3. **`agent/orchestrator.py`** - Main orchestrator
   - Phase 4: Engagement integration
   - User interaction for call selection
   - Call type selection (interactive vs script-only)

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Key dependencies:
- `elevenlabs>=0.2.27` - Voice synthesis
- `pyaudio>=0.2.14` - Audio I/O (optional, for local playback)

### 2. Environment Variables

Add to your `.env` file:

```bash
# Required for voice features
ELEVENLABS_API_KEY=your_api_key_here

# Optional: Custom voice ID
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
```

Get your API key from: https://elevenlabs.io

### 3. Voice Selection

Default voice: Professional female voice (Rachel)
- Voice ID: `21m00Tcm4TlvDq8ikWAM`
- Customize via `ELEVENLABS_VOICE_ID` environment variable

Browse voices at: https://elevenlabs.io/app/voice-library

## Usage

### Basic Voice Call

```python
from tools.voice_tool import VoiceTool

# Initialize
voice = VoiceTool()

# Generate and play speech
script = "Hello, this is a test call from our sales team."
audio_data = voice.speak(script, play_audio=True)

# Cleanup
voice.cleanup()
```

### Interactive Voice Call

```python
from agent.engagement import EngagementEngine

engagement = EngagementEngine()

# Make a call to a lead
result = engagement.make_voice_call(
    lead=lead_data,
    icp_profile=icp_data,
    interactive=True  # Enables real-time conversation
)
```

### Through Orchestrator

The orchestrator integrates voice calls in Phase 4 (Engagement):

1. Run the agent: `python main.py`
2. Complete phases 1-3 (ICP, Discovery, Qualification)
3. In Phase 4, select option 2 for voice calls
4. Choose a lead and call type (interactive or script-only)

## Features

### 1. Text-to-Speech Streaming

```python
# Stream audio chunks for real-time playback
for audio_chunk in voice.text_to_speech_stream("Your text here"):
    # Process chunk immediately
    play_audio(audio_chunk)
```

### 2. Call Script Generation

The engagement engine automatically generates personalized call scripts using:
- Lead information (company, industry)
- ICP profile (pain points, target market)
- LLM-powered personalization

### 3. Dynamic Conversation

In interactive mode, the agent:
- Listens for user responses (STT integration needed)
- Generates contextual responses using LLM
- Maintains conversation history
- Adapts to lead responses

### 4. Call Transcripts

All calls generate transcripts with:
- Agent messages
- User responses (when STT is integrated)
- Timestamps
- Audio metadata

## Audio Streaming Details

### Input Streaming (STT)

**Current Status**: Placeholder implementation
- Framework is ready for STT integration
- Recommended services: Deepgram, AssemblyAI, or OpenAI Whisper

**Future Integration Example**:
```python
def start_listening(self, callback, duration=10):
    # Integrate with Deepgram/AssemblyAI
    stream = stt_client.stream()
    # Process audio chunks
    # Call callback with transcribed text
```

### Output Streaming (TTS)

**Current Implementation**: Full streaming support
- Uses ElevenLabs streaming API
- Real-time audio chunk generation
- Low-latency playback

## Configuration

### Voice Settings

Customize voice characteristics in `voice_tool.py`:

```python
self.voice_settings = {
    "stability": 0.5,        # 0.0-1.0 (higher = more consistent)
    "similarity_boost": 0.75, # 0.0-1.0 (higher = more like original)
    "style": 0.0,            # 0.0-1.0 (higher = more expressive)
    "use_speaker_boost": True # Enhances clarity
}
```

### Model Selection

Available ElevenLabs models:
- `eleven_turbo_v2_5` - Fast, low-latency (default)
- `eleven_multilingual_v2` - Multi-language support
- `eleven_monolingual_v1` - English only, high quality

## Limitations & Future Work

### Current Limitations

1. **STT Integration**: Speech-to-text is placeholder
   - Need to integrate Deepgram, AssemblyAI, or Whisper
   - Text input fallback currently used

2. **Audio I/O**: Requires `pyaudio` for local playback
   - May need system audio drivers
   - Alternative: Use web-based audio APIs

3. **Call Recording**: Audio recording not yet implemented
   - Transcripts are saved
   - Audio files can be saved via `save_audio()` method

### Future Enhancements

1. **Full STT Integration**: Real-time speech recognition
2. **Call Recording**: Save audio files for review
3. **Sentiment Analysis**: Real-time emotion detection
4. **Multi-language**: Support for international calls
5. **Voice Cloning**: Custom voice training
6. **Call Analytics**: Performance metrics and insights

## Troubleshooting

### "ELEVENLABS_API_KEY not found"
- Ensure `.env` file exists with the key
- Check key is valid at elevenlabs.io

### "Audio playback error"
- Install `pyaudio`: `pip install pyaudio`
- On macOS: May need `brew install portaudio`
- On Linux: May need `sudo apt-get install portaudio19-dev`

### "Voice tool not available"
- Check API key is set correctly
- Verify `elevenlabs` package is installed
- Check internet connection for API calls

### Low audio quality
- Adjust `voice_settings` for better quality
- Use higher-quality model (slower but better)
- Check audio system settings

## Example Workflow

```
1. Agent generates call script based on lead + ICP
2. Voice tool converts script to audio
3. Audio streams to speakers/phone
4. (Interactive mode) User responds via STT
5. LLM generates response based on conversation
6. Response converted to speech
7. Process repeats until call ends
8. Transcript saved to database
```

## API Reference

### VoiceTool Class

- `speak(text, play_audio=True)` - Convert text to speech
- `text_to_speech_stream(text)` - Stream audio chunks
- `voice_call(script, on_user_speech, max_turns)` - Full call orchestration
- `save_audio(audio_data, filepath)` - Save audio to file
- `cleanup()` - Release audio resources

### EngagementEngine Class

- `generate_call_script(lead, icp_profile)` - Generate personalized script
- `make_voice_call(lead, icp_profile, interactive)` - Execute voice call
- `generate_email(lead, icp_profile)` - Generate email (non-voice)

## Support

For issues or questions:
1. Check ElevenLabs documentation: https://elevenlabs.io/docs
2. Review error messages in console
3. Verify API key and network connectivity
4. Check audio system configuration

---

**Note**: Voice features require an active ElevenLabs subscription. Free tier has usage limits.

