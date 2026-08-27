#!/usr/bin/env python3
"""
Sprout — Personal AI OS Assistant

Voice-activated (Phase 2) assistant that controls your computer
with a permission-first architecture.

Phase 1: Text-based interface with full agent functionality
"""
import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from core.agents.orchestrator import OrchestratorAgent

console = Console()

def print_welcome():
    """Display welcome banner"""
    welcome_text = """
[bold green]🌱 Sprout — Personal AI OS Assistant[/bold green]

[dim]Phase 1: Text Interface[/dim]

I can help you:
• Open and close applications
• Manage files (read, write, delete)
• Run terminal commands
• Search the web
• Answer questions

Type '[bold]help[/bold]' for more info or '[bold]exit[/bold]' to quit.
"""
    console.print(Panel(welcome_text, border_style="green"))


def main():
    """Main entry point for Sprout"""
    print_welcome()

    # Initialize orchestrator
    orchestrator = OrchestratorAgent()

    try:
        while True:
            # Get user input
            user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]").strip()

            if not user_input:
                continue

            # Handle special commands
            if user_input.lower() in ["exit", "quit", "bye"]:
                console.print("\n[green]👋 Goodbye![/green]")
                break

            elif user_input.lower() == "help":
                show_help()
                continue

            elif user_input.lower() == "history":
                show_history(orchestrator)
                continue

            elif user_input.lower() == "clear":
                console.clear()
                print_welcome()
                continue

            # Process the input through orchestrator
            orchestrator.process(user_input)

    except KeyboardInterrupt:
        console.print("\n\n[yellow]Interrupted by user[/yellow]")

    except Exception as e:
        console.print(f"\n[red]Fatal error: {str(e)}[/red]")
        import traceback
        traceback.print_exc()

    finally:
        # Shutdown orchestrator
        orchestrator.shutdown()
        console.print("\n[dim]Session ended[/dim]\n")


def show_help():
    """Display help information"""
    help_text = """
[bold]Sprout Commands[/bold]

[bold cyan]System Actions:[/bold cyan]
• open [app]         - Open an application
• close [app]        - Close an application
• screenshot         - Take a screenshot
• clipboard          - Get clipboard content

[bold cyan]File Operations:[/bold cyan]
• read file [path]   - Read a file
• write file [path]  - Write to a file
• delete file [path] - Delete a file
• list files [dir]   - List directory contents

[bold cyan]Terminal:[/bold cyan]
• run [command]      - Execute a terminal command

[bold cyan]Information:[/bold cyan]
• search [query]     - Search the web
• what is [query]    - Ask a question
• help              - Show this help
• history           - Show recent actions
• exit              - Quit Sprout

[bold yellow]Examples:[/bold yellow]
• "open terminal"
• "search for Python tutorials"
• "read file ~/Documents/notes.txt"
• "what time is it"
"""
    console.print(Panel(help_text, border_style="cyan"))


def show_history(orchestrator: OrchestratorAgent):
    """Display recent action history"""
    from rich.table import Table

    actions = orchestrator.callbacks.action_history.get_recent_actions(limit=10)

    if not actions:
        console.print("[dim]No actions recorded yet[/dim]")
        return

    table = Table(title="Recent Actions", show_header=True, header_style="bold magenta")
    table.add_column("Time", style="dim")
    table.add_column("Intent", style="cyan")
    table.add_column("Action", style="yellow")
    table.add_column("Target", style="green")
    table.add_column("Success", style="bold")

    for action in actions:
        timestamp = action['timestamp'].split('.')[0] if '.' in action['timestamp'] else action['timestamp']
        success_icon = "✓" if action['success'] else "✗"
        success_style = "green" if action['success'] else "red"

        table.add_row(
            timestamp.split()[1],  # Just show time
            action['intent_type'],
            action['action'],
            action['target'][:30],  # Truncate long targets
            f"[{success_style}]{success_icon}[/{success_style}]"
        )

    console.print(table)


if __name__ == "__main__":
    main()
