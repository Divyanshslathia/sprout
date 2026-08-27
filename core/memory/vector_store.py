"""
Vector Store using ChromaDB

Semantic memory for conversation history and user preferences
"""
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
from config import memory_config

class VectorStore:
    """Semantic memory using ChromaDB for embedding-based search"""

    def __init__(self, persist_directory: Optional[str] = None):
        """
        Initialize ChromaDB vector store

        Args:
            persist_directory: Directory to persist the database
        """
        self.persist_directory = persist_directory or memory_config.vector_db_path
        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB client
        self.client = chromadb.Client(Settings(
            persist_directory=self.persist_directory,
            anonymized_telemetry=False
        ))

        # Create collections
        self.conversations = self._get_or_create_collection("conversations")
        self.preferences = self._get_or_create_collection("preferences")
        self.actions = self._get_or_create_collection("actions")

    def _get_or_create_collection(self, name: str):
        """Get or create a collection"""
        try:
            return self.client.get_collection(name=name)
        except:
            return self.client.create_collection(
                name=name,
                metadata={"hnsw:space": "cosine"}
            )

    def add_conversation(self, text: str, role: str, metadata: Optional[Dict] = None):
        """
        Add conversation message to vector store

        Args:
            text: Message text
            role: 'user' or 'assistant'
            metadata: Optional metadata dict
        """
        doc_id = f"conv_{datetime.now().timestamp()}"

        meta = {
            "role": role,
            "timestamp": datetime.now().isoformat(),
            **(metadata or {})
        }

        self.conversations.add(
            documents=[text],
            metadatas=[meta],
            ids=[doc_id]
        )

    def add_preference(self, preference: str, category: str = "general"):
        """
        Store user preference

        Args:
            preference: Preference description
            category: Category (e.g., 'apps', 'behavior', 'general')
        """
        doc_id = f"pref_{category}_{datetime.now().timestamp()}"

        self.preferences.add(
            documents=[preference],
            metadatas=[{
                "category": category,
                "timestamp": datetime.now().isoformat()
            }],
            ids=[doc_id]
        )

    def add_action_memory(self, action: str, result: str, success: bool):
        """
        Store action and its result

        Args:
            action: Action description
            result: Result description
            success: Whether action succeeded
        """
        doc_id = f"action_{datetime.now().timestamp()}"

        combined_text = f"{action} -> {result}"

        self.actions.add(
            documents=[combined_text],
            metadatas=[{
                "action": action,
                "result": result,
                "success": success,
                "timestamp": datetime.now().isoformat()
            }],
            ids=[doc_id]
        )

    def search_conversations(self, query: str, n_results: int = 5) -> List[Dict]:
        """
        Search conversation history by semantic similarity

        Args:
            query: Search query
            n_results: Number of results to return

        Returns:
            List of matching conversations with metadata
        """
        results = self.conversations.query(
            query_texts=[query],
            n_results=n_results
        )

        return self._format_results(results)

    def search_preferences(self, query: str, n_results: int = 3) -> List[Dict]:
        """Search user preferences"""
        results = self.preferences.query(
            query_texts=[query],
            n_results=n_results
        )

        return self._format_results(results)

    def search_actions(self, query: str, n_results: int = 5) -> List[Dict]:
        """Search past actions"""
        results = self.actions.query(
            query_texts=[query],
            n_results=n_results
        )

        return self._format_results(results)

    def _format_results(self, results: Dict) -> List[Dict]:
        """Format ChromaDB results into clean dict list"""
        formatted = []

        if not results['documents'] or not results['documents'][0]:
            return formatted

        docs = results['documents'][0]
        metadatas = results['metadatas'][0]
        distances = results['distances'][0] if 'distances' in results else [0] * len(docs)

        for doc, meta, distance in zip(docs, metadatas, distances):
            formatted.append({
                "text": doc,
                "metadata": meta,
                "similarity": 1 - distance  # Convert distance to similarity
            })

        return formatted

    def get_relevant_context(self, query: str, max_items: int = 5) -> str:
        """
        Get relevant context for a query from all collections

        Args:
            query: User query
            max_items: Maximum items to retrieve

        Returns:
            Formatted context string
        """
        context_parts = []

        # Search conversations
        conv_results = self.search_conversations(query, n_results=max_items)
        if conv_results:
            context_parts.append("## Recent Related Conversations:")
            for item in conv_results[:3]:
                role = item['metadata'].get('role', 'unknown')
                context_parts.append(f"- [{role}] {item['text']}")

        # Search preferences
        pref_results = self.search_preferences(query, n_results=2)
        if pref_results:
            context_parts.append("\n## User Preferences:")
            for item in pref_results:
                context_parts.append(f"- {item['text']}")

        # Search actions
        action_results = self.search_actions(query, n_results=3)
        if action_results:
            context_parts.append("\n## Related Past Actions:")
            for item in action_results:
                context_parts.append(f"- {item['text']}")

        return "\n".join(context_parts) if context_parts else ""

    def get_collection_stats(self) -> Dict:
        """Get statistics about stored data"""
        return {
            "conversations": self.conversations.count(),
            "preferences": self.preferences.count(),
            "actions": self.actions.count(),
            "total_memories": (
                self.conversations.count() +
                self.preferences.count() +
                self.actions.count()
            )
        }

    def clear_collection(self, collection_name: str):
        """Clear a specific collection"""
        try:
            self.client.delete_collection(name=collection_name)
            setattr(self, collection_name, self._get_or_create_collection(collection_name))
        except:
            pass

    def reset_all(self):
        """Reset all collections (dangerous!)"""
        for name in ["conversations", "preferences", "actions"]:
            self.clear_collection(name)
