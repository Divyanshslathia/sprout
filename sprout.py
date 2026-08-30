#!/usr/bin/env python3
"""
Sprout — Personal AI OS Assistant (Phase 2 & 3 Complete)

Enhanced with:
- Voice interaction (Whisper STT + Porcupine wake word + TTS)
- Semantic memory (ChromaDB)
- Knowledge graph permissions (NetworkX/Neo4j)
- LLM-powered parsing (Gemini)
- RAG system for personalized responses
"""
import sys
import os
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown
from tray import get_tray
console = Console()

def print_welcome(mode: str = "text"):
    """Display welcome banner"""
    if mode == "voice":
        welcome_text = """
[bold green]🌱 Sprout — Voice Mode[/bold green]

[bold]Phase 2 & 3 Features Active:[/bold]
• 🎤 Voice interaction (wake word + STT + TTS)
• 🧠 Semantic memory with ChromaDB
• 🔐 Knowledge graph permissions
• 🤖 LLM-powered intent parsing
• 💡 RAG for personalized responses

Say '[bold]Hey Sprout[/bold]' to activate voice input.

[dim]Type 'text' to switch to text mode, or 'exit' to quit.[/dim]
"""
    else:
        welcome_text = """
[bold green]🌱 Sprout — Personal AI OS Assistant[/bold green]

[bold]Phase 1-3 Complete:[/bold]
• Multi-agent architecture with orchestration
• Permission-gated execution
• Semantic memory & RAG
• LLM-powered parsing (if API key set)
• Voice support ready (use --voice flag)

Commands: help | history | memory | recommendations | voice | exit
"""
    console.print(Panel(welcome_text, border_style="green"))


def run_text_mode():
    """Run in text-only mode"""
    print_welcome("text")

    # Import here to handle dependencies gracefully
    try:
        from core.agents.orchestrator_v2 import EnhancedOrchestrator
        orchestrator = EnhancedOrchestrator(use_llm=True, use_knowledge_graph=True)
    except Exception as e:
        console.print(f"[yellow]Warning: Enhanced features unavailable: {str(e)}[/yellow]")
        console.print("[yellow]Could not start. Check your .env and dependencies.[/yellow]")
        raise

    try:
        while True:
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

            elif user_input.lower() == "memory":
                show_memory_stats(orchestrator)
                continue

            elif user_input.lower() == "recommendations":
                show_recommendations(orchestrator)
                continue

            elif user_input.lower() == "voice":
                console.print("[yellow]Switching to voice mode...[/yellow]")
                orchestrator.shutdown()
                run_voice_mode()
                return

            elif user_input.lower() == "clear":
                console.clear()
                print_welcome("text")
                continue

            # Process through orchestrator
            orchestrator.process(user_input)

    except KeyboardInterrupt:
        console.print("\n\n[yellow]Interrupted by user[/yellow]")

    except Exception as e:
        console.print(f"\n[red]Fatal error: {str(e)}[/red]")
        import traceback
        traceback.print_exc()

    finally:
        orchestrator.shutdown()
        console.print("\n[dim]Session ended[/dim]\n")


def run_voice_mode():
    """Run in voice mode with wake word detection"""
    print_welcome("voice")

    try:
        from voice.pipeline import VoicePipeline
        from core.agents.orchestrator_v2 import EnhancedOrchestrator

        # Initialize orchestrator
        orchestrator = EnhancedOrchestrator(use_llm=True, use_knowledge_graph=True)

        # Create callback for voice commands
        def process_voice_command(command: str) -> str:
            result = orchestrator.process(command)
            return result.get("enhanced_message", result.get("message", "Done"))

        # Initialize voice pipeline
        voice = VoicePipeline(on_command=process_voice_command)

        console.print("\n[bold green]Voice pipeline ready![/bold green]")
        console.print("[yellow]Test commands:[/yellow]")
        console.print("  test-stt  - Test speech recognition")
        console.print("  test-tts  - Test text-to-speech")
        console.print("  test-full - Test complete pipeline")
        console.print("  start     - Start wake word listening")
        console.print("  text      - Switch to text mode")
        console.print("  exit      - Quit\n")

        while True:
            cmd = Prompt.ask("[bold cyan]Voice>[/bold cyan]").strip().lower()

            if cmd in ["exit", "quit"]:
                break
            elif cmd == "text":
                console.print("[yellow]Switching to text mode...[/yellow]")
                voice.stop()
                orchestrator.shutdown()
                run_text_mode()
                return
            elif cmd == "test-stt":
                voice.test_stt()
            elif cmd == "test-tts":
                voice.test_tts()
            elif cmd == "test-full":
                voice.test_full_pipeline()
            elif cmd == "start":
                console.print("[green]Starting wake word detection...[/green]")
                voice.start()  # This blocks until Ctrl+C
            else:
                console.print("[yellow]Unknown command. Type 'help' for options.[/yellow]")

        voice.stop()
        orchestrator.shutdown()

    except ImportError as e:
        console.print(f"[red]Voice dependencies not installed: {str(e)}[/red]")
        console.print("[yellow]Install with: pip install openai-whisper openwakeword pyttsx3 pyaudio[/yellow]")
        console.print("[yellow]Falling back to text mode...[/yellow]")
        run_text_mode()

    except Exception as e:
        console.print(f"[red]Voice mode error: {str(e)}[/red]")
        import traceback
        traceback.print_exc()


def show_help():
    """Display help information"""
    help_text = """
[bold]Sprout Commands & Features[/bold]

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

[bold cyan]Information & Memory:[/bold cyan]
• search [query]     - Search the web
• what is [query]    - Ask a question
• what did I [query] - Search your action history
• memory             - Show memory statistics
• recommendations    - Get AI recommendations

[bold cyan]Special Commands:[/bold cyan]
• help               - Show this help
• history            - Show recent actions
• memory             - Show memory stats
• recommendations    - Get suggestions
• voice              - Switch to voice mode
• clear              - Clear screen
• exit               - Quit Sprout

[bold yellow]Phase 2 & 3 Features:[/bold yellow]
• Semantic memory search across all interactions
• LLM-powered natural language understanding
• Personalized responses based on your patterns
• Knowledge graph for advanced permissions
"""
    console.print(Panel(help_text, border_style="cyan"))


def show_history(orchestrator):
    """Display recent action history"""
    from rich.table import Table

    actions = orchestrator.callbacks.action_history.get_recent_actions(limit=15)

    if not actions:
        console.print("[dim]No actions recorded yet[/dim]")
        return

    table = Table(title="Recent Actions", show_header=True, header_style="bold magenta")
    table.add_column("Time", style="dim", width=8)
    table.add_column("Intent", style="cyan", width=15)
    table.add_column("Action", style="yellow", width=15)
    table.add_column("Target", style="green")
    table.add_column("✓", style="bold", width=3)

    for action in actions:
        timestamp = action['timestamp'].split()[1].split('.')[0] if ' ' in action['timestamp'] else action['timestamp']
        success_icon = "✓" if action['success'] else "✗"
        success_style = "green" if action['success'] else "red"

        table.add_row(
            timestamp,
            action['intent_type'][:15],
            action['action'][:15],
            action['target'][:40],
            f"[{success_style}]{success_icon}[/{success_style}]"
        )

    console.print(table)


def show_memory_stats(orchestrator):
    """Display memory statistics"""
    if not hasattr(orchestrator, 'get_memory_stats'):
        console.print("[yellow]Memory stats not available in Phase 1 mode[/yellow]")
        return

    stats = orchestrator.get_memory_stats()

    stats_text = f"""
[bold]Memory Statistics[/bold]

[cyan]Vector Store (Semantic Memory):[/cyan]
  Conversations: {stats.get('conversations', 0)}
  Preferences: {stats.get('preferences', 0)}
  Action Memories: {stats.get('actions', 0)}
  Total: {stats.get('total_memories', 0)}

[cyan]Recent Activity:[/cyan]
  Recent Actions: {stats.get('recent_actions', 0)}

[dim]Semantic search available across all memories[/dim]
"""
    console.print(Panel(stats_text, border_style="magenta"))


def show_recommendations(orchestrator):
    """Show AI-powered recommendations"""
    if not hasattr(orchestrator, 'get_recommendations'):
        console.print("[yellow]Recommendations not available in Phase 1 mode[/yellow]")
        return

    recommendations = orchestrator.get_recommendations()

    if not recommendations:
        console.print("[dim]No recommendations available yet[/dim]")
        return

    console.print("\n[bold magenta]💡 Recommendations:[/bold magenta]\n")
    for i, rec in enumerate(recommendations, 1):
        console.print(f"  {i}. {rec}")
    console.print()


def main():
    parser = argparse.ArgumentParser(description="Sprout AI Assistant")
    parser.add_argument("--voice", action="store_true")
    parser.add_argument("--background", action="store_true")
    parser.add_argument("--test", action="store_true")
    args = parser.parse_args()

    if args.test:
        import subprocess
        subprocess.run(["python", "test_sprout.py"])
    elif args.background:
        run_background()
    elif args.voice:
        run_voice_mode()
    else:
        run_text_mode()
def run_background():
    """
    Run Sprout as a silent background process.
 
    - No terminal UI
    - System tray icon shows status
    - Listens for wake word always
    - Activates voice pipeline on detection
    - Logs everything to logs/sprout.log
    """
    import logging
    from pathlib import Path
    from tray import get_tray
 
    # Setup file logging (no console output in background mode)
    log_path = Path(__file__).parent / "logs" / "sprout.log"
    logging.basicConfig(
        filename=str(log_path),
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
    log = logging.getLogger("sprout")
    log.info("Sprout starting in background mode")
 
    # Start tray icon
    tray = get_tray()
    tray.start()
    tray.set_state("idle", "🌱 Sprout — Starting up...")
 
    try:
        from voice.pipeline import VoicePipeline
        from core.agents.orchestrator_v2 import EnhancedOrchestrator
 
        orchestrator = EnhancedOrchestrator()
        log.info("Orchestrator initialized")
 
        def on_wake_word():
            """Called when wake word is detected."""
            log.info("Wake word detected")
            tray.set_state("listening", "🎤 Sprout — Listening...")
 
        def on_command(text: str):
            """Called when STT produces text."""
            log.info(f"Command received: {text}")
            tray.set_state("thinking", "💭 Sprout — Processing...")
            try:
                orchestrator.process(text)
                log.info("Command processed successfully")
            except Exception as e:
                log.error(f"Command failed: {e}")
                tray.set_state("error", f"❌ Error: {str(e)[:40]}")
            finally:
                tray.set_state("idle", "🌱 Sprout — Waiting for wake word")
 
        pipeline = VoicePipeline(
            on_wake_word_callback=on_wake_word,
            on_command_callback=on_command
        )
 
        tray.set_state("idle", "🌱 Sprout — Say 'Hey Sprout' to activate")
        log.info("Voice pipeline ready — listening for wake word")
 
        pipeline.start()  # blocking — runs forever
 
    except ImportError as e:
        log.error(f"Voice dependencies missing: {e}")
        tray.set_state("error", "❌ Voice deps missing — check logs")
 
        # Fall back to keeping tray alive without voice
        import time
        log.info("Running in tray-only mode (no voice)")
        while True:
            time.sleep(60)
 
    except KeyboardInterrupt:
        log.info("Sprout stopped by user")
        tray.stop()
 


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Sprout AI Assistant")
    parser.add_argument("--voice", action="store_true")
    parser.add_argument("--background", action="store_true")
    parser.add_argument("--test", action="store_true")
    parser.add_argument("--demo", action="store_true")
    args = parser.parse_args()

    if args.test:
        import subprocess
        subprocess.run(["python", "test_sprout.py"])
    elif args.demo:
        import subprocess
        subprocess.run(["python", "demo.py"])
    elif args.background:
        run_background()
    elif args.voice:
        # your existing voice mode call
        main()
    else:
        main()