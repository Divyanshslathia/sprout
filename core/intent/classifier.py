"""
Intent Classifier

Analyzes user input to determine intent type and risk level.
"""
from typing import Tuple
from core.intent.types import IntentType, RiskLevel

class IntentClassifier:
    """Classifies user intent and assesses risk"""

    # Keywords for intent detection
    INTENT_KEYWORDS = {
        IntentType.INFORMATION: ["what", "who", "when", "where", "why", "how", "search", "find", "tell me", "show me"],
        IntentType.SYSTEM_ACTION: ["open", "close", "launch", "quit", "kill", "screenshot", "clipboard"],
        IntentType.FILE_OPERATION: ["read", "write", "delete", "remove", "create", "edit", "file", "folder"],
        IntentType.APPLICATION_CONTROL: ["open", "start", "close", "quit", "app", "application"],
        IntentType.TERMINAL_OPERATION: ["run", "execute", "command", "terminal", "bash"],
        IntentType.CONVERSATION: ["remember", "recall", "what did", "yesterday", "last time"],
    }

    # Keywords for risk assessment
    DESTRUCTIVE_KEYWORDS = ["delete", "remove", "rm", "format", "destroy", "kill", "wipe"]
    SENSITIVE_KEYWORDS = ["send", "message", "post", "upload", "install", "download", "modify"]

    def classify(self, user_input: str) -> Tuple[IntentType, RiskLevel]:
        """
        Classify intent type and risk level from user input

        Args:
            user_input: Raw user command

        Returns:
            Tuple of (IntentType, RiskLevel)
        """
        user_input_lower = user_input.lower()

        # Determine intent type
        intent_type = self._classify_intent(user_input_lower)

        # Determine risk level
        risk_level = self._classify_risk(user_input_lower, intent_type)

        return intent_type, risk_level

    def _classify_intent(self, text: str) -> IntentType:
        """Determine the intent type based on keywords"""
        scores = {intent: 0 for intent in IntentType}

        for intent, keywords in self.INTENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    scores[intent] += 1

        # Return intent with highest score, default to CONVERSATION
        if max(scores.values()) == 0:
            return IntentType.CONVERSATION

        return max(scores, key=scores.get)

    def _classify_risk(self, text: str, intent_type: IntentType) -> RiskLevel:
        
        # Split into words for exact matching — prevents "rm" matching "terminal"
        words = text.split()
        
        # Destructive keywords — check whole words only
        for keyword in self.DESTRUCTIVE_KEYWORDS:
            if keyword in words:  # "in words" not "in text"
                return RiskLevel.DESTRUCTIVE

        # Terminal commands are sensitive by default
        if intent_type == IntentType.TERMINAL_OPERATION:
            return RiskLevel.SENSITIVE

        # File operations — only sensitive if modifying
        if intent_type == IntentType.FILE_OPERATION:
            for keyword in self.SENSITIVE_KEYWORDS:
                if keyword in text:
                    return RiskLevel.SENSITIVE
            return RiskLevel.SAFE

        # System actions — open/close/launch are SAFE
        if intent_type == IntentType.SYSTEM_ACTION:
            for keyword in self.SENSITIVE_KEYWORDS:
                if keyword in text:
                    return RiskLevel.SENSITIVE
            return RiskLevel.SAFE

        return RiskLevel.SAFE