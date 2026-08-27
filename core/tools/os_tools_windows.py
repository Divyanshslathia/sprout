"""
Windows OS Tools

Windows-specific implementations for system automation
"""
import subprocess
import os
from typing import Optional

class WindowsOSTools:
    """Windows system automation tools"""

    @staticmethod
    def open_application(app_name: str) -> dict:
        """
        Open an application on Windows

        Args:
            app_name: Name of the application to open

        Returns:
            Result dictionary
        """
        try:
            # Common Windows applications mapping
            common_apps = {
                "terminal": "wt.exe",  # Windows Terminal
                "cmd": "cmd.exe",
                "powershell": "powershell.exe",
                "notepad": "notepad.exe",
                "explorer": "explorer.exe",
                "chrome": "chrome.exe",
                "firefox": "firefox.exe",
                "edge": "msedge.exe",
                "code": "code.exe",
                "calculator": "calc.exe",
                "paint": "mspaint.exe",
            }

            # Try to map to known app
            exe_name = common_apps.get(app_name.lower(), app_name)

            # Try to start the application
            subprocess.Popen(
                ["start", "", exe_name],
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return {"success": True, "message": f"Opened {app_name}"}

        except Exception as e:
            return {"success": False, "message": f"Error opening {app_name}: {str(e)}"}

    @staticmethod
    def close_application(app_name: str) -> dict:
        """
        Close an application by name on Windows

        Args:
            app_name: Name of the application to close

        Returns:
            Result dictionary
        """
        try:
            # Use taskkill to terminate the application
            result = subprocess.run(
                ["taskkill", "/IM", f"{app_name}.exe", "/F"],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                return {"success": True, "message": f"Closed {app_name}"}
            else:
                # Try without .exe extension
                result = subprocess.run(
                    ["taskkill", "/IM", app_name, "/F"],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    return {"success": True, "message": f"Closed {app_name}"}
                else:
                    return {"success": False, "message": f"Process {app_name} not found"}

        except Exception as e:
            return {"success": False, "message": f"Error closing {app_name}: {str(e)}"}

    @staticmethod
    def run_terminal_command(command: str, working_dir: Optional[str] = None,
                            use_powershell: bool = True) -> dict:
        """
        Execute a terminal command on Windows

        Args:
            command: Command to execute
            working_dir: Optional working directory
            use_powershell: Use PowerShell instead of CMD

        Returns:
            Result with stdout, stderr, and return code
        """
        try:
            if use_powershell:
                # Run with PowerShell
                full_command = ["powershell.exe", "-Command", command]
            else:
                # Run with CMD
                full_command = ["cmd.exe", "/c", command]

            result = subprocess.run(
                full_command,
                capture_output=True,
                text=True,
                cwd=working_dir,
                timeout=30
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }

        except subprocess.TimeoutExpired:
            return {"success": False, "message": "Command timed out after 30 seconds"}
        except Exception as e:
            return {"success": False, "message": f"Error running command: {str(e)}"}

    @staticmethod
    def get_clipboard() -> dict:
        """Get clipboard content on Windows"""
        try:
            # Use PowerShell to get clipboard
            result = subprocess.run(
                ["powershell.exe", "-Command", "Get-Clipboard"],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                return {"success": True, "content": result.stdout}
            else:
                return {"success": False, "message": "Could not read clipboard"}

        except Exception as e:
            return {"success": False, "message": f"Error reading clipboard: {str(e)}"}

    @staticmethod
    def set_clipboard(content: str) -> dict:
        """Set clipboard content on Windows"""
        try:
            # Use PowerShell to set clipboard
            result = subprocess.run(
                ["powershell.exe", "-Command", f"Set-Clipboard -Value '{content}'"],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                return {"success": True, "message": "Clipboard updated"}
            else:
                return {"success": False, "message": "Failed to set clipboard"}

        except Exception as e:
            return {"success": False, "message": f"Error setting clipboard: {str(e)}"}

    @staticmethod
    def take_screenshot(filepath: Optional[str] = None) -> dict:
        """Take a screenshot on Windows"""
        try:
            if filepath is None:
                import tempfile
                filepath = os.path.join(tempfile.gettempdir(), f"screenshot_{os.getpid()}.png")

            # Use PowerShell to take screenshot
            ps_script = f"""
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$bitmap = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size)
$bitmap.Save('{filepath}')
$graphics.Dispose()
$bitmap.Dispose()
"""

            result = subprocess.run(
                ["powershell.exe", "-Command", ps_script],
                capture_output=True,
                text=True
            )

            if result.returncode == 0 and os.path.exists(filepath):
                return {"success": True, "filepath": filepath}
            else:
                return {"success": False, "message": "Screenshot failed"}

        except Exception as e:
            return {"success": False, "message": f"Error taking screenshot: {str(e)}"}

    @staticmethod
    def list_running_apps() -> dict:
        """List currently running applications on Windows"""
        try:
            # Use tasklist to get running processes
            result = subprocess.run(
                ["tasklist"],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                return {"success": True, "processes": result.stdout}
            else:
                return {"success": False, "message": "Could not list processes"}

        except Exception as e:
            return {"success": False, "message": f"Error listing apps: {str(e)}"}

    @staticmethod
    def get_system_info() -> dict:
        """Get Windows system information"""
        try:
            result = subprocess.run(
                ["systeminfo"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                return {"success": True, "info": result.stdout}
            else:
                return {"success": False, "message": "Could not get system info"}

        except Exception as e:
            return {"success": False, "message": f"Error getting system info: {str(e)}"}
