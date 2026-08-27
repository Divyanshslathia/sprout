#!/usr/bin/env python3
"""
Sprout Demo Script

Demonstrates Phase 1 capabilities with automated examples
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from core.agents.orchestrator import OrchestratorAgent

console = Console()

def demo_header():
    """Display demo header"""
    header = """
# 🌱 Sprout Phase 1 Demo

## Capabilities Demonstration

This demo showcases the following features:
- Multi-agent orchestration
- Intent classification with risk assessment
- Permission-gated execution
- Human-in-the-loop for sensitive operations
- Action logging and memory
"""
    console.print(Panel(Markdown(header), border_style="green"))


def run_demo_command(orchestrator, command, description):
    """Run a demo command with description"""
    console.print(f"\n[bold yellow]Demo:[/bold yellow] {description}")
    console.print(f"[dim]Command: {command}[/dim]")
    console.print("─" * 60)

    result = orchestrator.process(command)

    console.print("─" * 60)
    return result


def main():
    """Run automated demo"""
    demo_header()

    console.print("\n[bold cyan]Starting Automated Demo...[/bold cyan]\n")
    console.print("[dim]Note: Some commands may require confirmation or fail due to permissions[/dim]\n")

    orchestrator = OrchestratorAgent()

    try:
        # Demo 1: Information Query
        run_demo_command(
            orchestrator,
            "what time is it",
            "Information Query - Safe, no confirmation needed"
        )

        # Demo 2: Web Search
        run_demo_command(
            orchestrator,
            "search for Python tutorials",
            "Web Search - Opens browser search"
        )

        # Demo 3: File Operations
        run_demo_command(
            orchestrator,
            "list files ~/Documents",
            "File Operation - List directory contents"
        )

        # Demo 4: System Information
        run_demo_command(
            orchestrator,
            "what did I do yesterday",
            "Memory Recall - Search action history"
        )

        # Demo 5: Help
        run_demo_command(
            orchestrator,
            "help",
            "Built-in Help System"
        )

        # Show session summary
        console.print("\n[bold green]Demo Complete![/bold green]\n")

        summary = orchestrator.callbacks.get_session_summary()
        console.print(Panel(f"""
[bold]Session Summary[/bold]

Duration: {summary['duration_seconds']} seconds
Actions Logged: {len(summary['recent_actions'])}

[dim]View full history with: python agent.py (then type 'history')[/dim]
""", border_style="cyan"))

        orchestrator.shutdown()

    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted[/yellow]")
        orchestrator.shutdown()
    except Exception as e:
        console.print(f"\n[red]Demo error: {str(e)}[/red]")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
