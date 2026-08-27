"""
Speech-to-Text using OpenAI Whisper

Offline, CPU-friendly speech recognition with tiny model
"""
import os
import tempfile
from pathlib import Path
from typing import Optional
import wave
import pyaudio

# Whisper will be imported lazily to avoid startup penalty
_whisper_model = None

class WhisperSTT:
    """Speech-to-Text using Whisper tiny model"""

    def __init__(self, model_size: str = "tiny"):
        """
        Initialize Whisper STT

        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
                       tiny = 39MB, fastest, good for real-time
        """
        self.model_size = model_size
        self.model = None
        self.sample_rate = 16000
        self.channels = 1

    def _load_model(self):
        """Lazy load Whisper model"""
        global _whisper_model

        if _whisper_model is None:
            try:
                import whisper
                _whisper_model = whisper.load_model(self.model_size)
                print(f"✓ Loaded Whisper {self.model_size} model")
            except ImportError:
                raise ImportError(
                    "Whisper not installed. Install with: pip install openai-whisper"
                )

        self.model = _whisper_model

    def transcribe_file(self, audio_path: str) -> dict:
        """
        Transcribe audio file to text

        Args:
            audio_path: Path to audio file

        Returns:
            Result dict with text and confidence
        """
        if self.model is None:
            self._load_model()

        try:
            result = self.model.transcribe(audio_path, language="en")

            return {
                "success": True,
                "text": result["text"].strip(),
                "language": result.get("language", "en"),
                "confidence": "high"  # Whisper doesn't provide confidence scores
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "text": ""
            }

    def record_audio(self, duration: int = 5, filename: Optional[str] = None) -> str:
        """
        Record audio from microphone

        Args:
            duration: Recording duration in seconds
            filename: Optional output filename (temp file if None)

        Returns:
            Path to recorded audio file
        """
        if filename is None:
            temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            filename = temp_file.name
            temp_file.close()

        try:
            audio = pyaudio.PyAudio()

            # Open stream
            stream = audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=1024
            )

            print(f"Recording for {duration} seconds...")
            frames = []

            # Record
            for _ in range(0, int(self.sample_rate / 1024 * duration)):
                data = stream.read(1024)
                frames.append(data)

            print("Recording complete")

            # Stop and close stream
            stream.stop_stream()
            stream.close()
            audio.terminate()

            # Save to file
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
                wf.setframerate(self.sample_rate)
                wf.writeframes(b''.join(frames))

            return filename

        except Exception as e:
            print(f"Error recording audio: {str(e)}")
            raise

    def listen_and_transcribe(self, duration: int = 5) -> dict:
        """
        Record audio and transcribe in one call

        Args:
            duration: Recording duration in seconds

        Returns:
            Transcription result dict
        """
        try:
            # Record audio
            audio_file = self.record_audio(duration)

            # Transcribe
            result = self.transcribe_file(audio_file)

            # Clean up temp file
            try:
                os.unlink(audio_file)
            except:
                pass

            return result

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "text": ""
            }

    def transcribe_with_retry(self, audio_path: str, max_retries: int = 2) -> dict:
        """
        Transcribe with retry logic for robustness

        Args:
            audio_path: Path to audio file
            max_retries: Maximum number of retry attempts

        Returns:
            Transcription result
        """
        for attempt in range(max_retries + 1):
            result = self.transcribe_file(audio_path)

            if result["success"]:
                return result

            if attempt < max_retries:
                print(f"Retry {attempt + 1}/{max_retries}...")

        return result
