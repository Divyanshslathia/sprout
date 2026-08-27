"""
Cross-Platform File Tools

Unified file operations that work on both Linux and Windows
"""
import os
from pathlib import Path
from typing import Optional, List
from core.platform import PlatformDetector

class CrossPlatformFileTools:
    """File system operations with cross-platform path handling"""

    @staticmethod
    def normalize_path(filepath: str) -> Path:
        """Convert path to platform-appropriate format"""
        # Expand ~ to home directory
        path = Path(filepath).expanduser().resolve()
        return path

    @staticmethod
    def read_file(filepath: str) -> dict:
        """Read file contents (cross-platform)"""
        try:
            path = CrossPlatformFileTools.normalize_path(filepath)

            if not path.exists():
                return {"success": False, "message": f"File not found: {filepath}"}

            if not path.is_file():
                return {"success": False, "message": f"Not a file: {filepath}"}

            # Handle different encodings
            encodings = ['utf-8', 'utf-16', 'cp1252', 'latin-1']
            content = None

            for encoding in encodings:
                try:
                    with open(path, 'r', encoding=encoding) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue

            if content is None:
                return {"success": False, "message": "Could not decode file"}

            return {
                "success": True,
                "content": content,
                "filepath": str(path),
                "platform": PlatformDetector.detect().value
            }

        except PermissionError:
            return {"success": False, "message": f"Permission denied: {filepath}"}
        except Exception as e:
            return {"success": False, "message": f"Error reading file: {str(e)}"}

    @staticmethod
    def write_file(filepath: str, content: str) -> dict:
        """Write content to file (cross-platform)"""
        try:
            path = CrossPlatformFileTools.normalize_path(filepath)
            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)

            return {
                "success": True,
                "message": f"File written: {filepath}",
                "filepath": str(path)
            }

        except PermissionError:
            return {"success": False, "message": f"Permission denied: {filepath}"}
        except Exception as e:
            return {"success": False, "message": f"Error writing file: {str(e)}"}

    @staticmethod
    def delete_file(filepath: str) -> dict:
        """Delete a file (cross-platform)"""
        try:
            path = CrossPlatformFileTools.normalize_path(filepath)

            if not path.exists():
                return {"success": False, "message": f"File not found: {filepath}"}

            if not path.is_file():
                return {"success": False, "message": f"Not a file: {filepath}"}

            path.unlink()

            return {
                "success": True,
                "message": f"File deleted: {filepath}"
            }

        except PermissionError:
            return {"success": False, "message": f"Permission denied: {filepath}"}
        except Exception as e:
            return {"success": False, "message": f"Error deleting file: {str(e)}"}

    @staticmethod
    def list_directory(dirpath: str) -> dict:
        """List files in directory (cross-platform)"""
        try:
            path = CrossPlatformFileTools.normalize_path(dirpath)

            if not path.exists():
                return {"success": False, "message": f"Directory not found: {dirpath}"}

            if not path.is_dir():
                return {"success": False, "message": f"Not a directory: {dirpath}"}

            files = []
            for item in path.iterdir():
                files.append({
                    "name": item.name,
                    "type": "dir" if item.is_dir() else "file",
                    "path": str(item)
                })

            return {
                "success": True,
                "files": files,
                "count": len(files),
                "platform": PlatformDetector.detect().value
            }

        except PermissionError:
            return {"success": False, "message": f"Permission denied: {dirpath}"}
        except Exception as e:
            return {"success": False, "message": f"Error listing directory: {str(e)}"}

    @staticmethod
    def create_directory(dirpath: str) -> dict:
        """Create a directory (cross-platform)"""
        try:
            path = CrossPlatformFileTools.normalize_path(dirpath)
            path.mkdir(parents=True, exist_ok=True)

            return {
                "success": True,
                "message": f"Directory created: {dirpath}",
                "path": str(path)
            }

        except PermissionError:
            return {"success": False, "message": f"Permission denied: {dirpath}"}
        except Exception as e:
            return {"success": False, "message": f"Error creating directory: {str(e)}"}

    @staticmethod
    def file_exists(filepath: str) -> dict:
        """Check if file exists (cross-platform)"""
        try:
            path = CrossPlatformFileTools.normalize_path(filepath)
            exists = path.exists()

            return {
                "success": True,
                "exists": exists,
                "is_file": path.is_file() if exists else False,
                "is_dir": path.is_dir() if exists else False,
                "platform": PlatformDetector.detect().value
            }

        except Exception as e:
            return {"success": False, "message": f"Error checking file: {str(e)}"}
