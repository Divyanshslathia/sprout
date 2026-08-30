#!/usr/bin/env python3
"""
Test Suite for Sprout Phase 1

Tests all major components and functionality
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rich.console import Console
from rich.table import Table
from core.intent.classifier import IntentClassifier
from core.intent.types import IntentType, RiskLevel
from core.permissions.policy import PermissionPolicy
from core.tools.os_tools import OSTools
from core.tools.file_tools import FileTools
from core.memory.session import SessionMemory
from core.memory.history import ActionHistory

console = Console()

def test_intent_classification():
    """Test intent classifier"""
    console.print("\n[bold cyan]Testing Intent Classification...[/bold cyan]")

    classifier = IntentClassifier()

    test_cases = [
        ("open terminal", IntentType.SYSTEM_ACTION, RiskLevel.SAFE),
        ("what is the weather", IntentType.INFORMATION, RiskLevel.SAFE),
        ("delete file test.txt", IntentType.FILE_OPERATION, RiskLevel.DESTRUCTIVE),
        ("search for Python", IntentType.INFORMATION, RiskLevel.SAFE),
        ("run ls -la", IntentType.TERMINAL_OPERATION, RiskLevel.SENSITIVE),
    ]

    results = []
    for user_input, expected_intent, expected_risk in test_cases:
        intent, risk = classifier.classify(user_input)
        passed = (intent == expected_intent and risk == expected_risk)
        results.append({
            "input": user_input,
            "intent": intent.value,
            "risk": risk.value,
            "passed": passed
        })

    # Display results
    table = Table(title="Intent Classification Tests")
    table.add_column("Input", style="cyan")
    table.add_column("Intent", style="yellow")
    table.add_column("Risk", style="magenta")
    table.add_column("Result", style="bold")

    for result in results:
        status = "[green]✓ PASS[/green]" if result["passed"] else "[red]✗ FAIL[/red]"
        table.add_row(
            result["input"],
            result["intent"],
            result["risk"],
            status
        )

    console.print(table)
    passed = sum(1 for r in results if r["passed"])
    console.print(f"\n[bold]Passed: {passed}/{len(results)}[/bold]")


def test_permissions():
    """Test permission system"""
    console.print("\n[bold cyan]Testing Permission System...[/bold cyan]")

    policy = PermissionPolicy()

    test_cases = [
        ("open_app", "terminal", RiskLevel.SENSITIVE, True),
        ("open_app", "unknown_app", RiskLevel.SENSITIVE, False),
        ("file_read", "/home/divyansh/Documents/test.txt", RiskLevel.SAFE, True),
        ("file_delete", "/etc/passwd", RiskLevel.DESTRUCTIVE, False),
        ("run_command", "rm -rf /", RiskLevel.DESTRUCTIVE, False),
    ]

    table = Table(title="Permission Tests")
    table.add_column("Action", style="cyan")
    table.add_column("Target", style="yellow")
    table.add_column("Expected", style="magenta")
    table.add_column("Result", style="bold")

    passed_count = 0
    for action, target, risk, expected_allowed in test_cases:
        allowed, reason = policy.check_permission(action, target, risk)
        passed = (allowed == expected_allowed)
        if passed:
            passed_count += 1

        status = "[green]✓ PASS[/green]" if passed else "[red]✗ FAIL[/red]"
        expected = "Allow" if expected_allowed else "Deny"
        table.add_row(action, target[:40], expected, status)

    console.print(table)
    console.print(f"\n[bold]Passed: {passed_count}/{len(test_cases)}[/bold]")


def test_file_tools():
    """Test file operations"""
    console.print("\n[bold cyan]Testing File Tools...[/bold cyan]")

    file_tools = FileTools()
    test_file = "/tmp/sprout_test.txt"
    test_content = "Hello from Sprout!"

    results = []

    # Test write
    result = file_tools.write_file(test_file, test_content)
    results.append(("Write file", result["success"]))

    # Test read
    result = file_tools.read_file(test_file)
    read_success = result["success"] and result.get("content") == test_content
    results.append(("Read file", read_success))

    # Test exists
    result = file_tools.file_exists(test_file)
    results.append(("File exists", result["success"] and result["exists"]))

    # Test delete
    result = file_tools.delete_file(test_file)
    results.append(("Delete file", result["success"]))

    # Verify deleted
    result = file_tools.file_exists(test_file)
    results.append(("Verify delete", not result["exists"]))

    # Display results
    table = Table(title="File Tools Tests")
    table.add_column("Test", style="cyan")
    table.add_column("Result", style="bold")

    for test_name, passed in results:
        status = "[green]✓ PASS[/green]" if passed else "[red]✗ FAIL[/red]"
        table.add_row(test_name, status)

    console.print(table)
    passed = sum(1 for _, p in results if p)
    console.print(f"\n[bold]Passed: {passed}/{len(results)}[/bold]")


def test_memory():
    """Test memory systems"""
    console.print("\n[bold cyan]Testing Memory Systems...[/bold cyan]")

    results = []

    # Test session memory
    session = SessionMemory()
    session_id = session.create_session()
    results.append(("Create session", session_id is not None))

    session.add_message(session_id, "user", "test message")
    history = session.get_session_history(session_id)
    results.append(("Add message", len(history) > 0))

    session.end_session(session_id)
    results.append(("End session", True))

    # Test action history
    action_log = ActionHistory()
    action_log.log_action(
        intent_type="TEST",
        risk_level="SAFE",
        action="test_action",
        target="test_target",
        permission_granted=True,
        success=True,
        result="test result"
    )

    recent = action_log.get_recent_actions(limit=1)
    results.append(("Log action", len(recent) > 0))

    search_results = action_log.search_actions("test_action")
    results.append(("Search actions", len(search_results) > 0))

    # Display results
    table = Table(title="Memory System Tests")
    table.add_column("Test", style="cyan")
    table.add_column("Result", style="bold")

    for test_name, passed in results:
        status = "[green]✓ PASS[/green]" if passed else "[red]✗ FAIL[/red]"
        table.add_row(test_name, status)

    console.print(table)
    passed = sum(1 for _, p in results if p)
    console.print(f"\n[bold]Passed: {passed}/{len(results)}[/bold]")


def test_os_tools():
    """Test OS tools (non-destructive tests only)"""
    console.print("\n[bold cyan]Testing OS Tools...[/bold cyan]")

    os_tools = OSTools()

    results = []

    # Test clipboard (if xclip available)
    result = os_tools.set_clipboard("Sprout test")
    clipboard_works = result["success"]
    results.append(("Set clipboard", clipboard_works))

    if clipboard_works:
        result = os_tools.get_clipboard()
        results.append(("Get clipboard", result["success"] and "Sprout test" in result.get("content", "")))

    # Test command execution (safe command)
    result = os_tools.run_terminal_command("echo 'test'")
    results.append(("Run command", result["success"]))

    # Display results
    table = Table(title="OS Tools Tests")
    table.add_column("Test", style="cyan")
    table.add_column("Result", style="bold")

    for test_name, passed in results:
        status = "[green]✓ PASS[/green]" if passed else "[red]✗ FAIL[/red]"
        table.add_row(test_name, status)

    console.print(table)
    passed = sum(1 for _, p in results if p)
    console.print(f"\n[bold]Passed: {passed}/{len(results)}[/bold]")


def main():
    """Run all tests"""
    console.print("\n[bold green]🌱 Sprout Phase 1 Test Suite[/bold green]\n")

    try:
        test_intent_classification()
        test_permissions()
        test_file_tools()
        test_memory()
        test_os_tools()

        console.print("\n[bold green]✓ All test suites completed![/bold green]\n")

    except Exception as e:
        console.print(f"\n[bold red]✗ Test failed with error:[/bold red] {str(e)}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
