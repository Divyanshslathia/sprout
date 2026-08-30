"""
LLM-powered Intent Parser using Gemini

Advanced intent classification and action parsing using LLM
"""
import os
import json
from typing import Dict, Tuple, Optional

from core.intent.types import IntentType, RiskLevel

class LLMIntentParser:
    """LLM-based intent classification and parameter extraction"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = None
        self._initialize_model()

    def _initialize_model(self):
        """Initialize Gemini model"""
        if not self.api_key:
            print("Warning: GEMINI_API_KEY not set. Using fallback keyword parser.")
            return

        try:
            from google import genai
            self._client = genai.Client(api_key=self.api_key)
            self.model = True  # flag that LLM is available
            print("✓ Gemini LLM initialized")
        except ImportError:
            print("Warning: google-genai not installed. Run: pip install google-genai")
        except Exception as e:
            print(f"Warning: Failed to initialize Gemini: {str(e)}")

    def parse_intent(self, user_input: str) -> Tuple[IntentType, RiskLevel, str, Dict]:
        """
        Parse user input using LLM to extract intent, risk, action, and parameters

        Returns:
            Tuple of (IntentType, RiskLevel, action_str, parameters_dict)
        """
        if not self.model:
            return self._fallback_parse(user_input)

        try:
            prompt = f"""Analyze this user command and extract intent, risk level, and parameters.

User command: "{user_input}"

Respond with JSON only, no markdown:
{{
  "intent_type": "one of: INFORMATION, SYSTEM_ACTION, FILE_OPERATION, APPLICATION_CONTROL, TERMINAL_OPERATION, CONVERSATION",
  "risk_level": "one of: SAFE, SENSITIVE, DESTRUCTIVE",
  "action": "one of: open_app, close_app, run_command, take_screenshot, get_clipboard, set_clipboard, read, write, delete, list, search_web, answer_question, recall_action",
  "parameters": {{
    "key": "value"
  }},
  "reasoning": "brief explanation"
}}

Intent guidelines:
- INFORMATION: questions, searches, lookups
- SYSTEM_ACTION: OS operations (screenshot, clipboard)
- FILE_OPERATION: file/directory operations
- APPLICATION_CONTROL: open/close apps
- TERMINAL_OPERATION: run shell commands
- CONVERSATION: chat, greetings, memory recall

Risk guidelines:
- SAFE: no system changes (questions, reads, greetings)
- SENSITIVE: reversible changes (open app, write file)
- DESTRUCTIVE: dangerous operations (delete, system modifications)

Parameter format by action:
- open_app / close_app: {{"app_name": "..."}}
- run_command: {{"command": "..."}}
- read / write / delete / list: {{"filepath": "..."}}
- search_web: {{"query": "..."}}
- answer_question: {{"question": "..."}}
- recall_action: {{"query": "..."}}"""

            response = self._client.models.generate_content(
                model='gemini-3.6-flash',
                contents=prompt
            )
            text = self._strip_markdown(response.text)
            result = json.loads(text)

            intent_type = IntentType[result["intent_type"]]
            risk_level = RiskLevel[result["risk_level"]]
            action = result["action"]
            parameters = result.get("parameters", {})

            return intent_type, risk_level, action, parameters

        except Exception as e:
            print(f"LLM parsing failed: {str(e)}")
            return self._fallback_parse(user_input)

    def _strip_markdown(self, text: str) -> str:
        """Remove markdown code fences Gemini sometimes wraps responses in"""
        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            # drop first line (```json or ```) and last line (```)
            text = "\n".join(lines[1:-1])
        return text.strip()

    def _fallback_parse(self, user_input: str) -> Tuple[IntentType, RiskLevel, str, Dict]:
        """Fallback to keyword-based parsing when LLM is unavailable"""
        from core.intent.classifier import IntentClassifier

        classifier = IntentClassifier()
        intent_type, risk_level = classifier.classify(user_input)
        action = self._infer_action(user_input, intent_type)
        params = self._extract_basic_params(user_input, intent_type)

        return intent_type, risk_level, action, params

    def _extract_basic_params(self, text: str, intent_type: IntentType) -> Dict:
        """Basic parameter extraction without LLM"""
        words = text.lower().split()
        params = {}

        if intent_type == IntentType.APPLICATION_CONTROL:
            for i, word in enumerate(words):
                if word in ["open", "launch", "start", "close", "quit"]:
                    if i + 1 < len(words):
                        params["app_name"] = words[i + 1]
                    break

        elif intent_type == IntentType.FILE_OPERATION:
            for word in words:
                if "/" in word or word.startswith("~"):
                    params["filepath"] = word.strip("'\"")
                    break

        elif intent_type == IntentType.TERMINAL_OPERATION:
            for i, word in enumerate(words):
                if word in ["run", "execute", "command"]:
                    params["command"] = " ".join(text.split()[i + 1:])
                    break

        elif intent_type in [IntentType.INFORMATION, IntentType.CONVERSATION]:
            params["question"] = text

        return params

    def _infer_action(self, text: str, intent_type: IntentType) -> str:
        """Infer action from text and intent type"""
        text_lower = text.lower()

        if intent_type == IntentType.APPLICATION_CONTROL:
            if any(w in text_lower for w in ["open", "launch", "start"]):
                return "open_app"
            if any(w in text_lower for w in ["close", "quit", "kill"]):
                return "close_app"

        elif intent_type == IntentType.FILE_OPERATION:
            if "read" in text_lower:
                return "read"
            if "write" in text_lower or "create" in text_lower:
                return "write"
            if "delete" in text_lower or "remove" in text_lower:
                return "delete"
            if "list" in text_lower:
                return "list"

        elif intent_type == IntentType.TERMINAL_OPERATION:
            return "run_command"

        elif intent_type == IntentType.INFORMATION:
            if "search" in text_lower:
                return "search_web"
            return "answer_question"

        elif intent_type == IntentType.CONVERSATION:
            if any(w in text_lower for w in ["remember", "recall", "what did"]):
                return "recall_action"
            return "answer_question"

        return "answer_question"

    def enhance_response(self, user_input: str, raw_response: str, context: str = "") -> str:
        """
        Use LLM to generate a natural, friendly response

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

Reply in 1-2 sentences. Be friendly and conversational. Don't repeat technical details."""

            response = self._client.models.generate_content(
                model='gemini-3.6-flash',
                contents=prompt
            )
            return response.text.strip()

        except Exception as e:
            print(f"Response enhancement failed: {str(e)}")
            return raw_response
        