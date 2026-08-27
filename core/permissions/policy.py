"""
Permission Policy System

JSON-based permission checker (will evolve to Neo4j in Phase 3)
"""
import json
from pathlib import Path
from typing import Dict, Optional
from core.intent.types import IntentType, RiskLevel
from config import permission_config

class PermissionPolicy:
    """Manages permission checks for actions"""

    def __init__(self):
        self.policy_file = Path(permission_config.policy_file)
        self._ensure_policy_file()
        self.permissions = self._load_permissions()

    def _ensure_policy_file(self):
        """Create default permissions file if it doesn't exist"""
        if not self.policy_file.exists():
            default_permissions = {
                "allowed_apps": [
                    "firefox", "chrome", "terminal", "code", "nautilus"
                ],
                "allowed_directories": [
                    "/home/divyansh/Documents",
                    "/home/divyansh/Downloads",
                    "/home/divyansh/projects"
                ],
                "blocked_directories": [
                    "/etc", "/sys", "/proc", "/root"
                ],
                "blocked_commands": [
                    "rm -rf /", "format", "dd if=", "mkfs"
                ],
                "require_confirmation": [
                    "delete", "remove", "install", "download"
                ]
            }
            self.policy_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.policy_file, 'w') as f:
                json.dump(default_permissions, f, indent=2)

    def _load_permissions(self) -> Dict:
        """Load permissions from JSON file"""
        with open(self.policy_file, 'r') as f:
            return json.load(f)

    def check_permission(self, action: str, target: str, risk_level: RiskLevel) -> tuple[bool, Optional[str]]:
        """
        Check if an action is permitted

        Args:
            action: The action to perform (e.g., "open_app", "delete_file")
            target: The target of the action (e.g., app name, file path)
            risk_level: Risk level of the action

        Returns:
            Tuple of (is_allowed, reason)
        """

        # DESTRUCTIVE actions always need confirmation
        if risk_level == RiskLevel.DESTRUCTIVE:
            return False, "DESTRUCTIVE action requires explicit confirmation"

        # Check blocked commands
        for blocked_cmd in self.permissions.get("blocked_commands", []):
            if blocked_cmd in target.lower():
                return False, f"Blocked command pattern: {blocked_cmd}"

        # Check directory permissions for file operations
        if "file" in action.lower() or "directory" in action.lower():
            target_path = Path(target).resolve()

            # Check blocked directories
            for blocked_dir in self.permissions.get("blocked_directories", []):
                if str(target_path).startswith(blocked_dir):
                    return False, f"Access to {blocked_dir} is blocked"

            # Check allowed directories
            allowed_dirs = self.permissions.get("allowed_directories", [])
            if allowed_dirs:
                is_in_allowed = any(str(target_path).startswith(d) for d in allowed_dirs)
                if not is_in_allowed:
                    return False, f"Directory not in allowed list"

        # Check app permissions
        if "app" in action.lower():
            allowed_apps = self.permissions.get("allowed_apps", [])
            if allowed_apps and target.lower() not in allowed_apps:
                return False, f"App '{target}' not in allowed list"

        # SENSITIVE actions pass but need confirmation
        if risk_level == RiskLevel.SENSITIVE:
            return True, "SENSITIVE action - confirmation recommended"

        # SAFE actions are allowed
        return True, None

    def add_permission(self, resource_type: str, resource: str):
        """Add a new permission to the policy"""
        if resource_type == "app":
            if resource not in self.permissions["allowed_apps"]:
                self.permissions["allowed_apps"].append(resource)
        elif resource_type == "directory":
            if resource not in self.permissions["allowed_directories"]:
                self.permissions["allowed_directories"].append(resource)

        self._save_permissions()

    def _save_permissions(self):
        """Save current permissions to file"""
        with open(self.policy_file, 'w') as f:
            json.dump(self.permissions, f, indent=2)
