"""
Research Agent

Handles information queries, web searches, and general questions
"""
from typing import Dict, Any
from core.tools.web_tools import WebTools
from core.memory.history import ActionHistory

class ResearchAgent:
    """Agent for information retrieval and research"""

    def __init__(self):
        self.web_tools = WebTools()
        self.action_history = ActionHistory()
        self._init_llm()

    def execute(self, action: str, params: Dict[str, Any]) -> Dict:
        """
        Execute a research action

        Args:
            action: Action to perform (search_web, answer_question, recall_action)
            params: Parameters for the action

        Returns:
            Result dictionary with at minimum: success, message
        """
        if action == "search_web":
            query = params.get('query', '')
            return self.web_tools.search_web(query)

        elif action == "open_url":
            url = params.get('url', '')
            return self.web_tools.open_url(url)

        elif action == "answer_question":
            question = params.get('question', params.get('query', ''))
            answer = self._generate_answer(question)
            return {
                "success": True,
                "message": answer,
                "source": "llm"
            }
        elif action == "recall_action":
            query = params.get('query', '')
            actions = self.action_history.search_actions(query)
            summary = f"Found {len(actions)} past actions" if actions else "No matching actions found"
            return {
                "success": True,
                "message": summary,
                "actions": actions,
                "count": len(actions)
            }

        else:
            return {"success": False, "message": f"Unknown action: {action}"}

    def _init_llm(self):
        """Initialize Gemini for answering questions"""
        try:
            import os
            from google import genai
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                self._client = genai.Client(api_key=api_key)
                self.llm = True  # flag that LLM is available
            else:
                self._client = None
                self.llm = None
        except Exception:
            self._client = None
            self.llm = None
    def _generate_answer(self, question: str) -> str:
        """Generate an answer using local logic or Gemini"""
        question_lower = question.lower()

        # Handle time/date locally — no LLM needed
        if "time" in question_lower:
            from datetime import datetime
            return f"The current time is {datetime.now().strftime('%H:%M:%S')}"

        if "date" in question_lower:
            from datetime import datetime
            return f"Today is {datetime.now().strftime('%A, %B %d, %Y')}"

        if any(phrase in question_lower for phrase in ["who are you", "what are you"]):
            return "I'm Sprout, your personal AI assistant. I can open apps, manage files, run commands, and answer questions."

        # Use Gemini for everything else
        if self.llm:
            try:
                response = self._client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=f"You are Sprout, a personal AI assistant. Answer concisely in 1-2 sentences: {question}"
                )
                return response.text.strip()
            except Exception as e:
                return f"I couldn't answer that: {e}"

        return "LLM unavailable — set GEMINI_API_KEY to enable answers."