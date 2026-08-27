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
            # For Phase 1, provide basic responses
            question = params.get('question', '')
            return {
                "success": True,
                "answer": self._generate_answer(question),
                "source": "local_knowledge"
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

    def _generate_answer(self, question: str) -> str:
        """
        Generate a basic answer to a question

        Note: In Phase 3, this will be enhanced with RAG and LLM integration
        """
        question_lower = question.lower()

        # Basic pattern matching for common questions
        if "weather" in question_lower:
            return "I can open a weather website for you. Which city would you like to check?"

        elif "time" in question_lower:
            from datetime import datetime
            return f"The current time is {datetime.now().strftime('%H:%M:%S')}"

        elif "date" in question_lower:
            from datetime import datetime
            return f"Today is {datetime.now().strftime('%A, %B %d, %Y')}"

        elif "who are you" in question_lower or "what are you" in question_lower:
            return "I'm Sprout, your personal AI assistant. I can help you control your computer, manage files, and answer questions."

        elif "help" in question_lower:
            return """I can help you with:
- Opening and closing applications
- Managing files (read, write, delete)
- Running terminal commands
- Searching the web
- Answering basic questions
- Taking screenshots and managing clipboard

Just ask me naturally, like "open terminal" or "search for Python tutorials"."""

        else:
            return "I'll search the web for that information. Let me open a browser search for you."
