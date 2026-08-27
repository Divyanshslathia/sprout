"""
Voice Pipeline

Integrates wake word -> STT -> agent -> TTS
"""
import os
from typing import Optional, Callable
from rich.console import Console

from voice.wake_word import WakeWordDetector
from voice.stt import WhisperSTT
from voice.tts import TextToSpeech
from config import voice_config

console = Console()

class VoicePipeline:
    """Complete voice interaction pipeline"""

    def __init__(self,
                 porcupine_key: Optional[str] = None,
                 on_command: Optional[Callable[[str], str]] = None):
        """
        Initialize voice pipeline

        Args:
            porcupine_key: Porcupine access key
            on_command: Callback function that processes voice command and returns response
        """
        self.porcupine_key = porcupine_key or os.getenv("PORCUPINE_ACCESS_KEY")
        self.on_command = on_command

        # Initialize components
        self.wake_word = None
        self.stt = WhisperSTT(model_size=voice_config.whisper_model)
        self.tts = TextToSpeech(rate=voice_config.tts_rate)

        # State
        self.is_running = False
        self.listen_duration = 5  # seconds to listen after wake word

    def initialize_wake_word(self):
        """Initialize wake word detector (only when needed)"""
        if self.wake_word is None:
            try:
                self.wake_word = WakeWordDetector(
                    access_key=self.porcupine_key,
                    keyword=voice_config.wake_word
                )
                console.print(f"[green]✓ Wake word detector ready[/green]")
            except Exception as e:
                console.print(f"[red]✗ Wake word initialization failed: {str(e)}[/red]")
                console.print("[yellow]Tip: Get Porcupine key from https://picovoice.ai/[/yellow]")
                raise

    def _on_wake_word_detected(self):
        """Called when wake word is detected"""
        console.print("\n[bold green]👂 Listening...[/bold green]")
        self.tts.speak("Yes?")

        # Listen and transcribe
        result = self.stt.listen_and_transcribe(duration=self.listen_duration)

        if not result["success"]:
            console.print(f"[red]✗ Speech recognition failed: {result.get('error', 'Unknown error')}[/red]")
            self.tts.speak("Sorry, I didn't catch that.")
            return

        user_input = result["text"]
        console.print(f"[cyan]You said:[/cyan] {user_input}\n")

        if not user_input.strip():
            self.tts.speak("I didn't hear anything.")
            return

        # Process command through callback
        if self.on_command:
            try:
                response = self.on_command(user_input)

                # Speak response
                if response:
                    self.tts.speak(response)

            except Exception as e:
                console.print(f"[red]Error processing command: {str(e)}[/red]")
                self.tts.speak("Sorry, something went wrong.")

    def start(self):
        """Start the voice pipeline (wake word listening loop)"""
        console.print("\n[bold green]🌱 Sprout Voice Mode[/bold green]")
        console.print(f"[dim]Say '{voice_config.wake_word}' to activate[/dim]\n")

        self.initialize_wake_word()
        self.is_running = True

        try:
            self.wake_word.start_listening(
                callback=self._on_wake_word_detected,
                sensitivity=voice_config.porcupine_sensitivity
            )
        except KeyboardInterrupt:
            console.print("\n[yellow]Voice mode stopped[/yellow]")
        finally:
            self.stop()

    def stop(self):
        """Stop the voice pipeline"""
        self.is_running = False
        if self.wake_word:
            self.wake_word.stop_listening()
        console.print("[dim]Voice pipeline stopped[/dim]")

    def test_stt(self, duration: int = 5):
        """Test speech-to-text"""
        console.print(f"\n[cyan]Testing STT - speak for {duration} seconds...[/cyan]")

        result = self.stt.listen_and_transcribe(duration)

        if result["success"]:
            console.print(f"[green]✓ Transcription:[/green] {result['text']}")
        else:
            console.print(f"[red]✗ Failed:[/red] {result.get('error', 'Unknown error')}")

        return result

    def test_tts(self, text: str = "Hello, I am Sprout, your personal AI assistant."):
        """Test text-to-speech"""
        console.print(f"\n[cyan]Testing TTS...[/cyan]")
        console.print(f"[dim]Speaking: {text}[/dim]")

        success = self.tts.speak(text)

        if success:
            console.print("[green]✓ TTS working[/green]")
        else:
            console.print("[red]✗ TTS failed[/red]")

        return success

    def test_full_pipeline(self):
        """Test the complete pipeline without wake word"""
        console.print("\n[bold cyan]Testing Full Voice Pipeline[/bold cyan]\n")

        # Test TTS
        console.print("[yellow]Step 1: Testing TTS[/yellow]")
        self.test_tts()

        # Test STT
        console.print("\n[yellow]Step 2: Testing STT[/yellow]")
        self.tts.speak("Please speak now")
        result = self.test_stt(duration=3)

        if result["success"] and self.on_command:
            console.print("\n[yellow]Step 3: Testing command processing[/yellow]")
            response = self.on_command(result["text"])
            if response:
                self.tts.speak(response)

        console.print("\n[green]✓ Pipeline test complete[/green]")

    def process_voice_command_once(self, duration: int = 5) -> Optional[str]:
        """
        Listen for a single voice command without wake word

        Args:
            duration: How long to listen

        Returns:
            Transcribed text or None
        """
        console.print(f"[cyan]🎤 Listening for {duration} seconds...[/cyan]")

        result = self.stt.listen_and_transcribe(duration)

        if result["success"]:
            return result["text"]
        else:
            console.print(f"[red]Error: {result.get('error', 'Failed')}[/red]")
            return None
