"""
Callbacks and Guardrails

Logging, cost tracking, and safety checks for all tool calls
"""
from datetime import datetime
from typing import Any, Dict
from rich.console import Console
from core.memory.history import ActionHistory

console = Console()

class SproutCallbacks:
    """Callbacks for logging and guardrails"""

    def __init__(self):
        self.action_history = ActionHistory()
        self.session_start = datetime.now()
        self.total_tokens = 0

    def on_tool_start(self, tool_name: str, inputs: Dict[str, Any]):
        """Called before a tool executes"""
        console.print(f"[yellow]🔧 Tool: {tool_name}[/yellow]")
        console.print(f"[dim]Inputs: {inputs}[/dim]")

    def on_tool_end(self, tool_name: str, output: Any):
        """Called after a tool executes"""
        console.print(f"[green]✓ {tool_name} completed[/green]")

    def on_tool_error(self, tool_name: str, error: Exception):
        """Called when a tool fails"""
        console.print(f"[red]✗ {tool_name} failed: {str(error)}[/red]")

    def on_llm_start(self, prompt: str):
        """Called before LLM invocation"""
        console.print(f"[cyan]🤖 Thinking...[/cyan]")

    def on_llm_end(self, response: str, tokens_used: int = 0):
        """Called after LLM responds"""
        self.total_tokens += tokens_used
        console.print(f"[green]💬 Response received[/green]")
        if tokens_used > 0:
            console.print(f"[dim]Tokens: {tokens_used} (Total: {self.total_tokens})[/dim]")

    def log_action(self, intent_type: str, risk_level: str, action: str,
                   target: str, permission_granted: bool, success: bool,
                   result: str):
        """Log an action to history"""
        self.action_history.log_action(
            intent_type=intent_type,
            risk_level=risk_level,
            action=action,
            target=target,
            permission_granted=permission_granted,
            success=success,
            result=result
        )

    def get_session_summary(self) -> Dict:
        """Get summary of current session"""
        duration = (datetime.now() - self.session_start).seconds
        return {
            "duration_seconds": duration,
            "total_tokens": self.total_tokens,
            "recent_actions": self.action_history.get_recent_actions(limit=5)
        }


class SafetyGuardrails:
    """Input validation and safety checks"""

    BLOCKED_PATTERNS = [
        "rm -rf /",
        "format",
        "mkfs",
        "dd if=/dev/zero",
        ":(){:|:&};:",  # fork bomb
    ]

    SENSITIVE_PATHS = [
        "/etc",
        "/sys",
        "/proc",
        "/root",
        "/boot"
    ]

    @staticmethod
    def check_input_safety(user_input: str) -> tuple[bool, str]:
        """
        Check if input is safe to process

        Returns:
            (is_safe, reason)
        """
        user_input_lower = user_input.lower()

        # Check for blocked command patterns
        for pattern in SafetyGuardrails.BLOCKED_PATTERNS:
            if pattern in user_input_lower:
                return False, f"Blocked dangerous pattern: {pattern}"

        # Check for sensitive path access
        for path in SafetyGuardrails.SENSITIVE_PATHS:
            if path in user_input and ("delete" in user_input_lower or "remove" in user_input_lower):
                return False, f"Attempted dangerous operation on system path: {path}"

        return True, "Input passed safety checks"

    @staticmethod
    def sanitize_command(command: str) -> str:
        """Remove potentially dangerous command components"""
        # Remove command chaining
        dangerous_chars = [";", "&&", "||", "|"]
        for char in dangerous_chars:
            if char in command:
                command = command.split(char)[0]

        return command.strip()
