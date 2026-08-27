"""
OS Tools for Linux

System-level operations: app control, terminal, clipboard, screenshots
"""
import subprocess
import os
from typing import Optional, List

class OSTools:
    """Linux system automation tools"""

    @staticmethod
    def open_application(app_name: str) -> dict:
        """
        Open an application on Linux

        Args:
            app_name: Name of the application to open

        Returns:
            Result dictionary with success status and message
        """
        try:
            # Try to launch the application
            subprocess.Popen([app_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return {"success": True, "message": f"Opened {app_name}"}
        except FileNotFoundError:
            # Try with common paths
            common_apps = {
                "terminal": "gnome-terminal",
                "browser": "firefox",
                "chrome": "google-chrome",
                "code": "code",
                "files": "nautilus",
                "calculator": "gnome-calculator"
            }

            if app_name.lower() in common_apps:
                try:
                    subprocess.Popen([common_apps[app_name.lower()]],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return {"success": True, "message": f"Opened {common_apps[app_name.lower()]}"}
                except Exception as e:
                    return {"success": False, "message": f"Failed to open {app_name}: {str(e)}"}

            return {"success": False, "message": f"Application '{app_name}' not found"}
        except Exception as e:
            return {"success": False, "message": f"Error opening {app_name}: {str(e)}"}

    @staticmethod
    def close_application(app_name: str) -> dict:
        """
        Close an application by name

        Args:
            app_name: Name of the application to close

        Returns:
            Result dictionary
        """
        try:
            # Use pkill to terminate the application
            result = subprocess.run(["pkill", "-f", app_name], capture_output=True)
            if result.returncode == 0:
                return {"success": True, "message": f"Closed {app_name}"}
            else:
                return {"success": False, "message": f"No process found for {app_name}"}
        except Exception as e:
            return {"success": False, "message": f"Error closing {app_name}: {str(e)}"}

    @staticmethod
    def run_terminal_command(command: str, working_dir: Optional[str] = None) -> dict:
        """
        Execute a terminal command

        Args:
            command: Shell command to execute
            working_dir: Optional working directory

        Returns:
            Result with stdout, stderr, and return code
        """
        try:
            result = subprocess.run(
                command,
                shell=True,
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
        """Get clipboard content"""
        try:
            result = subprocess.run(["xclip", "-selection", "clipboard", "-o"],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return {"success": True, "content": result.stdout}
            else:
                return {"success": False, "message": "Could not read clipboard"}
        except FileNotFoundError:
            return {"success": False, "message": "xclip not installed. Install with: sudo apt install xclip"}
        except Exception as e:
            return {"success": False, "message": f"Error reading clipboard: {str(e)}"}

    @staticmethod
    def set_clipboard(content: str) -> dict:
        """Set clipboard content"""
        try:
            process = subprocess.Popen(
                ["xclip", "-selection", "clipboard"],
                stdin=subprocess.PIPE
            )
            process.communicate(content.encode())

            if process.returncode == 0:
                return {"success": True, "message": "Clipboard updated"}
            else:
                return {"success": False, "message": "Failed to set clipboard"}
        except FileNotFoundError:
            return {"success": False, "message": "xclip not installed"}
        except Exception as e:
            return {"success": False, "message": f"Error setting clipboard: {str(e)}"}

    @staticmethod
    def take_screenshot(filepath: Optional[str] = None) -> dict:
        """Take a screenshot"""
        try:
            if filepath is None:
                filepath = f"/tmp/screenshot_{os.getpid()}.png"

            result = subprocess.run(["scrot", filepath], capture_output=True)

            if result.returncode == 0:
                return {"success": True, "filepath": filepath}
            else:
                return {"success": False, "message": "Screenshot failed"}
        except FileNotFoundError:
            return {"success": False, "message": "scrot not installed. Install with: sudo apt install scrot"}
        except Exception as e:
            return {"success": False, "message": f"Error taking screenshot: {str(e)}"}

    @staticmethod
    def list_running_apps() -> dict:
        """List currently running applications"""
        try:
            result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
            if result.returncode == 0:
                return {"success": True, "processes": result.stdout}
            else:
                return {"success": False, "message": "Could not list processes"}
        except Exception as e:
            return {"success": False, "message": f"Error listing apps: {str(e)}"}
