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
            action: Action to perform (search, answer, recall, etc.)
            params: Parameters for the action

        Returns:
            Result dictionary
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
                "message": answer,  # changed from "answer" to "message"
                "source": "llm"
            }
        elif action == "recall_action":
            # Search action history
            query = params.get('query', '')
            actions = self.action_history.search_actions(query)
            return {
                "success": True,
                "actions": actions,
                "count": len(actions)
            }

        else:
            return {"success": False, "message": f"Unknown action: {action}"}

    def _init_llm(self):
        """Initialize Gemini for answering questions"""
        try:
            import google.generativeai as genai
            import os
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                self.llm = genai.GenerativeModel('gemini-3.5-flash')
            else:
                self.llm = None
        except Exception:
            self.llm = None
    def _generate_answer(self, question: str) -> str:
        question_lower = question.lower()

        # Handle time/date locally — no LLM needed
        if "time" in question_lower:
            from datetime import datetime
            return f"The current time is {datetime.now().strftime('%H:%M:%S')}"

        elif "date" in question_lower:
            from datetime import datetime
            return f"Today is {datetime.now().strftime('%A, %B %d, %Y')}"

        elif any(w in question_lower for w in ["who are you", "what are you"]):
            return "I'm Sprout, your personal AI assistant. I can open apps, manage files, run commands and answer questions."

        # Use Gemini for everything else
        if self.llm:
            try:
                response = self.llm.generate_content(
                    f"You are Sprout, a personal AI assistant. Answer concisely in 1-2 sentences: {question}"
                )
                return response.text.strip()
            except Exception as e:
                return f"I couldn't answer that: {e}"

        return "I don't have an answer for that. Try searching the web."