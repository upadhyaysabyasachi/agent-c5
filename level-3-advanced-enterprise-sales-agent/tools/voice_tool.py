"""
Voice Tool - ElevenLabs Integration for Voice Agent
Handles audio streaming for real-time voice conversations.
"""

import os
import io
import queue
import threading
import time
from typing import Optional, Callable, Generator
from dotenv import load_dotenv

try:
    from elevenlabs import ElevenLabs
    from elevenlabs.client import ElevenLabs
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
    print("⚠️  Warning: elevenlabs package not installed. Voice features will be disabled.")

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
except OSError:
    # pyaudio installed but portaudio library not found
    PYAUDIO_AVAILABLE = False

# Try alternative audio libraries
try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False

try:
    import simpleaudio as sa
    SIMPLEAUDIO_AVAILABLE = True
except ImportError:
    SIMPLEAUDIO_AVAILABLE = False

# Deepgram (optional - for future STT integration)
try:
    from deepgram import Deepgram
    DEEPGRAM_AVAILABLE = True
except (ImportError, Exception) as e:
    DEEPGRAM_AVAILABLE = False
    Deepgram = None  # Placeholder for type hints
    if not isinstance(e, ImportError):
        print(f"⚠️  Warning: Deepgram import failed: {e}")

load_dotenv()


class VoiceTool:
    """
    Voice Agent Tool using ElevenLabs for text-to-speech and speech-to-text.
    Supports real-time audio streaming for natural conversations.
    """
    
    def __init__(self, voice_id: Optional[str] = None):
        """
        Initialize the Voice Tool.
        
        Args:
            voice_id: Optional ElevenLabs voice ID. Defaults to a professional voice.
        """
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY not found in environment variables")
        
        if not ELEVENLABS_AVAILABLE:
            raise ImportError("elevenlabs package is required. Install with: pip install elevenlabs")
        
        self.client = ElevenLabs(api_key=self.api_key)
        
        # Default professional voice ID (can be customized)
        self.voice_id = voice_id or os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  # Rachel voice
        
        # Audio settings (using dictionary format for ElevenLabs SDK)
        self.voice_settings = {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True
        }
        
        # Audio configuration
        self.sample_rate = 44100
        self.channels = 1
        self.chunk_size = 1024
        
        # Audio I/O setup
        self.audio = None
        self.input_stream = None
        self.output_stream = None
        
        if PYAUDIO_AVAILABLE:
            try:
                self.audio = pyaudio.PyAudio()
            except Exception as e:
                print(f"⚠️  PyAudio initialization warning: {e}")
                self.audio = None
        
        # Log available audio backends
        available_backends = []
        if PYAUDIO_AVAILABLE:
            available_backends.append("PyAudio")
        if SOUNDDEVICE_AVAILABLE:
            available_backends.append("SoundDevice")
        if SIMPLEAUDIO_AVAILABLE:
            available_backends.append("SimpleAudio")
        
        if available_backends:
            print(f"✅ Audio playback available via: {', '.join(available_backends)}")
        else:
            print("⚠️  No audio playback libraries available. Audio will be generated but not played.")
            print("   Install one of: pyaudio (requires portaudio), sounddevice, or simpleaudio")

        # Initialize Deepgram (optional - for future STT integration)
        self.deepgram = None
        if DEEPGRAM_AVAILABLE:
            deepgram_key = os.getenv("DEEPGRAM_API_KEY")
            if deepgram_key:
                try:
                    self.deepgram = Deepgram(deepgram_key)
                except Exception as e:
                    print(f"⚠️  Deepgram initialization warning: {e}")
    
    def text_to_speech_stream(self, text: str) -> Generator[bytes, None, None]:
        """
        Convert text to speech and stream audio chunks.
        
        Args:
            text: Text to convert to speech
            
        Yields:
            Audio chunks as bytes
        """
        if not ELEVENLABS_AVAILABLE:
            raise RuntimeError("ElevenLabs SDK not available")
        
        try:
            # Generate audio stream from ElevenLabs
            # Using the text_to_speech method with streaming
            audio_generator = self.client.text_to_speech.convert(
                voice_id=self.voice_id,
                text=text,
                model_id="eleven_turbo_v2_5",  # Fast model for real-time
                voice_settings=self.voice_settings
            )
            
            # Yield audio chunks
            for chunk in audio_generator:
                if chunk:
                    yield chunk
                    
        except Exception as e:
            print(f"❌ TTS Error: {e}")
            # Fallback: try alternative method
            try:
                audio_generator = self.client.generate(
                    text=text,
                    voice=self.voice_id,
                    model="eleven_turbo_v2_5",
                    stream=True
                )
                for chunk in audio_generator:
                    if chunk:
                        yield chunk
            except Exception as e2:
                print(f"❌ TTS Fallback Error: {e2}")
                raise
    
    def speak(self, text: str, play_audio: bool = True) -> bytes:
        """
        Convert text to speech and optionally play it.
        
        Args:
            text: Text to speak
            play_audio: Whether to play audio through speakers
            
        Returns:
            Complete audio data as bytes
        """
        audio_chunks = []
        
        # Collect all audio chunks
        for chunk in self.text_to_speech_stream(text):
            audio_chunks.append(chunk)
            if play_audio and PYAUDIO_AVAILABLE:
                self._play_audio_chunk(chunk)
        
        # Return complete audio
        return b''.join(audio_chunks)
    
    def _play_audio_chunk(self, chunk: bytes):
        """Play a single audio chunk through speakers."""
        # Try pyaudio first
        if PYAUDIO_AVAILABLE and self.audio:
            try:
                if not self.output_stream:
                    self.output_stream = self.audio.open(
                        format=pyaudio.paInt16,
                        channels=self.channels,
                        rate=self.sample_rate,
                        output=True
                    )
                self.output_stream.write(chunk)
                return
            except Exception as e:
                print(f"⚠️  PyAudio playback error: {e}")
        
        # Try sounddevice as alternative
        if SOUNDDEVICE_AVAILABLE:
            try:
                import numpy as np
                # Convert bytes to numpy array
                audio_array = np.frombuffer(chunk, dtype=np.int16)
                sd.play(audio_array, samplerate=self.sample_rate)
                return
            except Exception as e:
                print(f"⚠️  SoundDevice playback error: {e}")
        
        # Try simpleaudio as fallback
        if SIMPLEAUDIO_AVAILABLE:
            try:
                play_obj = sa.play_buffer(chunk, self.channels, 2, self.sample_rate)
                return
            except Exception as e:
                print(f"⚠️  SimpleAudio playback error: {e}")
        
        # If no audio library available, just log
        if not any([PYAUDIO_AVAILABLE, SOUNDDEVICE_AVAILABLE, SIMPLEAUDIO_AVAILABLE]):
            # Silent failure - audio will be generated but not played
            pass
    
    def start_listening(self, callback: Callable[[str], None], duration: int = 10):
        """
        Start listening for speech input (placeholder for future STT integration).
        
        Note: ElevenLabs currently focuses on TTS. For STT, you'd integrate
        with services like Deepgram, AssemblyAI, or Whisper.
        
        Args:
            callback: Function to call with transcribed text
            duration: How long to listen (seconds)
        """
        # Placeholder implementation
        if self.deepgram:
            try:
                dg_connection = self.deepgram.transcription.live({
                    'punctuate': True,
                    'interim_results': False
                })
                # In production, integrate with a speech-to-text service
                print("🎤 Listening for speech... (STT integration needed)")
                
                async def on_message(transcript):
                    text = transcript['channel']['alternatives'][0]['transcript']
                    if text:
                        callback(text)
                    
                dg_connection.registerHandler('transcriptReceived', on_message)
                time.sleep(1)
                callback("Mock transcription - integrate STT service here")
                return
            except Exception as e:
                print(f"⚠️  Deepgram error: {e}")
        
        # Fallback if Deepgram not available
        print("🎤 Listening for speech... (STT integration needed)")
        print("   Note: For full STT, integrate with Deepgram, AssemblyAI, or OpenAI Whisper")
        time.sleep(1)
        callback("Mock transcription - integrate STT service here")
    
    def _handle_deepgram_transcription(self, dg_connection):
        """Handle Deepgram transcription."""
        if not self.deepgram:
            return None
        try:
            for chunk in dg_connection:
                if chunk.type == "Result":
                    print(chunk.channel.alternatives[0].transcript)
                    return chunk.channel.alternatives[0].transcript
        except Exception as e:
            print(f"⚠️  Deepgram transcription error: {e}")
        return None
    def voice_call(
        self,
        script: str,
        on_user_speech: Optional[Callable[[str], str]] = None,
        max_turns: int = 10
    ) -> dict:
        """
        Conduct a voice call with streaming audio.
        
        Args:
            script: Initial script/script to say
            on_user_speech: Callback function that receives user speech and returns agent response
            max_turns: Maximum conversation turns
            
        Returns:
            Dictionary with call metadata and transcript
        """
        transcript = []
        turn_count = 0
        
        print("📞 Starting voice call...")
        
        # Initial greeting
        print(f"🤖 Agent: {script[:100]}...")
        audio_data = self.speak(script, play_audio=True)
        transcript.append({"role": "agent", "text": script, "audio_length": len(audio_data)})
        
        # Conversation loop
        while turn_count < max_turns:
            turn_count += 1
            
            # Listen for user response
            user_text = None
            if on_user_speech:
                # In production, this would use actual STT
                # For now, we'll use a callback that simulates user input
                user_text = on_user_speech("")
            else:
                # Fallback: prompt for text input
                user_text = input("You (speak or type): ")
            
            if not user_text or user_text.lower() in ["end", "goodbye", "exit"]:
                break
            
            transcript.append({"role": "user", "text": user_text})
            
            # Generate agent response (this would come from LLM in production)
            if on_user_speech:
                agent_response = on_user_speech(user_text)
            else:
                # Placeholder response
                agent_response = f"I understand you said: {user_text}. How can I help you further?"
            
            # Speak response
            print(f"🤖 Agent: {agent_response[:100]}...")
            audio_data = self.speak(agent_response, play_audio=True)
            transcript.append({"role": "agent", "text": agent_response, "audio_length": len(audio_data)})
        
        print("📞 Call ended.")
        
        return {
            "duration_seconds": time.time(),  # Would track actual duration
            "turns": turn_count,
            "transcript": transcript,
            "status": "completed"
        }
    
    def save_audio(self, audio_data: bytes, filepath: str):
        """Save audio data to a file."""
        with open(filepath, "wb") as f:
            f.write(audio_data)
        print(f"💾 Audio saved to {filepath}")
    
    def cleanup(self):
        """Clean up audio resources."""
        if self.output_stream:
            self.output_stream.stop_stream()
            self.output_stream.close()
            self.output_stream = None
        
        if self.input_stream:
            self.input_stream.stop_stream()
            self.input_stream.close()
            self.input_stream = None
        
        if self.audio:
            self.audio.terminate()
            self.audio = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup."""
        self.cleanup()


def create_voice_tool(voice_id: Optional[str] = None) -> VoiceTool:
    """
    Factory function to create a VoiceTool instance.
    
    Args:
        voice_id: Optional voice ID
        
    Returns:
        VoiceTool instance
    """
    return VoiceTool(voice_id=voice_id)

