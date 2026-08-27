# 🌱 Sprout — Personal AI OS Assistant

> LLM-powered voice-activated assistant that controls your computer with a permission-first architecture.
> Built solo. Runs locally. Privacy by design.

---

## The Big Idea

Sprout listens for your voice, understands your intent, checks permissions, and executes actions on your OS — while keeping a memory of everything you've done and everything you prefer.

Three core rules that govern every decision in the system:

```
Rule 1: LLM is a decision maker, NOT an executor.
Rule 2: OS actions are gated by permissions, not prompts.
Rule 3: Always-listening ≠ always-thinking.
```

---

## Target Platform

| Platform | Status     | Notes                                      |
|----------|------------|--------------------------------------------|
| Linux    | ✅ Primary  | Full support, built here first             |
| Windows  | 🔜 Phase 3 | Same agent logic, different OS action layer|
| macOS    | ❌ Skipped  | Sandboxing restrictions, policy overhead   |

**Why Linux first:** Open OS automation APIs, no sandboxing headaches, runs well on weak hardware.

---

## System Architecture

```
                        [ User ]
                           |
                    Voice / Text Input
                           |
                    ┌──────▼──────┐
                    │  Wake Word  │  "Hey Sprout" / "Sprouty"
                    │  Detector   │  Porcupine (offline, lightweight)
                    └──────┬──────┘
                           |
                    ┌──────▼──────┐
                    │  Speech to  │  Whisper (tiny/base model)
                    │    Text     │  Offline, runs on CPU
                    └──────┬──────┘
                           |
              ┌────────────▼────────────┐
              │    Orchestrator Agent   │  Root ADK Agent
              │  (Intent + Risk Layer)  │  Classifies + Routes
              └──┬──────┬──────┬───────┘
                 │      │      │
         ┌───────▼─┐ ┌──▼────┐ ┌▼──────────┐
         │Research │ │ File  │ │  System   │
         │  Agent  │ │ Agent │ │  Agent    │
         │         │ │(MCP)  │ │           │
         └─────────┘ └───────┘ └───────────┘
                 │      │           │
         ┌───────▼──────▼───────────▼───────┐
         │         Permission Layer          │
         │   Knowledge Graph (Neo4j)         │
         │   Policy Check before any action  │
         └───────────────┬───────────────────┘
                         │
                 ┌───────▼────────┐
                 │ Action Executor │  OS automation
                 │                │  App control
                 │                │  File ops
                 │                │  Terminal
                 └───────┬────────┘
                         │
                 ┌───────▼────────┐
                 │  Memory Layer  │
                 │  Vector DB     │  Past actions
                 │  Session DB    │  Conversation history
                 └────────────────┘
```

---

## Intent Classification

Every user input is classified on two levels before anything executes.

### Level 1 — Intent Type

| Type                  | Example                              |
|-----------------------|--------------------------------------|
| `INFORMATION`         | "what is the weather in Hyderabad"   |
| `SYSTEM_ACTION`       | "open terminal"                      |
| `FILE_OPERATION`      | "delete report.csv"                  |
| `APPLICATION_CONTROL` | "open Instagram, message Rahet"      |
| `TERMINAL_OPERATION`  | "run the server"                     |
| `CONVERSATION`        | "what did I do yesterday"            |

### Level 2 — Risk Level

| Risk          | Behaviour                                    |
|---------------|----------------------------------------------|
| `SAFE`        | Execute immediately                          |
| `SENSITIVE`   | Show what will happen, ask for confirmation  |
| `DESTRUCTIVE` | Hard stop — explicit confirmation required   |

---

## Agent Stack

| Agent                | Role                                                    | Tools                          |
|----------------------|---------------------------------------------------------|-------------------------------|
| Orchestrator         | Routes intent, applies guardrails, manages conversation | classify_intent, route_to_agent|
| Research Agent       | Answers questions, summarises, web lookups              | web_search, summarise          |
| File Agent           | File read/write/delete/search                           | MCP Filesystem                 |
| System Agent         | App open/close, screenshot, clipboard                   | OS automation tools            |
| Memory Agent         | Store and recall user preferences and past actions      | Vector DB read/write           |

---

## ADK Features Used

| Feature               | Where it's used                                              |
|-----------------------|--------------------------------------------------------------|
| Multi-agent           | Orchestrator delegates to specialist agents                  |
| MCP                   | File Agent uses filesystem MCP server                        |
| Callbacks             | Every tool call logged with timestamp + token cost           |
| Guardrails            | Input checked for DESTRUCTIVE intent before LLM sees it      |
| Human in the loop     | SENSITIVE and DESTRUCTIVE actions pause and wait for confirm |
| Parallel tools        | Multiple safe actions run simultaneously                     |
| Persistent memory     | SQLite session DB + Vector DB for long term memory           |
| Error handling        | All tools have retry decorator, never throw raw exceptions   |
| Streaming             | Responses stream token by token, no waiting                  |

---

## Memory Architecture

```
Short term  →  ADK Session (current conversation)
Long term   →  SQLite (structured facts, preferences)
Semantic    →  ChromaDB / Pinecone (search by meaning)
Permissions →  Neo4j (capability graph, who can do what)
```

### What gets remembered
- Every action taken (what, when, outcome)
- User preferences (preferred apps, shortcuts)
- Past conversation summaries
- Permission grants and denials

---

## Permission System

Built on a Knowledge Graph (Neo4j). Relationships define what Sprout can do.

```
Sprout ──can_open──► Terminal
Sprout ──can_read──► /home/divyansh/Documents
Sprout ──cannot──►   /etc/passwd
Sprout ──needs_confirm──► send_message
Sprout ──needs_confirm──► delete_file
Sprout ──always_block──►  format_drive
```

Before any action executes:
1. Orchestrator classifies risk
2. Permission layer queries knowledge graph
3. If allowed → execute
4. If needs confirm → human in the loop
5. If blocked → hard deny, log attempt

---

## Voice Pipeline

```
Always running (tiny, offline):
Porcupine wake word detector
        ↓ "Hey Sprout" detected
Whisper STT activates (tiny model, CPU)
        ↓ transcribed text
Sprout agent pipeline starts
        ↓ response
TTS speaks back (pyttsx3 or Coqui, offline)
```

### Hardware Constraints (weakest machine target)

| Component       | Target spec         | Model choice                    |
|-----------------|---------------------|----------------------------------|
| Wake word       | Always on, < 5% CPU | Porcupine (runs on Pi)           |
| Speech to Text  | < 2s latency        | Whisper tiny (CPU, ~39MB)        |
| LLM             | Fast responses      | Gemini API (offloaded to cloud)  |
| Vector DB       | Low RAM             | ChromaDB (embedded, no server)   |
| Graph DB        | Lightweight         | Neo4j or SQLite + networkx       |

**Design principle:** Wake word and STT run locally always. LLM is cloud (Gemini API). Memory is local. Network only needed for LLM calls and web search.

---

## Build Phases

### Phase 1 — Working Brain (Weeks 1-4, text only)
- [ ] Project structure + environment setup
- [ ] Intent detection agent (classify type + risk)
- [ ] File agent with MCP filesystem
- [ ] System agent (open/close apps on Linux)
- [ ] Permission system (simple JSON → Neo4j later)
- [ ] Human in the loop for SENSITIVE/DESTRUCTIVE
- [ ] Callbacks + guardrails
- [ ] Persistent memory (SQLite)

**End of Phase 1:** Type commands, Sprout executes with permissions. Fully demoable.

### Phase 2 — Voice Layer (Weeks 5-6)
- [ ] Whisper STT integration
- [ ] Wake word with Porcupine
- [ ] TTS response (pyttsx3)
- [ ] Voice pipeline connected to agent

**End of Phase 2:** Say "Hey Sprout open terminal" — it opens.

### Phase 3 — Memory + Knowledge Graph (Weeks 7-8)
- [ ] ChromaDB for semantic memory
- [ ] Neo4j for permission graph
- [ ] Behaviour learning from past actions
- [ ] RAG on personal history

**End of Phase 3:** Sprout remembers you, adapts to your patterns.

### Phase 4 — Windows Support
- [ ] OS action layer abstraction
- [ ] Windows-specific app control
- [ ] Same agent logic, swapped execution layer

---

## Project Structure

```
sprout/
├── core/
│   ├── agents/
│   │   ├── orchestrator.py      # root agent, intent + routing
│   │   ├── file_agent.py        # MCP filesystem
│   │   ├── system_agent.py      # OS actions
│   │   └── research_agent.py    # information queries
│   ├── intent/
│   │   ├── classifier.py        # intent type + risk level
│   │   └── types.py             # IntentType, RiskLevel enums
│   ├── permissions/
│   │   ├── policy.py            # permission check logic
│   │   └── graph.py             # Neo4j / knowledge graph
│   ├── memory/
│   │   ├── session.py           # short term, ADK session
│   │   ├── vector_store.py      # ChromaDB semantic memory
│   │   └── history.py           # action log
│   ├── tools/
│   │   ├── os_tools.py          # Linux app control, terminal
│   │   ├── file_tools.py        # file operations
│   │   └── web_tools.py         # search, fetch
│   └── callbacks.py             # logging, cost tracking, guardrails
├── voice/
│   ├── wake_word.py             # Porcupine
│   ├── stt.py                   # Whisper
│   └── tts.py                   # pyttsx3
├── agent.py                     # entry point
├── config.py                    # all settings, paths, model names
├── .env                         # API keys
└── README.md
```

---

## Tech Stack

| Layer           | Technology                    | Why                                      |
|-----------------|-------------------------------|------------------------------------------|
| Agent framework | Google ADK                    | Multi-agent, MCP, callbacks built in     |
| LLM             | Gemini 3.6 Flash              | Fast, cheap, good function calling       |
| Wake word       | Porcupine (Picovoice)         | Offline, < 5% CPU, runs on weak hardware |
| STT             | OpenAI Whisper (tiny)         | Offline, CPU-only, accurate enough       |
| TTS             | pyttsx3 / Coqui TTS           | Offline, no API needed                   |
| Vector DB       | ChromaDB                      | Embedded, no server, low RAM             |
| Graph DB        | Neo4j (or networkx for dev)   | Permission relationships                 |
| Session DB      | SQLite (ADK built in)         | Conversation persistence                 |
| OS automation   | subprocess + xdotool (Linux)  | App control, window management           |
| MCP server      | filesystem MCP                | File operations via standard protocol    |

---

## Constraints and Design Decisions

**Privacy first** — wake word detection is always offline. Nothing leaves the machine until you give a command. LLM call is the only network request.

**Weak hardware friendly** — Whisper tiny model (39MB), Porcupine (runs on Raspberry Pi), ChromaDB embedded (no server process). Should run on a 4GB RAM machine.

**Permission over prompts** — the LLM decides what to do, but the permission layer decides if it's allowed. LLM cannot override permissions no matter how the user phrases it.

**Fail safe** — if permission check fails, action doesn't execute. If LLM is down, wake word still works. If STT fails, fallback to text input.

**Auditability** — every action logged with timestamp, intent classification, risk level, permission decision, and outcome. Full history queryable.

---

## What This Demonstrates in Interviews

- Multi-agent system design with real orchestration
- MCP integration for OS-level tool access
- Permission-gated action execution (not just prompt-based)
- Voice pipeline with offline components
- Vector DB + Knowledge Graph for different memory needs
- Production patterns — callbacks, guardrails, retries, human in the loop
- Privacy-conscious architecture decisions
- Cross-platform thinking (Linux first, Windows next)