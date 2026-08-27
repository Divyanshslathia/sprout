"""
Text-to-Speech using pyttsx3

Offline text-to-speech for voice responses
"""
import pyttsx3
from typing import Optional

class TextToSpeech:
    """Text-to-speech using pyttsx3"""

    def __init__(self, rate: int = 150, volume: float = 1.0):
        """
        Initialize TTS engine

        Args:
            rate: Speech rate (words per minute)
            volume: Volume level (0.0 to 1.0)
        """
        self.rate = rate
        self.volume = volume
        self.engine = None
        self._initialize_engine()

    def _initialize_engine(self):
        """Initialize pyttsx3 engine"""
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', self.rate)
            self.engine.setProperty('volume', self.volume)

            # Try to set a better voice if available
            voices = self.engine.getProperty('voices')
            if voices:
                # Prefer female voice if available
                for voice in voices:
                    if 'female' in voice.name.lower() or 'woman' in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        break

            print("✓ TTS engine initialized")

        except Exception as e:
            print(f"Warning: TTS initialization failed: {str(e)}")
            self.engine = None

    def speak(self, text: str, wait: bool = True) -> bool:
        """
        Speak text

        Args:
            text: Text to speak
            wait: Whether to wait for speech to complete

        Returns:
            Success status
        """
        if not self.engine:
            print(f"TTS not available. Would say: {text}")
            return False

        try:
            self.engine.say(text)
            if wait:
                self.engine.runAndWait()
            return True

        except Exception as e:
            print(f"TTS error: {str(e)}")
            return False

    def speak_async(self, text: str):
        """Speak text asynchronously (non-blocking)"""
        return self.speak(text, wait=False)

    def stop(self):
        """Stop current speech"""
        if self.engine:
            try:
                self.engine.stop()
            except:
                pass

    def set_rate(self, rate: int):
        """Set speech rate"""
        self.rate = rate
        if self.engine:
            self.engine.setProperty('rate', rate)

    def set_volume(self, volume: float):
        """Set volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        if self.engine:
            self.engine.setProperty('volume', self.volume)

    def list_voices(self):
        """List available voices"""
        if not self.engine:
            return []

        voices = self.engine.getProperty('voices')
        return [{"id": v.id, "name": v.name, "languages": v.languages} for v in voices]

    def set_voice(self, voice_id: str):
        """Set voice by ID"""
        if self.engine:
            self.engine.setProperty('voice', voice_id)

    def save_to_file(self, text: str, filename: str) -> bool:
        """
        Save speech to audio file

        Args:
            text: Text to convert
            filename: Output audio file path

        Returns:
            Success status
        """
        if not self.engine:
            return False

        try:
            self.engine.save_to_file(text, filename)
            self.engine.runAndWait()
            return True
        except Exception as e:
            print(f"Error saving to file: {str(e)}")
            return False
