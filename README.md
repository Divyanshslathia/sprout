# 🌱 Sprout — Personal AI OS Assistant

> LLM-powered voice-activated assistant that controls your computer with a permission-first architecture.

**Current Status:** Phase 1 Complete — Text-based interface with full agent functionality

## Features (Phase 1)

✅ **Multi-Agent Architecture**
- Orchestrator agent for intent routing
- System agent for OS operations
- File agent for file system management
- Research agent for information queries

✅ **Intent Classification**
- Automatic detection of intent type (INFORMATION, SYSTEM_ACTION, FILE_OPERATION, etc.)
- Risk level assessment (SAFE, SENSITIVE, DESTRUCTIVE)
- Human-in-the-loop for sensitive operations

✅ **Permission System**
- JSON-based permission policy (will evolve to Neo4j in Phase 3)
- Configurable allowed apps, directories, and commands
- Automatic blocking of dangerous operations

✅ **Memory & Logging**
- SQLite session history
- Action logging with full audit trail
- Conversation persistence

✅ **Safety Features**
- Input guardrails against dangerous commands
- Permission checks before every action
- Confirmation prompts for sensitive operations

## Installation

```bash
# Clone the repository
cd ~/Downloads/sprout

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

## Quick Start

```bash
# Activate virtual environment
source venv/bin/activate

# Run Sprout
python agent.py
```

## Usage Examples

### System Control
```
You: open terminal
You: close firefox
You: screenshot
```

### File Operations
```
You: read file ~/Documents/notes.txt
You: list files ~/Downloads
You: write file test.txt
```

### Terminal Commands
```
You: run ls -la
You: run pwd
```

### Information Queries
```
You: what time is it
You: search for Python tutorials
You: help
```

### View History
```
You: history
```

## Architecture

```
User Input
    ↓
Intent Classifier (Type + Risk)
    ↓
Orchestrator Agent
    ↓
Permission Check
    ↓
Human-in-the-Loop (if SENSITIVE/DESTRUCTIVE)
    ↓
Specialist Agent (System/File/Research)
    ↓
Action Execution
    ↓
Memory & Logging
```

## Project Structure

```
sprout/
├── core/
│   ├── agents/
│   │   ├── orchestrator.py      # Root agent, routing
│   │   ├── file_agent.py        # File operations
│   │   ├── system_agent.py      # OS actions
│   │   └── research_agent.py    # Information queries
│   ├── intent/
│   │   ├── classifier.py        # Intent classification
│   │   └── types.py             # IntentType, RiskLevel enums
│   ├── permissions/
│   │   └── policy.py            # Permission checking
│   ├── memory/
│   │   ├── session.py           # Conversation history
│   │   └── history.py           # Action logging
│   ├── tools/
│   │   ├── os_tools.py          # Linux system automation
│   │   ├── file_tools.py        # File operations
│   │   └── web_tools.py         # Web search
│   └── callbacks.py             # Logging & guardrails
├── voice/                       # Phase 2: Voice pipeline
├── data/                        # SQLite databases, permissions
├── agent.py                     # Main entry point
├── config.py                    # Configuration
└── requirements.txt
```

## Permission Configuration

Permissions are stored in `data/permissions.json`. Default permissions include:

**Allowed Apps:**
- firefox, chrome, terminal, code, nautilus

**Allowed Directories:**
- /home/divyansh/Documents
- /home/divyansh/Downloads
- /home/divyansh/projects

**Blocked Directories:**
- /etc, /sys, /proc, /root

**Blocked Commands:**
- rm -rf /, format, dd if=, mkfs

You can edit this file to customize permissions.

## Safety Features

### Input Guardrails
- Blocks dangerous command patterns (rm -rf /, format, fork bombs)
- Prevents operations on sensitive system paths
- Sanitizes command inputs

### Permission Layers
- **SAFE** actions execute immediately
- **SENSITIVE** actions show confirmation prompt
- **DESTRUCTIVE** actions require explicit user approval

### Audit Trail
Every action is logged with:
- Timestamp
- Intent type and risk level
- Action and target
- Permission decision
- Success/failure status

## Development Roadmap

### ✅ Phase 1 — Working Brain (Complete)
- Multi-agent system with orchestrator
- Intent classification and risk assessment
- Permission system with JSON policies
- Memory and action logging
- Text-based interface

### 🔜 Phase 2 — Voice Layer (Weeks 5-6)
- [ ] Whisper STT integration
- [ ] Porcupine wake word detection
- [ ] Text-to-speech with pyttsx3
- [ ] Voice pipeline connection

### 🔜 Phase 3 — Memory & Knowledge Graph (Weeks 7-8)
- [ ] ChromaDB for semantic memory
- [ ] Neo4j for permission graph
- [ ] Behavior learning from history
- [ ] RAG on personal data

### 🔜 Phase 4 — Windows Support
- [ ] Cross-platform OS abstraction
- [ ] Windows-specific automation
- [ ] Same agent logic, different execution layer

## Requirements

- Python 3.8+
- Linux (Ubuntu/Debian recommended)
- Optional for full functionality:
  - `xclip` for clipboard operations: `sudo apt install xclip`
  - `scrot` for screenshots: `sudo apt install scrot`

## Tech Stack

- **Agent Framework:** Google ADK (Phase 3)
- **LLM:** Gemini Flash (Phase 3 for advanced parsing)
- **Database:** SQLite for sessions and history
- **UI:** Rich library for terminal interface
- **OS Automation:** subprocess, xdotool

## Commands Reference

| Command | Description |
|---------|-------------|
| `open [app]` | Open an application |
| `close [app]` | Close an application |
| `screenshot` | Take a screenshot |
| `clipboard` | Get clipboard content |
| `read file [path]` | Read file contents |
| `write file [path]` | Write to a file |
| `delete file [path]` | Delete a file |
| `list files [dir]` | List directory contents |
| `run [command]` | Execute terminal command |
| `search [query]` | Search the web |
| `help` | Show help information |
| `history` | Show recent actions |
| `exit` | Quit Sprout |

## Contributing

This is a solo project built as a portfolio piece demonstrating:
- Multi-agent system design
- Permission-gated execution
- Voice pipeline integration (Phase 2)
- Memory and knowledge graph architecture (Phase 3)

## License

MIT License

## Author

Built by [Your Name] as a demonstration of:
- LLM-powered agent systems
- OS automation with safety controls
- Multi-agent orchestration
- Privacy-first AI assistant design

---

**Note:** Phase 1 complete. Voice integration coming in Phase 2!
