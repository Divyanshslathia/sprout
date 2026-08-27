"""
RAG (Retrieval-Augmented Generation) System

Combines vector search with LLM for personalized responses
"""
from typing import Optional, Dict
from core.memory.vector_store import VectorStore
from core.memory.history import ActionHistory

class RAGSystem:
    """RAG system for personalized, context-aware responses"""

    def __init__(self, vector_store: VectorStore, llm_parser=None):
        """
        Initialize RAG system

        Args:
            vector_store: ChromaDB vector store
            llm_parser: Optional LLM parser for generation
        """
        self.vector_store = vector_store
        self.llm_parser = llm_parser
        self.action_history = ActionHistory()

    def get_personalized_context(self, query: str) -> Dict[str, any]:
        """
        Retrieve relevant context for a query

        Args:
            query: User query

        Returns:
            Dictionary with relevant context
        """
        context = {
            "conversations": [],
            "preferences": [],
            "actions": [],
            "patterns": []
        }

        # Get semantic search results
        context["conversations"] = self.vector_store.search_conversations(query, n_results=3)
        context["preferences"] = self.vector_store.search_preferences(query, n_results=2)
        context["actions"] = self.vector_store.search_actions(query, n_results=3)

        # Get behavioral patterns
        context["patterns"] = self._analyze_patterns(query)

        return context

    def _analyze_patterns(self, query: str) -> list:
        """
        Analyze user behavior patterns

        Args:
            query: User query

        Returns:
            List of detected patterns
        """
        patterns = []

        # Get recent actions from SQLite
        recent_actions = self.action_history.get_recent_actions(limit=20)

        if not recent_actions:
            return patterns

        # Analyze app usage patterns
        app_counts = {}
        for action in recent_actions:
            if action["intent_type"] == "APPLICATION_CONTROL":
                app = action.get("target", "")
                app_counts[app] = app_counts.get(app, 0) + 1

        if app_counts:
            most_used_app = max(app_counts, key=app_counts.get)
            patterns.append(f"Frequently uses: {most_used_app}")

        # Analyze time patterns (if we had timestamps in detail)
        successful_actions = [a for a in recent_actions if a.get("success")]
        if len(successful_actions) / len(recent_actions) < 0.7:
            patterns.append("Some actions have been failing recently")

        # Analyze file operation patterns
        file_ops = [a for a in recent_actions if a["intent_type"] == "FILE_OPERATION"]
        if len(file_ops) > len(recent_actions) * 0.3:
            patterns.append("Heavy file operations recently")

        return patterns

    def generate_personalized_response(self, query: str, system_response: str) -> str:
        """
        Generate a personalized response using context and LLM

        Args:
            query: User query
            system_response: Raw system response

        Returns:
            Personalized response
        """
        # Get context
        context = self.get_personalized_context(query)

        # Build context string
        context_str = self._format_context(context)

        # Use LLM to generate personalized response
        if self.llm_parser and hasattr(self.llm_parser, 'enhance_response'):
            return self.llm_parser.enhance_response(query, system_response, context_str)

        # Fallback: return system response with context hint
        if context["patterns"]:
            return f"{system_response}\n\n💡 {context['patterns'][0]}"

        return system_response

    def _format_context(self, context: Dict) -> str:
        """Format context into a readable string"""
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
        """
        Learn from user interaction

        Args:
            user_input: User's input
            system_response: System's response
            success: Whether the interaction was successful
            feedback: Optional user feedback
        """
        # Store conversation in vector DB
        self.vector_store.add_conversation(user_input, "user")
        self.vector_store.add_conversation(system_response, "assistant",
                                          metadata={"success": success})

        # Extract and store preferences from feedback
        if feedback:
            if "prefer" in feedback.lower() or "like" in feedback.lower():
                self.vector_store.add_preference(feedback, category="behavior")

    def get_recommendations(self, context: str = "") -> list:
        """
        Get action recommendations based on context

        Args:
            context: Optional context string

        Returns:
            List of recommended actions
        """
        recommendations = []

        # Get recent patterns
        recent_actions = self.action_history.get_recent_actions(limit=10)

        if not recent_actions:
            return ["No recent activity to base recommendations on"]

        # Time-based recommendations
        from datetime import datetime
        current_hour = datetime.now().hour

        if 9 <= current_hour < 12:
            recommendations.append("Good morning! Ready to start working?")
        elif 14 <= current_hour < 18:
            recommendations.append("Afternoon session - need any files or apps?")

        # Failure-based recommendations
        failed = [a for a in recent_actions if not a.get("success")]
        if len(failed) > 3:
            recommendations.append("Several actions failed recently - need help?")

        # Pattern-based recommendations
        app_actions = [a for a in recent_actions if a["intent_type"] == "APPLICATION_CONTROL"]
        if len(app_actions) > 5:
            frequently_used = {}
            for action in app_actions:
                app = action.get("target", "")
                frequently_used[app] = frequently_used.get(app, 0) + 1

            if frequently_used:
                top_app = max(frequently_used, key=frequently_used.get)
                recommendations.append(f"You often use {top_app} - want me to open it?")

        return recommendations[:3]  # Return top 3

    def search_memory(self, query: str) -> str:
        """
        Search across all memory systems

        Args:
            query: Search query

        Returns:
            Formatted search results
        """
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
