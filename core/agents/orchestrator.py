"""
Orchestrator Agent

Root agent that classifies intent, routes to specialists, and manages permissions
"""
from typing import Dict, Any, Optional
from rich.console import Console
from rich.prompt import Confirm

from core.intent.classifier import IntentClassifier
from core.intent.types import IntentType, RiskLevel
from core.permissions.policy import PermissionPolicy
from core.agents.system_agent import SystemAgent
from core.agents.file_agent import FileAgent
from core.agents.research_agent import ResearchAgent
from core.callbacks import SproutCallbacks, SafetyGuardrails
from core.memory.session import SessionMemory

console = Console()

class OrchestratorAgent:
    """
    Root agent that orchestrates all operations

    Responsibilities:
    1. Classify intent and risk level
    2. Route to appropriate specialist agent
    3. Enforce permission checks
    4. Handle human-in-the-loop confirmations
    5. Log all actions
    """

    def __init__(self):
        # Initialize components
        self.intent_classifier = IntentClassifier()
        self.permission_policy = PermissionPolicy()
        self.callbacks = SproutCallbacks()
        self.guardrails = SafetyGuardrails()
        self.session_memory = SessionMemory()

        # Initialize specialist agents
        self.system_agent = SystemAgent(self.permission_policy)
        self.file_agent = FileAgent(self.permission_policy)
        self.research_agent = ResearchAgent()

        # Create or get active session
        self.session_id = self.session_memory.get_active_session()
        if not self.session_id:
            self.session_id = self.session_memory.create_session()

    def process(self, user_input: str) -> Dict[str, Any]:
        """
        Process user input through the full pipeline

        Args:
            user_input: Raw user command or question

        Returns:
            Result dictionary with success status and message
        """
        console.print(f"\n[bold cyan]User:[/bold cyan] {user_input}\n")

        # Save user message to session
        self.session_memory.add_message(self.session_id, "user", user_input)

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

        # Step 2: Classify intent and risk
        intent_type, risk_level = self.intent_classifier.classify(user_input)

        console.print(f"[dim]Intent: {intent_type.value} | Risk: {risk_level.value}[/dim]\n")

        # Step 3: Human in the loop for SENSITIVE/DESTRUCTIVE actions
        if risk_level in [RiskLevel.SENSITIVE, RiskLevel.DESTRUCTIVE]:
            if not self._request_confirmation(user_input, intent_type, risk_level):
                result = {
                    "success": False,
                    "message": "Action cancelled by user",
                    "cancelled": True
                }
                console.print(f"[yellow]{result['message']}[/yellow]")
                return result

        # Step 4: Route to appropriate agent
        result = self._route_to_agent(user_input, intent_type, risk_level)

        # Step 5: Log action
        self.callbacks.log_action(
            intent_type=intent_type.value,
            risk_level=risk_level.value,
            action=result.get('action', 'unknown'),
            target=result.get('target', 'unknown'),
            permission_granted=not result.get('permission_denied', False),
            success=result.get('success', False),
            result=str(result.get('message', ''))
        )

        # Save assistant response
        self.session_memory.add_message(self.session_id, "assistant", str(result))

        # Display result
        if result.get('success'):
            console.print(f"[green]✓ {result.get('message', 'Done')}[/green]")
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

    def _route_to_agent(self, user_input: str, intent_type: IntentType,
                       risk_level: RiskLevel) -> Dict[str, Any]:
        """Route the request to the appropriate specialist agent"""

        # Parse action and parameters from user input
        action, params = self._parse_action(user_input, intent_type)

        try:
            if intent_type == IntentType.SYSTEM_ACTION:
                result = self.system_agent.execute(action, params, risk_level)
                result['action'] = action
                result['target'] = params.get('app_name', 'system')
                return result

            elif intent_type == IntentType.APPLICATION_CONTROL:
                result = self.system_agent.execute(action, params, risk_level)
                result['action'] = action
                result['target'] = params.get('app_name', 'unknown')
                return result

            elif intent_type == IntentType.FILE_OPERATION:
                result = self.file_agent.execute(action, params, risk_level)
                result['action'] = action
                result['target'] = params.get('filepath', params.get('dirpath', 'unknown'))
                return result

            elif intent_type == IntentType.TERMINAL_OPERATION:
                result = self.system_agent.execute('run_command', params, risk_level)
                result['action'] = 'run_command'
                result['target'] = params.get('command', 'unknown')
                return result

            elif intent_type == IntentType.INFORMATION:
                result = self.research_agent.execute(action, params)
                result['action'] = action
                result['target'] = params.get('query', 'information')
                return result

            elif intent_type == IntentType.CONVERSATION:
                result = self.research_agent.execute('answer_question',
                                                    {'question': user_input})
                result['action'] = 'conversation'
                result['target'] = 'chat'
                return result

            else:
                return {
                    "success": False,
                    "message": f"Unknown intent type: {intent_type}",
                    "action": "unknown",
                    "target": "unknown"
                }

        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            return {
                "success": False,
                "message": f"Error executing action: {str(e)}",
                "action": action,
                "target": "error"
            }

    def _parse_action(self, user_input: str, intent_type: IntentType) -> tuple[str, Dict[str, Any]]:
        """
        Parse user input into action and parameters

        This is a simple parser for Phase 1. Phase 3 will use LLM for better parsing.
        """
        user_input_lower = user_input.lower()
        words = user_input_lower.split()

        # System/App actions
        if "open" in words or "launch" in words or "start" in words:
            # Extract app name (word after open/launch/start)
            try:
                idx = max([words.index(w) for w in ["open", "launch", "start"] if w in words])
                app_name = words[idx + 1] if idx + 1 < len(words) else "unknown"
                return "open_app", {"app_name": app_name}
            except:
                return "open_app", {"app_name": "unknown"}

        elif "close" in words or "quit" in words or "kill" in words:
            try:
                idx = max([words.index(w) for w in ["close", "quit", "kill"] if w in words])
                app_name = words[idx + 1] if idx + 1 < len(words) else "unknown"
                return "close_app", {"app_name": app_name}
            except:
                return "close_app", {"app_name": "unknown"}

        elif "screenshot" in user_input_lower:
            return "take_screenshot", {}

        elif "clipboard" in user_input_lower:
            if "get" in words or "show" in words or "what" in words:
                return "get_clipboard", {}
            else:
                # Extract content after clipboard/copy
                return "set_clipboard", {"content": user_input}

        # File operations
        elif "read" in words and "file" in user_input_lower:
            # Extract filepath
            filepath = self._extract_filepath(user_input)
            return "read", {"filepath": filepath}

        elif "write" in words or "create" in words:
            filepath = self._extract_filepath(user_input)
            return "write", {"filepath": filepath, "content": ""}

        elif "delete" in words or "remove" in words:
            filepath = self._extract_filepath(user_input)
            return "delete", {"filepath": filepath}

        elif "list" in words and ("file" in words or "directory" in words or "folder" in words):
            dirpath = self._extract_filepath(user_input) or "."
            return "list", {"dirpath": dirpath}

        # Terminal operations
        elif "run" in words or "execute" in words or "command" in words:
            # Extract command (everything after run/execute)
            try:
                idx = max([words.index(w) for w in ["run", "execute", "command"] if w in words])
                command = " ".join(user_input.split()[idx + 1:])
                return "run_command", {"command": command}
            except:
                return "run_command", {"command": user_input}

        # Information/Research
        elif any(w in words for w in ["search", "find", "look", "google"]):
            query = user_input
            for prefix in ["search for", "find", "look up", "google"]:
                if prefix in user_input_lower:
                    query = user_input_lower.split(prefix, 1)[1].strip()
                    break
            return "search_web", {"query": query}

        elif "what did" in user_input_lower or "yesterday" in words or "recall" in words:
            return "recall_action", {"query": user_input}

        else:
            # Default to answering as a question
            return "answer_question", {"question": user_input}

    def _extract_filepath(self, text: str) -> str:
        """Extract filepath from user input"""
        # Look for paths starting with / or ~ or containing /
        words = text.split()
        for word in words:
            if '/' in word or word.startswith('~'):
                return word.strip('"\'')

        # If no path found, return last word as filename
        return words[-1] if words else "unknown"

    def shutdown(self):
        """Clean shutdown of the orchestrator"""
        self.session_memory.end_session(self.session_id)
        summary = self.callbacks.get_session_summary()

        console.print("\n[bold]Session Summary:[/bold]")
        console.print(f"Duration: {summary['duration_seconds']} seconds")
        console.print(f"Total tokens: {summary['total_tokens']}")
        console.print(f"Recent actions: {len(summary['recent_actions'])}")
