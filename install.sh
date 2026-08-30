#!/bin/bash
# ─────────────────────────────────────────────
#  Sprout — Install Script
#  Installs Sprout as a proper system service
#  that runs in the background on boot.
# ─────────────────────────────────────────────

set -e  # exit on any error

SPROUT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SPROUT_DIR/venv"
SERVICE_NAME="sprout"
SERVICE_FILE="$HOME/.config/systemd/user/$SERVICE_NAME.service"

echo ""
echo "🌱 Sprout Installer"
echo "===================="
echo "Installing from: $SPROUT_DIR"
echo ""

# ── Step 1: Python check ──────────────────────────────────────────────────────
echo "Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Install it with: sudo apt install python3"
    exit 1
fi
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✓ Python $PYTHON_VERSION found"

# ── Step 2: Virtual environment ───────────────────────────────────────────────
echo ""
echo "Setting up virtual environment..."
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    echo "✓ Created venv"
else
    echo "✓ venv already exists"
fi

source "$VENV_DIR/bin/activate"

# ── Step 3: Dependencies ──────────────────────────────────────────────────────
echo ""
echo "Installing dependencies..."
pip install --upgrade pip --quiet

# Core — always required
pip install --quiet \
    rich \
    pydantic \
    python-dotenv \
    google-genai \
    chromadb \
    networkx \
    pystray \
    pillow

echo "✓ Core dependencies installed"

# Voice — optional, skip if pyaudio fails (needs portaudio)
echo ""
echo "Installing voice dependencies (optional)..."
if sudo apt-get install -y portaudio19-dev --quiet 2>/dev/null; then
    pip install --quiet openai-whisper openwakeword pyttsx3 pyaudio
    echo "✓ Voice dependencies installed"
else
    echo "⚠️  Skipping voice deps — install portaudio manually:"
    echo "    sudo apt install portaudio19-dev"
    echo "    pip install openai-whisper openwakeword pyttsx3 pyaudio"
fi

# Screenshot tool
if ! command -v scrot &> /dev/null; then
    echo ""
    echo "Installing scrot for screenshots..."
    sudo apt-get install -y scrot --quiet
    echo "✓ scrot installed"
fi

# ── Step 4: Environment file ──────────────────────────────────────────────────
echo ""
if [ ! -f "$SPROUT_DIR/.env" ]; then
    cp "$SPROUT_DIR/.env.example" "$SPROUT_DIR/.env" 2>/dev/null || cat > "$SPROUT_DIR/.env" << EOF
GEMINI_API_KEY=your_gemini_api_key_here
EOF
    echo "⚠️  Created .env — add your GEMINI_API_KEY:"
    echo "    nano $SPROUT_DIR/.env"
else
    echo "✓ .env already exists"
fi

# ── Step 5: Data directories ──────────────────────────────────────────────────
mkdir -p "$SPROUT_DIR/data"
mkdir -p "$SPROUT_DIR/logs"
mkdir -p "$SPROUT_DIR/voice/models"
echo "✓ Directories created"

# ── Step 6: systemd user service ──────────────────────────────────────────────
echo ""
echo "Installing systemd service..."

mkdir -p "$HOME/.config/systemd/user"

cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Sprout AI Assistant
After=graphical-session.target
PartOf=graphical-session.target

[Service]
Type=simple
WorkingDirectory=$SPROUT_DIR
ExecStart=$VENV_DIR/bin/python $SPROUT_DIR/sprout.py --background
Restart=on-failure
RestartSec=5
Environment=DISPLAY=:0
Environment=DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/%U/bus
StandardOutput=append:$SPROUT_DIR/logs/sprout.log
StandardError=append:$SPROUT_DIR/logs/sprout.log

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable "$SERVICE_NAME"
echo "✓ Service installed and enabled on boot"

# ── Step 7: CLI shortcut ──────────────────────────────────────────────────────
echo ""
SHORTCUT="$HOME/.local/bin/sprout"
mkdir -p "$HOME/.local/bin"

cat > "$SHORTCUT" << EOF
#!/bin/bash
# Sprout CLI shortcut
source $VENV_DIR/bin/activate
cd $SPROUT_DIR
python sprout.py "\$@"
EOF

chmod +x "$SHORTCUT"

# Add to PATH if not already there
if ! echo "$PATH" | grep -q "$HOME/.local/bin"; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
    echo "✓ Added ~/.local/bin to PATH (restart terminal to take effect)"
fi

echo "✓ CLI shortcut installed"

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo "=============================="
echo "✓ Sprout installed!"
echo ""
echo "Commands:"
echo "  sprout              - Start interactive mode"
echo "  sprout --voice      - Start voice mode"
echo "  sprout --background - Start as background daemon"
echo ""
echo "Service commands:"
echo "  systemctl --user start sprout    - Start now"
echo "  systemctl --user stop sprout     - Stop"
echo "  systemctl --user status sprout   - Check status"
echo "  tail -f $SPROUT_DIR/logs/sprout.log - View logs"
echo ""
echo "Next step: Add your Gemini API key"
echo "  nano $SPROUT_DIR/.env"
echo ""