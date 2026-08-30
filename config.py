"""
Sprout Configuration

All system settings, paths, and model configurations.
"""
import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# LLM Configuration
class LLMConfig(BaseModel):
    model_name: str = "gemini-3.5-flash"
    temperature: float = 0.7
    max_tokens: int = 2048

# Memory Configuration
class MemoryConfig(BaseModel):
    session_db_path: str = str(DATA_DIR / "session.db")
    vector_db_path: str = str(DATA_DIR / "chroma")
    action_log_path: str = str(DATA_DIR / "actions.db")

# Permission Configuration
class PermissionConfig(BaseModel):
    policy_file: str = str(DATA_DIR / "permissions.json")
    auto_allow_safe: bool = True
    require_confirm_sensitive: bool = True
    block_destructive: bool = True

# Voice Configuration (Phase 2)
class VoiceConfig(BaseModel):
    wake_word: str = "sprout"
    whisper_model: str = "tiny"
    wake_word_threshold: float = 0.5
    wake_word_model: str = "hey_jarvis"  # replace with path to hey_sprout.tflite later
    tts_rate: int = 150

# System settings
llm_config = LLMConfig()
memory_config = MemoryConfig()
permission_config = PermissionConfig()
voice_config = VoiceConfig()

# Intent types
class IntentType:
    INFORMATION = "INFORMATION"
    SYSTEM_ACTION = "SYSTEM_ACTION"
    FILE_OPERATION = "FILE_OPERATION"
    APPLICATION_CONTROL = "APPLICATION_CONTROL"
    TERMINAL_OPERATION = "TERMINAL_OPERATION"
    CONVERSATION = "CONVERSATION"

# Risk levels
class RiskLevel:
    SAFE = "SAFE"
    SENSITIVE = "SENSITIVE"
    DESTRUCTIVE = "DESTRUCTIVE"
