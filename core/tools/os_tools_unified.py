"""
Unified OS Tools - Cross-Platform Abstraction

Automatically selects Linux or Windows implementation based on platform
"""
from typing import Optional
from core.platform import PlatformDetector

class UnifiedOSTools:
    """Cross-platform OS tools that work on both Linux and Windows"""

    def __init__(self):
        """Initialize with platform-specific implementation"""
        self.platform = PlatformDetector.detect()

        if PlatformDetector.is_windows():
            from core.tools.os_tools_windows import WindowsOSTools
            self.impl = WindowsOSTools()
        else:
            from core.tools.os_tools import OSTools
            self.impl = OSTools()

    def open_application(self, app_name: str) -> dict:
        """Open an application (cross-platform)"""
        return self.impl.open_application(app_name)

    def close_application(self, app_name: str) -> dict:
        """Close an application (cross-platform)"""
        return self.impl.close_application(app_name)

    def run_terminal_command(self, command: str, working_dir: Optional[str] = None) -> dict:
        """Execute a terminal command (cross-platform)"""
        if hasattr(self.impl, 'run_terminal_command'):
            if PlatformDetector.is_windows():
                return self.impl.run_terminal_command(command, working_dir, use_powershell=True)
            else:
                return self.impl.run_terminal_command(command, working_dir)
        return {"success": False, "message": "Command execution not supported on this platform"}

    def get_clipboard(self) -> dict:
        """Get clipboard content (cross-platform)"""
        return self.impl.get_clipboard()

    def set_clipboard(self, content: str) -> dict:
        """Set clipboard content (cross-platform)"""
        return self.impl.set_clipboard(content)

    def take_screenshot(self, filepath: Optional[str] = None) -> dict:
        """Take a screenshot (cross-platform)"""
        return self.impl.take_screenshot(filepath)

    def list_running_apps(self) -> dict:
        """List running applications (cross-platform)"""
        return self.impl.list_running_apps()

    def get_platform_name(self) -> str:
        """Get current platform name"""
        return self.platform.value
