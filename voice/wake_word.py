"""
Wake Word Detection using Porcupine

Always-on, lightweight wake word detection for "Hey Sprout"
"""
import struct
import pyaudio
from typing import Optional, Callable

# Porcupine will be imported lazily
_porcupine = None

class WakeWordDetector:
    """Wake word detector using Porcupine"""

    def __init__(self, access_key: Optional[str] = None, keyword: str = "porcupine"):
        """
        Initialize wake word detector

        Args:
            access_key: Porcupine access key from picovoice.ai
            keyword: Wake word to detect (built-in keywords or custom)
                    Built-in: alexa, americano, blueberry, bumblebee, computer,
                             grapefruit, grasshopper, hey google, hey siri,
                             jarvis, ok google, picovoice, porcupine, terminator
        """
        self.access_key = access_key
        self.keyword = keyword
        self.porcupine = None
        self.audio = None
        self.stream = None

    def _initialize_porcupine(self):
        """Lazy initialization of Porcupine"""
        try:
            import pvporcupine
        except ImportError:
            raise ImportError(
                "Porcupine not installed. Install with: pip install pvporcupine"
            )

        if not self.access_key:
            raise ValueError(
                "Porcupine access key required. Get one at https://picovoice.ai/\n"
                "Set PORCUPINE_ACCESS_KEY in .env file"
            )

        try:
            # Initialize Porcupine with built-in keyword
            self.porcupine = pvporcupine.create(
                access_key=self.access_key,
                keywords=[self.keyword]
            )

            self.audio = pyaudio.PyAudio()

            print(f"✓ Porcupine initialized with keyword: '{self.keyword}'")

        except Exception as e:
            raise RuntimeError(f"Failed to initialize Porcupine: {str(e)}")

    def start_listening(self, callback: Callable[[], None], sensitivity: float = 0.5):
        """
        Start listening for wake word

        Args:
            callback: Function to call when wake word is detected
            sensitivity: Detection sensitivity (0.0 to 1.0)
                        Higher = more sensitive (more false positives)
        """
        if self.porcupine is None:
            self._initialize_porcupine()

        try:
            # Open audio stream
            self.stream = self.audio.open(
                rate=self.porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=self.porcupine.frame_length
            )

            print(f"🎤 Listening for '{self.keyword}'... (Ctrl+C to stop)")

            while True:
                # Read audio frame
                pcm = self.stream.read(self.porcupine.frame_length)
                pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)

                # Check for wake word
                keyword_index = self.porcupine.process(pcm)

                if keyword_index >= 0:
                    print(f"\n✓ Wake word '{self.keyword}' detected!")
                    callback()

        except KeyboardInterrupt:
            print("\nStopped listening")
        finally:
            self.stop_listening()

    def stop_listening(self):
        """Stop listening and clean up resources"""
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

        if self.audio is not None:
            self.audio.terminate()
            self.audio = None

        if self.porcupine is not None:
            self.porcupine.delete()
            self.porcupine = None

    def test_detection(self, duration: int = 10):
        """
        Test wake word detection for specified duration

        Args:
            duration: Test duration in seconds
        """
        import time

        detected = []

        def on_detection():
            detected.append(time.time())
            print("Wake word detected!")

        print(f"Testing wake word detection for {duration} seconds...")
        print(f"Say '{self.keyword}' to test detection")

        # Start in background thread to allow timeout
        import threading

        thread = threading.Thread(target=self.start_listening, args=(on_detection,))
        thread.daemon = True
        thread.start()

        time.sleep(duration)

        self.stop_listening()

        print(f"\nTest complete. Detected {len(detected)} times.")
        return len(detected)
