"""
Sprout System Tray Indicator

Shows Sprout's status in the system tray.
States:
  - Grey  = running in background, waiting for wake word
  - Green = wake word detected, listening
  - Red   = error / stopped

Install dependency: pip install pystray pillow
"""
import threading
import sys
from pathlib import Path
from typing import Optional

# Lazy imports so Sprout still works without tray
_pystray = None
_PIL = None


def _import_tray_deps() -> bool:
    """Check if tray dependencies are available."""
    global _pystray, _PIL
    try:
        import pystray
        from PIL import Image, ImageDraw
        _pystray = pystray
        _PIL = (Image, ImageDraw)
        return True
    except ImportError:
        return False


class SproutTrayIcon:
    """
    System tray icon that shows Sprout's current state.

    States:
        idle     → grey circle  — running, waiting for wake word
        listening → green circle — wake word detected, actively listening
        thinking  → blue circle  — processing a command
        error     → red circle   — something went wrong
    """

    COLORS = {
        "idle":      (120, 120, 120),   # grey
        "listening": (50,  200, 50),    # green
        "thinking":  (50,  150, 255),   # blue
        "error":     (220, 50,  50),    # red
    }

    def __init__(self):
        self.icon = None
        self.current_state = "idle"
        self._thread: Optional[threading.Thread] = None
        self._available = _import_tray_deps()

        if not self._available:
            print("⚠️  Tray icon unavailable. Install with: pip install pystray pillow")

    def _make_icon_image(self, state: str):
        """Create a simple colored circle image for the tray."""
        Image, ImageDraw = _PIL
        size = 64
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        color = self.COLORS.get(state, self.COLORS["idle"])
        margin = 4
        draw.ellipse(
            [margin, margin, size - margin, size - margin],
            fill=color + (255,)   # full opacity
        )

        # Small sprout detail — two dots for "eyes" feel
        cx, cy = size // 2, size // 2
        dot_r = 4
        draw.ellipse([cx - 10 - dot_r, cy - dot_r, cx - 10 + dot_r, cy + dot_r], fill=(255, 255, 255, 200))
        draw.ellipse([cx + 10 - dot_r, cy - dot_r, cx + 10 + dot_r, cy + dot_r], fill=(255, 255, 255, 200))

        return img

    def _build_menu(self):
        """Build the right-click context menu."""
        pystray = _pystray

        return pystray.Menu(
            pystray.MenuItem("Sprout is running", None, enabled=False),
            pystray.MenuItem("Status: " + self.current_state.title(), None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Open Sprout", self._on_open),
            pystray.MenuItem("View Logs", self._on_view_logs),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Stop Sprout", self._on_quit),
        )

    def _on_open(self, icon, item):
        """Open interactive Sprout terminal."""
        import subprocess
        subprocess.Popen(
            ["bash", "-c", f"cd {Path(__file__).parent} && source venv/bin/activate && python sprout.py"],
            start_new_session=True
        )

    def _on_view_logs(self, icon, item):
        """Open log file in default text editor."""
        import subprocess
        log_path = Path(__file__).parent / "logs" / "sprout.log"
        subprocess.Popen(["xdg-open", str(log_path)])

    def _on_quit(self, icon, item):
        """Stop Sprout."""
        self.stop()
        sys.exit(0)

    def start(self):
        """Start the tray icon in a background thread."""
        if not self._available:
            return

        pystray = _pystray

        self.icon = pystray.Icon(
            name="sprout",
            icon=self._make_icon_image("idle"),
            title="Sprout - Waiting for wake word",
            menu=self._build_menu()
        )

        self._thread = threading.Thread(target=self.icon.run, daemon=True)
        self._thread.start()
        print("✓ Tray icon started")

    def set_state(self, state: str, tooltip: Optional[str] = None):
        """
        Update tray icon state.

        Args:
            state: One of "idle", "listening", "thinking", "error"
            tooltip: Optional custom tooltip text
        """
        if not self._available or self.icon is None:
            return

        self.current_state = state

        titles = {
            "idle":      "Sprout - Waiting for wake word",
            "listening": "Sprout - Listening...",
            "thinking":  "Sprout - Processing...",
            "error":     "Sprout - Error occurred",
        }

        self.icon.icon = self._make_icon_image(state)
        self.icon.title = tooltip or titles.get(state, "🌱 Sprout")

    def stop(self):
        """Stop the tray icon."""
        if self.icon:
            self.icon.stop()
            self.icon = None


# ── Singleton so all parts of Sprout share one tray icon ─────────────────────
_tray_instance: Optional[SproutTrayIcon] = None


def get_tray() -> SproutTrayIcon:
    """Get or create the global tray icon instance."""
    global _tray_instance
    if _tray_instance is None:
        _tray_instance = SproutTrayIcon()
    return _tray_instance


if __name__ == "__main__":
    # Test the tray icon
    import time

    print("Testing tray icon — check your system tray")
    tray = get_tray()
    tray.start()

    time.sleep(2)
    tray.set_state("listening", "🎤 Sprout — Listening...")
    time.sleep(2)
    tray.set_state("thinking", "💭 Sprout — Processing...")
    time.sleep(2)
    tray.set_state("idle")

    print("Test complete — press Ctrl+C to exit")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        tray.stop()