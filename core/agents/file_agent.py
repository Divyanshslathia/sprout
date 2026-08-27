"""
File Agent

Handles file system operations with MCP filesystem integration
"""
from typing import Dict, Any
from core.tools.file_tools import FileTools
from core.permissions.policy import PermissionPolicy
from core.intent.types import RiskLevel

class FileAgent:
    """Agent for file system operations"""

    def __init__(self, permission_policy: PermissionPolicy):
        self.file_tools = FileTools()
        self.permission_policy = permission_policy

    def execute(self, action: str, params: Dict[str, Any], risk_level: RiskLevel) -> Dict:
        """
        Execute a file operation after permission check

        Args:
            action: Action to perform (read, write, delete, list, etc.)
            params: Parameters for the action
            risk_level: Risk level of the action

        Returns:
            Result dictionary
        """
        # Get target file/directory
        target = params.get('filepath') or params.get('dirpath') or 'unknown'

        # Permission check
        allowed, reason = self.permission_policy.check_permission(
            f"file_{action}", target, risk_level
        )

        if not allowed:
            return {
                "success": False,
                "message": f"Permission denied: {reason}",
                "permission_denied": True
            }

        # Execute based on action type
        if action == "read":
            return self.file_tools.read_file(params['filepath'])

        elif action == "write":
            return self.file_tools.write_file(params['filepath'], params['content'])

        elif action == "delete":
            return self.file_tools.delete_file(params['filepath'])

        elif action == "list":
            return self.file_tools.list_directory(params['dirpath'])

        elif action == "create_dir":
            return self.file_tools.create_directory(params['dirpath'])

        elif action == "exists":
            return self.file_tools.file_exists(params['filepath'])

        else:
            return {"success": False, "message": f"Unknown action: {action}"}
