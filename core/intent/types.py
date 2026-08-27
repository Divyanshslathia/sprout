"""
Intent Type and Risk Level definitions
"""
from enum import Enum

class IntentType(Enum):
    """Classification of user intent"""
    INFORMATION = "INFORMATION"  # Questions, lookups
    SYSTEM_ACTION = "SYSTEM_ACTION"  # OS-level actions
    FILE_OPERATION = "FILE_OPERATION"  # File read/write/delete
    APPLICATION_CONTROL = "APPLICATION_CONTROL"  # Open/close apps
    TERMINAL_OPERATION = "TERMINAL_OPERATION"  # Run commands
    CONVERSATION = "CONVERSATION"  # Chat, memory recall

class RiskLevel(Enum):
    """Risk assessment for actions"""
    SAFE = "SAFE"  # Execute immediately
    SENSITIVE = "SENSITIVE"  # Ask for confirmation
    DESTRUCTIVE = "DESTRUCTIVE"  # Hard stop, explicit confirm
