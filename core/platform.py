"""
Platform Detection and Abstraction Layer

Detects OS and provides unified interface for cross-platform operations
"""
import platform
import sys
from enum import Enum
from typing import Optional

class Platform(Enum):
    """Supported platforms"""
    LINUX = "linux"
    WINDOWS = "windows"
    MACOS = "macos"
    UNKNOWN = "unknown"

class PlatformDetector:
    """Detect and provide platform-specific information"""

    @staticmethod
    def detect() -> Platform:
        """
        Detect current operating system

        Returns:
            Platform enum
        """
        system = platform.system().lower()

        if system == "linux":
            return Platform.LINUX
        elif system == "windows":
            return Platform.WINDOWS
        elif system == "darwin":
            return Platform.MACOS
        else:
            return Platform.UNKNOWN

    @staticmethod
    def is_linux() -> bool:
        """Check if running on Linux"""
        return PlatformDetector.detect() == Platform.LINUX

    @staticmethod
    def is_windows() -> bool:
        """Check if running on Windows"""
        return PlatformDetector.detect() == Platform.WINDOWS

    @staticmethod
    def is_macos() -> bool:
        """Check if running on macOS"""
        return PlatformDetector.detect() == Platform.MACOS

    @staticmethod
    def get_platform_info() -> dict:
        """Get detailed platform information"""
        return {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": sys.version,
            "detected_platform": PlatformDetector.detect().value
        }

    @staticmethod
    def get_default_shell() -> str:
        """Get default shell for the platform"""
        if PlatformDetector.is_windows():
            return "powershell"
        elif PlatformDetector.is_linux():
            return "bash"
        elif PlatformDetector.is_macos():
            return "zsh"
        else:
            return "sh"

    @staticmethod
    def get_path_separator() -> str:
        """Get path separator for the platform"""
        if PlatformDetector.is_windows():
            return "\\"
        else:
            return "/"

    @staticmethod
    def normalize_path(path: str) -> str:
        """Normalize path for current platform"""
        import os
        return os.path.normpath(path)

# Global platform detection
CURRENT_PLATFORM = PlatformDetector.detect()
IS_LINUX = CURRENT_PLATFORM == Platform.LINUX
IS_WINDOWS = CURRENT_PLATFORM == Platform.WINDOWS
IS_MACOS = CURRENT_PLATFORM == Platform.MACOS
