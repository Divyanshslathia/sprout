"""
RAG (Retrieval-Augmented Generation) System

Combines vector search with LLM for personalized responses
"""
import concurrent.futures
from datetime import datetime
from typing import Optional, Dict

from core.memory.vector_store import VectorStore
from core.memory.history import ActionHistory

# Temporal keywords that can be answered from SQLite without vector search
TEMPORAL_QUERY_KEYWORDS = ["today", "yesterday", "did i", "what did", "recent", "last time", "earlier"]

VECTOR_SEARCH_TIMEOUT_SECONDS = 3


class RAGSystem:
    """RAG system for personalized, context-aware responses"""

    def __init__(self, vector_store: VectorStore, llm_parser=None):
        self.vector_store = vector_store
        self.llm_parser = llm_parser
        self.action_history = ActionHistory()

    def get_personalized_context(self, query: str) -> Dict[str, any]:
        """
        Retrieve relevant context for a query.

        Uses a fast SQLite path for temporal queries and falls back to
        vector search for semantic queries, with a timeout to prevent hangs.
        """
        context = {
            "conversations": [],
            "preferences": [],
            "actions": [],
            "patterns": []
        }

        # Fast path: temporal queries answered directly from SQLite
        if self._is_temporal_query(query):
            context["actions"] = self._get_todays_actions()
            context["patterns"] = self._analyze_patterns(query)
            return context

        # Slow path: full vector search with timeout
        context["conversations"] = self._search_with_timeout(
            lambda: self.vector_store.search_conversations(query, n_results=3)
        )
        context["preferences"] = self._search_with_timeout(
            lambda: self.vector_store.search_preferences(query, n_results=2)
        )
        context["actions"] = self._search_with_timeout(
            lambda: self.vector_store.search_actions(query, n_results=3)
        )
        context["patterns"] = self._analyze_patterns(query)

        return context

    def _is_temporal_query(self, query: str) -> bool:
        """Return True if the query is asking about recent history"""
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in TEMPORAL_QUERY_KEYWORDS)

    def _get_todays_actions(self) -> list:
        """Fetch today's actions directly from SQLite — fast, no embeddings"""
        today = datetime.now().strftime("%Y-%m-%d")
        recent = self.action_history.get_recent_actions(limit=50)
        todays = [
            a for a in recent
            if a.get("timestamp", "").startswith(today)
        ]
        # Format into the same shape vector search returns
        return [{"text": f"{a.get('action', '')} {a.get('target', '')}", "metadata": a}
                for a in todays]

    def _search_with_timeout(self, search_fn) -> list:
        """
        Run a vector search with a timeout.
        Returns empty list if search times out or fails.
        """
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(search_fn)
                return future.result(timeout=VECTOR_SEARCH_TIMEOUT_SECONDS)
        except concurrent.futures.TimeoutError:
            print(f"[RAG] Vector search timed out after {VECTOR_SEARCH_TIMEOUT_SECONDS}s")
            return []
        except Exception as e:
            print(f"[RAG] Vector search failed: {e}")
            return []

    def _analyze_patterns(self, query: str) -> list:
        """Analyze user behavior patterns from recent action history"""
        patterns = []
        recent_actions = self.action_history.get_recent_actions(limit=20)

        if not recent_actions:
            return patterns

        # App usage frequency
        app_counts = {}
        for action in recent_actions:
            if action["intent_type"] == "APPLICATION_CONTROL":
                app = action.get("target", "")
                app_counts[app] = app_counts.get(app, 0) + 1

        if app_counts:
            most_used_app = max(app_counts, key=app_counts.get)
            patterns.append(f"Frequently uses: {most_used_app}")

        # Success rate warning
        successful = [a for a in recent_actions if a.get("success")]
        if len(successful) / len(recent_actions) < 0.7:
            patterns.append("Some actions have been failing recently")

        # Heavy file operations
        file_ops = [a for a in recent_actions if a["intent_type"] == "FILE_OPERATION"]
        if len(file_ops) > len(recent_actions) * 0.3:
            patterns.append("Heavy file operations recently")

        return patterns

    def generate_personalized_response(self, query: str, system_response: str) -> str:
        """Generate a personalized response using context and LLM"""
        context = self.get_personalized_context(query)
        context_str = self._format_context(context)

        if self.llm_parser and hasattr(self.llm_parser, 'enhance_response'):
            return self.llm_parser.enhance_response(query, system_response, context_str)

        if context["patterns"]:
            return f"{system_response}\n\n💡 {context['patterns'][0]}"

        return system_response

    def _format_context(self, context: Dict) -> str:
        """Format context dict into a readable string for the LLM"""
        parts = []

        if context["preferences"]:
            prefs = [p["text"] for p in context["preferences"][:2]]
            parts.append(f"User preferences: {'; '.join(prefs)}")

        if context["patterns"]:
            parts.append(f"Patterns: {'; '.join(context['patterns'][:2])}")

        if context["conversations"]:
            recent = context["conversations"][0]["text"]
            parts.append(f"Recent context: {recent[:100]}")

        return " | ".join(parts)

    def learn_from_interaction(self, user_input: str, system_response: str,
                               success: bool, feedback: Optional[str] = None):
        """Learn from a user interaction by storing it in memory"""
        self.vector_store.add_conversation(user_input, "user")
        self.vector_store.add_conversation(
            system_response, "assistant", metadata={"success": success}
        )

        if feedback and any(w in feedback.lower() for w in ["prefer", "like"]):
            self.vector_store.add_preference(feedback, category="behavior")

    def get_recommendations(self, context: str = "") -> list:
        """Get action recommendations based on recent behavior and time of day"""
        recommendations = []
        recent_actions = self.action_history.get_recent_actions(limit=10)

        if not recent_actions:
            return ["No recent activity to base recommendations on"]

        current_hour = datetime.now().hour
        if 9 <= current_hour < 12:
            recommendations.append("Good morning! Ready to start working?")
        elif 14 <= current_hour < 18:
            recommendations.append("Afternoon session — need any files or apps?")

        failed = [a for a in recent_actions if not a.get("success")]
        if len(failed) > 3:
            recommendations.append("Several actions failed recently — need help?")

        app_actions = [a for a in recent_actions if a["intent_type"] == "APPLICATION_CONTROL"]
        if len(app_actions) > 5:
            app_counts = {}
            for action in app_actions:
                app = action.get("target", "")
                app_counts[app] = app_counts.get(app, 0) + 1
            top_app = max(app_counts, key=app_counts.get)
            recommendations.append(f"You often use {top_app} — want me to open it?")

        return recommendations[:3]

    def search_memory(self, query: str) -> str:
        """Search across all memory systems and return formatted results"""
        context = self.get_personalized_context(query)
        results = []

        if context["conversations"]:
            results.append("## Recent Conversations:")
            for conv in context["conversations"][:3]:
                role = conv["metadata"].get("role", "")
                results.append(f"  [{role}] {conv['text'][:100]}")

        if context["preferences"]:
            results.append("\n## Preferences:")
            for pref in context["preferences"]:
                results.append(f"  • {pref['text']}")

        if context["actions"]:
            results.append("\n## Past Actions:")
            for action in context["actions"][:3]:
                results.append(f"  • {action['text'][:100]}")

        if context["patterns"]:
            results.append("\n## Patterns:")
            for pattern in context["patterns"]:
                results.append(f"  • {pattern}")

        return "\n".join(results) if results else "No relevant memories found."
