"""
Wake Word Detection using OpenWakeWord

Always-on, lightweight wake word detection — completely free and offline.
Uses openWakeWord library (Apache 2.0 license).

Install: pip install openwakeword pyaudio
"""
import threading
import struct
import pyaudio
from typing import Optional, Callable


class WakeWordDetector:
    """
    Wake word detector using OpenWakeWord.

    Replaces Porcupine (paid) with a fully free, offline alternative.
    Supports custom wake word models trained for free via openWakeWord tooling.

    Default wake word: "hey jarvis" (built-in pretrained model)
    For "Hey Sprout": train a custom model at github.com/dscripka/openWakeWord
    """

    # Built-in models that come with openWakeWord out of the box
    BUILTIN_MODELS = [
        "hey_jarvis",       # closest to "hey sprout" style
        "alexa",
        "hey_mycroft",
        "timer",
    ]

    def __init__(
        self,
        model_path: Optional[str] = None,
        wake_word: str = "hey_jarvis",
        threshold: float = 0.5,
    ):
        """
        Initialize wake word detector.

        Args:
            model_path: Path to custom .tflite model file.
                        If None, uses a built-in pretrained model.
            wake_word:  Which built-in model to use if model_path is None.
                        One of BUILTIN_MODELS above.
            threshold:  Detection confidence threshold (0.0 - 1.0).
                        Lower = more sensitive (more false positives).
                        Higher = less sensitive (may miss detections).
        """
        self.model_path = model_path
        self.wake_word = wake_word
        self.threshold = threshold

        self.oww_model = None
        self.audio = None
        self.stream = None
        self._listening = False

        # Audio config — openWakeWord requires 16kHz, 16-bit, mono
        self.SAMPLE_RATE = 16000
        self.CHUNK_SIZE = 1280   # 80ms of audio at 16kHz — recommended by openWakeWord

    def _initialize(self):
        """Lazy initialization — only loads model when actually needed."""
        try:
            from openwakeword.model import Model
        except ImportError:
            raise ImportError(
                "OpenWakeWord not installed.\n"
                "Run: pip install openwakeword"
            )

        try:
            if self.model_path:
                # Custom trained model (e.g. "Hey Sprout")
                self.oww_model = Model(
                    wakeword_models=[self.model_path],
                    inference_framework="tflite"
                )
                print(f"✓ OpenWakeWord loaded custom model: {self.model_path}")
            else:
                # Built-in pretrained model
                self.oww_model = Model(
                    wakeword_models=[self.wake_word],
                    inference_framework="tflite"
                )
                print(f"✓ OpenWakeWord loaded built-in model: '{self.wake_word}'")

            # Initialize PyAudio
            self.audio = pyaudio.PyAudio()
            print("✓ Audio initialized")

        except Exception as e:
            raise RuntimeError(f"Failed to initialize OpenWakeWord: {e}")

    def start_listening(self, callback: Callable[[], None]):
        """
        Start the always-on listening loop.

        Runs in the current thread — call from a background thread if you
        need the main thread free.

        Args:
            callback: Function called immediately when wake word is detected.
        """
        if self.oww_model is None:
            self._initialize()

        self.stream = self.audio.open(
            rate=self.SAMPLE_RATE,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.CHUNK_SIZE
        )

        self._listening = True
        print(f"🎤 Listening for wake word... (threshold={self.threshold})")
        print("   Say 'Hey Sprout' or your configured wake word.")

        try:
            while self._listening:
                # Read one chunk of audio
                raw = self.stream.read(self.CHUNK_SIZE, exception_on_overflow=False)

                # Convert bytes → int16 array for openWakeWord
                audio_data = struct.unpack_from("h" * self.CHUNK_SIZE, raw)

                # Run inference
                prediction = self.oww_model.predict(audio_data)

                # Check if any model score exceeds threshold
                for model_name, score in prediction.items():
                    if score >= self.threshold:
                        print(f"\n✓ Wake word detected! (model={model_name}, score={score:.2f})")
                        # Reset scores so it doesn't keep firing
                        self.oww_model.reset()
                        callback()
                        break

        except KeyboardInterrupt:
            print("\nStopped listening")
        finally:
            self.stop_listening()

    def start_listening_async(self, callback: Callable[[], None]) -> threading.Thread:
        """
        Start listening in a background thread.

        Returns the thread so you can join it if needed.

        Args:
            callback: Function called when wake word is detected.

        Returns:
            Background thread running the detection loop.
        """
        thread = threading.Thread(
            target=self.start_listening,
            args=(callback,),
            daemon=True   # dies when main program exits
        )
        thread.start()
        return thread

    def stop_listening(self):
        """Stop listening and release audio resources."""
        self._listening = False

        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

        if self.audio is not None:
            self.audio.terminate()
            self.audio = None

        print("Wake word detector stopped.")

    def test_detection(self, duration: int = 10) -> int:
        """
        Test detection for N seconds. Prints detections and returns count.

        Args:
            duration: How many seconds to listen.

        Returns:
            Number of times wake word was detected.
        """
        import time

        detections = []

        def on_detect():
            detections.append(time.time())

        print(f"Testing for {duration} seconds — say your wake word...")

        thread = self.start_listening_async(on_detect)
        time.sleep(duration)
        self.stop_listening()
        thread.join(timeout=2)

        print(f"Done. Detected {len(detections)} time(s).")
        return len(detections)


# ── Training guide (printed when run directly) ────────────────────────────────

TRAINING_GUIDE = """
╔══════════════════════════════════════════════════════════════╗
║          Training a Custom "Hey Sprout" Wake Word           ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  OpenWakeWord lets you train custom wake words for FREE.     ║
║                                                              ║
║  Steps:                                                      ║
║  1. Go to: github.com/dscripka/openWakeWord                  ║
║  2. Use their Colab notebook (free Google Colab GPU)         ║
║  3. Record or synthesize ~5 mins of "Hey Sprout" audio       ║
║  4. Train — takes ~15 minutes on Colab                       ║
║  5. Download the .tflite model file                          ║
║  6. Place it in: voice/models/hey_sprout.tflite              ║
║  7. Update config.py:                                        ║
║       WAKE_WORD_MODEL = "voice/models/hey_sprout.tflite"     ║
║                                                              ║
║  Until then, use "hey_jarvis" as a placeholder.              ║
╚══════════════════════════════════════════════════════════════╝
"""


if __name__ == "__main__":
    print(TRAINING_GUIDE)

    detector = WakeWordDetector(wake_word="hey_jarvis", threshold=0.5)
    print("Running 15-second detection test...")
    count = detector.test_detection(duration=15)
    print(f"Result: {count} detection(s)")