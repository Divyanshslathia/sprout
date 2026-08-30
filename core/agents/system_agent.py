"""
System Agent

Handles OS-level actions: app control, terminal, clipboard, screenshots
Cross-platform: Works on Linux, Windows, and macOS
"""
from typing import Dict, Any
from core.tools.os_tools_unified import UnifiedOSTools
from core.permissions.policy import PermissionPolicy
from core.intent.types import RiskLevel

class SystemAgent:
    """Agent for system-level operations (cross-platform)"""

    def __init__(self, permission_policy: PermissionPolicy):
        self.os_tools = UnifiedOSTools()
        self.permission_policy = permission_policy

    def execute(self, action: str, params: Dict[str, Any], risk_level: RiskLevel, user_confirmed: bool = False) -> Dict:
        """
        Execute a system action after permission check

        Args:
            action: Action to perform (open_app, close_app, run_command, etc.)
            params: Parameters for the action
            risk_level: Risk level of the action

        Returns:
            Result dictionary
        """
        # Permission check
        target = params.get('app_name') or params.get('command') or 'system'
        allowed, reason = self.permission_policy.check_permission(action, target, risk_level, user_confirmed)

        if not allowed:
            return {
                "success": False,
                "message": f"Permission denied: {reason}",
                "permission_denied": True
            }

        # Execute based on action type
        if action == "open_app":
            return self.os_tools.open_application(params['app_name'])

        elif action == "close_app":
            return self.os_tools.close_application(params['app_name'])

        elif action == "run_command":
            command = params['command']
            working_dir = params.get('working_dir')
            return self.os_tools.run_terminal_command(command, working_dir)

        elif action == "get_clipboard":
            return self.os_tools.get_clipboard()

        elif action == "set_clipboard":
            return self.os_tools.set_clipboard(params['content'])

        elif action == "take_screenshot":
            filepath = params.get('filepath')
            return self.os_tools.take_screenshot(filepath)

        elif action == "list_apps":
            return self.os_tools.list_running_apps()

        else:
            return {"success": False, "message": f"Unknown action: {action}"}
