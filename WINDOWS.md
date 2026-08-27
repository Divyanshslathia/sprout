# Windows Setup Guide for Sprout

## Quick Start on Windows

### Prerequisites
1. **Python 3.8+** - Download from [python.org](https://www.python.org/downloads/)
2. **Git** (optional) - For cloning the repository

### Installation

```powershell
# Clone or download the repository
cd Downloads\sprout

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install rich pydantic python-dotenv chromadb networkx

# Optional: Install voice features
pip install openai-whisper pvporcupine pyttsx3 pyaudio

# Optional: Install LLM features
pip install google-generativeai
```

### Configuration

1. Copy `.env.example` to `.env`:
```powershell
copy .env.example .env
```

2. Edit `.env` and add your API keys:
```
GEMINI_API_KEY=your_key_here
PORCUPINE_ACCESS_KEY=your_key_here
```

### Running Sprout on Windows

```powershell
# Text mode
python sprout.py

# Voice mode
python sprout.py --voice

# Run tests
python test_sprout.py
```

## Windows-Specific Features

### PowerShell Integration
Sprout automatically uses PowerShell for command execution on Windows:
- Commands run in PowerShell by default
- Full PowerShell syntax supported
- Access to Windows-specific cmdlets

### Windows Applications
Common Windows apps are supported out of the box:
```
You: open notepad
You: open calculator
You: open cmd
You: open powershell
You: open chrome
You: open edge
You: open explorer
```

### File Paths
Use either Windows or Unix-style paths:
```
You: read file C:\Users\YourName\Documents\file.txt
You: read file C:/Users/YourName/Documents/file.txt
You: read file ~\Documents\file.txt
```

### Clipboard Operations
Full clipboard support via PowerShell:
```
You: clipboard
You: set clipboard Hello World
```

### Screenshots
Screenshots work via PowerShell/.NET:
```
You: screenshot
```

## Platform Differences

| Feature | Linux | Windows | Notes |
|---------|-------|---------|-------|
| Terminal | bash/zsh | PowerShell/CMD | Auto-detected |
| App Control | process names | .exe files | Mapped automatically |
| Clipboard | xclip | PowerShell | Windows built-in |
| Screenshots | scrot | PowerShell | Windows built-in |
| File Paths | / separator | \ separator | Auto-normalized |

## Troubleshooting Windows

### Audio Issues (Voice Mode)
```powershell
# Install PyAudio from wheel (easier on Windows)
pip install pipwin
pipwin install pyaudio
```

### PowerShell Execution Policy
If commands fail, enable script execution:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### PATH Issues
Ensure Python is in your PATH:
```powershell
# Check Python
python --version

# If not found, add to PATH or use full path
C:\Python39\python.exe sprout.py
```

### Antivirus Warnings
Some antivirus software may flag automation tools. Add exception for:
- Python executable
- Sprout directory

## Windows-Specific Permissions

Default Windows permissions (in `data/permissions.json`):
```json
{
  "allowed_apps": [
    "notepad", "calculator", "cmd", "powershell",
    "chrome", "firefox", "edge", "code", "explorer"
  ],
  "allowed_directories": [
    "C:\\Users\\YourName\\Documents",
    "C:\\Users\\YourName\\Downloads",
    "C:\\Users\\YourName\\Desktop"
  ],
  "blocked_directories": [
    "C:\\Windows", "C:\\Program Files",
    "C:\\System32"
  ]
}
```

## Performance Tips

1. **Antivirus Exclusion**: Add Python and Sprout to exclusions for better performance
2. **SSD Recommended**: ChromaDB performs better on SSD
3. **RAM**: 4GB minimum, 8GB recommended for voice features

## Next Steps

1. Test basic commands: `python sprout.py`
2. Try voice if installed: `python sprout.py --voice`
3. Configure permissions in `data/permissions.json`
4. Add your Gemini API key for LLM features

## Support

- Documentation: See main README.md
- Issues: Works identically to Linux version
- Platform detection: Automatic, no configuration needed
