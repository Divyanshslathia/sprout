"""
LLM-powered Intent Parser using Gemini

Advanced intent classification and action parsing using LLM
"""
import os
from typing import Dict, Tuple, Optional
import json
from core.intent.types import IntentType, RiskLevel

class LLMIntentParser:
    """LLM-based intent classification and parameter extraction"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize LLM parser

        Args:
            api_key: Gemini API key
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = None
        self._initialize_model()

    def _initialize_model(self):
        """Lazy initialize Gemini model"""
        if not self.api_key:
            print("Warning: GEMINI_API_KEY not set. Using fallback keyword parser.")
            return

        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-3.5-flash')
            print("✓ Gemini LLM initialized")
        except ImportError:
            print("Warning: google-generativeai not installed. Install with: pip install google-generativeai")
        except Exception as e:
            print(f"Warning: Failed to initialize Gemini: {str(e)}")

    def parse_intent(self, user_input: str) -> Tuple[IntentType, RiskLevel, Dict]:
        """
        Parse user input using LLM to extract intent, risk, and parameters

        Args:
            user_input: Raw user command

        Returns:
            Tuple of (IntentType, RiskLevel, parameters_dict)
        """
        if not self.model:
            # Fallback to simple parsing
            return self._fallback_parse(user_input)

        try:
            prompt = f"""Analyze this user command and extract intent, risk level, and parameters.

User command: "{user_input}"

Respond with JSON only:
{{
  "intent_type": "one of: INFORMATION, SYSTEM_ACTION, FILE_OPERATION, APPLICATION_CONTROL, TERMINAL_OPERATION, CONVERSATION",
  "risk_level": "one of: SAFE, SENSITIVE, DESTRUCTIVE",
  "action": "specific action to take (e.g., open_app, read_file, search_web)",
  "parameters": {{
    "key": "value"
  }},
  "reasoning": "brief explanation"
}}

Guidelines:
- INFORMATION: questions, searches, lookups
- SYSTEM_ACTION: OS operations (screenshot, clipboard)
- FILE_OPERATION: file/directory operations
- APPLICATION_CONTROL: open/close apps
- TERMINAL_OPERATION: run commands
- CONVERSATION: chat, memory recall

- SAFE: no system changes (questions, reads)
- SENSITIVE: system changes that are reversible (open app, write file)
- DESTRUCTIVE: dangerous operations (delete, remove, system modifications)

Extract parameters based on intent:
- For app operations: {{"app_name": "..."}}
- For file operations: {{"filepath": "...", "content": "..."}}
- For terminal: {{"command": "..."}}
- For search: {{"query": "..."}}"""

            response = self.model.generate_content(prompt)
            # strip markdown code blocks if Gemini wraps response in them
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            text = text.strip()
            result = json.loads(text)

            # Convert strings to enums
            intent_type = IntentType[result["intent_type"]]
            risk_level = RiskLevel[result["risk_level"]]
            action = result["action"]
            parameters = result["parameters"]

            return intent_type, risk_level, action, parameters

        except Exception as e:
            print(f"LLM parsing failed: {str(e)}")
            return self._fallback_parse(user_input)

    def _fallback_parse(self, user_input: str) -> Tuple[IntentType, RiskLevel, str, Dict]:
        """Fallback to simple keyword-based parsing"""
        from core.intent.classifier import IntentClassifier

        classifier = IntentClassifier()
        intent_type, risk_level = classifier.classify(user_input)

        # Simple parameter extraction
        params = self._extract_basic_params(user_input, intent_type)
        action = self._infer_action(user_input, intent_type)

        return intent_type, risk_level, action, params

    def _extract_basic_params(self, text: str, intent_type: IntentType) -> Dict:
        """Basic parameter extraction without LLM"""
        words = text.lower().split()
        params = {}

        if intent_type == IntentType.APPLICATION_CONTROL:
            # Find app name after open/close/launch
            for i, word in enumerate(words):
                if word in ["open", "launch", "start", "close", "quit"]:
                    if i + 1 < len(words):
                        params["app_name"] = words[i + 1]
                    break

        elif intent_type == IntentType.FILE_OPERATION:
            # Extract filepath
            for word in words:
                if "/" in word or word.startswith("~"):
                    params["filepath"] = word.strip("'\"")
                    break

        elif intent_type == IntentType.TERMINAL_OPERATION:
            # Extract command after "run" or "execute"
            for i, word in enumerate(words):
                if word in ["run", "execute", "command"]:
                    params["command"] = " ".join(text.split()[i + 1:])
                    break

        elif intent_type == IntentType.INFORMATION:
            # Extract search query
            params["query"] = text

        return params

    def _infer_action(self, text: str, intent_type: IntentType) -> str:
        """Infer action from text and intent type"""
        text_lower = text.lower()

        if intent_type == IntentType.APPLICATION_CONTROL:
            if any(w in text_lower for w in ["open", "launch", "start"]):
                return "open_app"
            elif any(w in text_lower for w in ["close", "quit", "kill"]):
                return "close_app"

        elif intent_type == IntentType.FILE_OPERATION:
            if "read" in text_lower:
                return "read"
            elif "write" in text_lower or "create" in text_lower:
                return "write"
            elif "delete" in text_lower or "remove" in text_lower:
                return "delete"
            elif "list" in text_lower:
                return "list"

        elif intent_type == IntentType.TERMINAL_OPERATION:
            return "run_command"

        elif intent_type == IntentType.INFORMATION:
            if "search" in text_lower:
                return "search_web"
            else:
                return "answer_question"

        elif intent_type == IntentType.CONVERSATION:
            if "remember" in text_lower or "recall" in text_lower:
                return "recall_action"
            else:
                return "answer_question"

        return "unknown"

    def enhance_response(self, user_input: str, raw_response: str, context: str = "") -> str:
        """
        Use LLM to generate natural, personalized response

        Args:
            user_input: Original user command
            raw_response: Raw system response
            context: Additional context from memory

        Returns:
            Enhanced natural language response
        """
        if not self.model:
            return raw_response

        try:
            prompt = f"""Generate a natural, concise response for the user.

User asked: "{user_input}"
System result: {raw_response}
Context: {context}

Generate a brief, friendly response (1-2 sentences) that:
- Confirms what was done
- Is conversational and natural
- Doesn't repeat technical details
- Matches the tone of a personal assistant

Response:"""

            response = self.model.generate_content(prompt)
            return response.text.strip()

        except Exception as e:
            print(f"Response enhancement failed: {str(e)}")
            return raw_response
