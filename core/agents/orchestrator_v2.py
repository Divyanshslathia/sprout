"""
Enhanced Orchestrator Agent (Phase 2 & 3)

Integrates voice, semantic memory, knowledge graph, and LLM parsing
"""
from typing import Dict, Any, Optional
from rich.console import Console
from rich.prompt import Confirm

from core.intent.classifier import IntentClassifier
from core.intent.types import IntentType, RiskLevel
from core.permissions.policy import PermissionPolicy
from core.permissions.graph import KnowledgeGraph
from core.agents.system_agent import SystemAgent
from core.agents.file_agent import FileAgent
from core.agents.research_agent import ResearchAgent
from core.callbacks import SproutCallbacks, SafetyGuardrails
from core.memory.session import SessionMemory
from core.memory.vector_store import VectorStore
from core.llm_parser import LLMIntentParser
from core.rag import RAGSystem

console = Console()

class EnhancedOrchestrator:
    """
    Enhanced orchestrator with Phase 2 & 3 features

    New capabilities:
    - LLM-based intent parsing (Gemini)
    - Semantic memory search (ChromaDB)
    - Knowledge graph permissions (Neo4j/NetworkX)
    - RAG for personalized responses
    - Behavior learning
    """

    def __init__(self, use_llm: bool = True, use_knowledge_graph: bool = True):
        """
        Initialize enhanced orchestrator

        Args:
            use_llm: Whether to use Gemini LLM (requires API key)
            use_knowledge_graph: Whether to use knowledge graph for permissions
        """
        # Initialize components
        self.callbacks = SproutCallbacks()
        self.guardrails = SafetyGuardrails()
        self.session_memory = SessionMemory()

        # Phase 3: Semantic memory
        console.print("[dim]Initializing semantic memory...[/dim]")
        self.vector_store = VectorStore()

        # Phase 3: LLM parser
        if use_llm:
            console.print("[dim]Initializing LLM parser...[/dim]")
            self.llm_parser = LLMIntentParser()
            self.use_llm = self.llm_parser.model is not None
        else:
            self.llm_parser = None
            self.use_llm = False

        # Fallback to keyword classifier
        self.intent_classifier = IntentClassifier()

        # Phase 3: RAG system
        self.rag_system = RAGSystem(self.vector_store, self.llm_parser)

        # Permission systems
        if use_knowledge_graph:
            console.print("[dim]Initializing knowledge graph...[/dim]")
            self.knowledge_graph = KnowledgeGraph(use_neo4j=False)  # NetworkX fallback
            self.use_knowledge_graph = True
        else:
            self.knowledge_graph = None
            self.use_knowledge_graph = False

        self.permission_policy = PermissionPolicy()

        # Initialize specialist agents
        self.system_agent = SystemAgent(self.permission_policy)
        self.file_agent = FileAgent(self.permission_policy)
        self.research_agent = ResearchAgent()

        # Create or get active session
        self.session_id = self.session_memory.get_active_session()
        if not self.session_id:
            self.session_id = self.session_memory.create_session()

        # Display initialization status
        self._display_initialization_status()

    def _display_initialization_status(self):
        """Display what features are active"""
        features = []
        if self.use_llm:
            features.append("✓ LLM Parser (Gemini)")
        else:
            features.append("○ LLM Parser (keyword fallback)")

        if self.use_knowledge_graph:
            features.append("✓ Knowledge Graph")
        else:
            features.append("○ Knowledge Graph")

        features.append("✓ Semantic Memory (ChromaDB)")
        features.append("✓ RAG System")

        console.print(f"[green]Active features: {' | '.join(features)}[/green]\n")

    def process(self, user_input: str) -> Dict[str, Any]:
        """
        Process user input through enhanced pipeline

        Args:
            user_input: Raw user command or question

        Returns:
            Result dictionary with success status and message
        """
        console.print(f"\n[bold cyan]You:[/bold cyan] {user_input}\n")

        # Save user message
        self.session_memory.add_message(self.session_id, "user", user_input)
        self.vector_store.add_conversation(user_input, "user")

        # Step 1: Safety guardrails
        is_safe, reason = self.guardrails.check_input_safety(user_input)
        if not is_safe:
            result = {
                "success": False,
                "message": f"🛑 Safety check failed: {reason}",
                "blocked": True
            }
            console.print(f"[red]{result['message']}[/red]")
            return result

        # Step 2: Classify intent and risk (with LLM if available)
        if self.use_llm:
            intent_type, risk_level, action, params = self.llm_parser.parse_intent(user_input)
        else:
            intent_type, risk_level = self.intent_classifier.classify(user_input)
            action, params = self._parse_action_legacy(user_input, intent_type)

        console.print(f"[dim]Intent: {intent_type.value} | Risk: {risk_level.value} | Action: {action}[/dim]\n")

        # Step 3: Get relevant context from memory (RAG)
        context = self.rag_system.get_personalized_context(user_input)
        if context.get("patterns"):
            console.print(f"[dim]💡 Pattern: {context['patterns'][0]}[/dim]\n")

        # Step 4: Human in the loop for SENSITIVE/DESTRUCTIVE
        if risk_level in [RiskLevel.SENSITIVE, RiskLevel.DESTRUCTIVE]:
            if not self._request_confirmation(user_input, intent_type, risk_level):
                result = {
                    "success": False,
                    "message": "Action cancelled by user",
                    "cancelled": True
                }
                console.print(f"[yellow]{result['message']}[/yellow]")
                return result

        # Step 5: Execute through appropriate agent
        result = self._execute_action(intent_type, action, params, risk_level)

        # Step 6: Enhance response with LLM if available
        if self.use_llm and result.get("success"):
            enhanced = self.rag_system.generate_personalized_response(
                user_input,
                result.get("message", "Done")
            )
            result["enhanced_message"] = enhanced

        # Step 7: Log action and learn
        self.callbacks.log_action(
            intent_type=intent_type.value,
            risk_level=risk_level.value,
            action=action,
            target=params.get('target', str(params)),
            permission_granted=not result.get('permission_denied', False),
            success=result.get('success', False),
            result=str(result.get('message', ''))
        )

        # Learn from interaction
        self.rag_system.learn_from_interaction(
            user_input,
            result.get("enhanced_message", result.get("message", "")),
            result.get("success", False)
        )

        # Save assistant response to memory
        response_text = result.get("enhanced_message", result.get("message", ""))
        self.session_memory.add_message(self.session_id, "assistant", str(response_text))
        self.vector_store.add_conversation(
            str(response_text),
            "assistant",
            metadata={"success": result.get("success", False)}
        )

        # Display result
        if result.get('success'):
            display_msg = result.get("enhanced_message", result.get("message", "Done"))
            console.print(f"[green]✓ {display_msg}[/green]")
        else:
            console.print(f"[red]✗ {result.get('message', 'Failed')}[/red]")

        return result

    def _request_confirmation(self, user_input: str, intent_type: IntentType,
                            risk_level: RiskLevel) -> bool:
        """Ask user for confirmation on sensitive/destructive actions"""
        console.print(f"[yellow]⚠️  {risk_level.value} ACTION DETECTED[/yellow]")
        console.print(f"[dim]Intent: {intent_type.value}[/dim]")
        console.print(f"[dim]Command: {user_input}[/dim]\n")

        return Confirm.ask("Do you want to proceed?", default=False)

    def _execute_action(self, intent_type: IntentType, action: str,
                       params: Dict, risk_level: RiskLevel) -> Dict[str, Any]:
        """Execute action through appropriate agent"""

        try:
            # Add target to params for logging
            if 'target' not in params:
                params['target'] = params.get('app_name') or params.get('filepath') or \
                                 params.get('command') or params.get('query') or 'unknown'

            if intent_type in [IntentType.SYSTEM_ACTION, IntentType.APPLICATION_CONTROL]:
                result = self.system_agent.execute(action, params, risk_level)

            elif intent_type == IntentType.FILE_OPERATION:
                result = self.file_agent.execute(action, params, risk_level)

            elif intent_type == IntentType.TERMINAL_OPERATION:
                result = self.system_agent.execute('run_command', params, risk_level)

            elif intent_type in [IntentType.INFORMATION, IntentType.CONVERSATION]:
                result = self.research_agent.execute(action, params)

            else:
                result = {
                    "success": False,
                    "message": f"Unknown intent type: {intent_type}"
                }

            result['action'] = action
            result['target'] = params['target']
            return result

        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            return {
                "success": False,
                "message": f"Error executing action: {str(e)}",
                "action": action,
                "target": params.get('target', 'error')
            }

    def _parse_action_legacy(self, user_input: str, intent_type: IntentType) -> tuple:
        """Legacy action parsing (fallback when LLM unavailable)"""
        from core.agents.orchestrator import OrchestratorAgent
        temp_orch = OrchestratorAgent()
        return temp_orch._parse_action(user_input, intent_type)

    def get_memory_stats(self) -> Dict:
        """Get statistics about stored memories"""
        stats = self.vector_store.get_collection_stats()
        stats['recent_actions'] = len(self.callbacks.action_history.get_recent_actions(limit=10))
        return stats

    def search_memory(self, query: str) -> str:
        """Search all memory systems"""
        return self.rag_system.search_memory(query)

    def get_recommendations(self) -> list:
        """Get AI-powered recommendations"""
        return self.rag_system.get_recommendations()

    def shutdown(self):
        """Clean shutdown"""
        self.session_memory.end_session(self.session_id)

        if self.knowledge_graph:
            self.knowledge_graph.close()

        # Display session summary
        summary = self.callbacks.get_session_summary()
        memory_stats = self.get_memory_stats()

        console.print("\n[bold]Session Summary:[/bold]")
        console.print(f"Duration: {summary['duration_seconds']} seconds")
        console.print(f"Actions: {len(summary['recent_actions'])}")
        console.print(f"\n[bold]Memory Stats:[/bold]")
        console.print(f"Conversations: {memory_stats['conversations']}")
        console.print(f"Preferences: {memory_stats['preferences']}")
        console.print(f"Action memories: {memory_stats['actions']}")
        console.print(f"Total memories: {memory_stats['total_memories']}")
