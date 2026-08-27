"""
File Tools

File system operations with safety checks
"""
import os
from pathlib import Path
from typing import Optional, List

class FileTools:
    """File system operation tools"""

    @staticmethod
    def read_file(filepath: str) -> dict:
        """Read file contents"""
        try:
            path = Path(filepath).expanduser().resolve()

            if not path.exists():
                return {"success": False, "message": f"File not found: {filepath}"}

            if not path.is_file():
                return {"success": False, "message": f"Not a file: {filepath}"}

            with open(path, 'r') as f:
                content = f.read()

            return {
                "success": True,
                "content": content,
                "filepath": str(path)
            }
        except PermissionError:
            return {"success": False, "message": f"Permission denied: {filepath}"}
        except Exception as e:
            return {"success": False, "message": f"Error reading file: {str(e)}"}

    @staticmethod
    def write_file(filepath: str, content: str) -> dict:
        """Write content to file"""
        try:
            path = Path(filepath).expanduser().resolve()
            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, 'w') as f:
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
        """Delete a file"""
        try:
            path = Path(filepath).expanduser().resolve()

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
        """List files in directory"""
        try:
            path = Path(dirpath).expanduser().resolve()

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
                "count": len(files)
            }
        except PermissionError:
            return {"success": False, "message": f"Permission denied: {dirpath}"}
        except Exception as e:
            return {"success": False, "message": f"Error listing directory: {str(e)}"}

    @staticmethod
    def create_directory(dirpath: str) -> dict:
        """Create a directory"""
        try:
            path = Path(dirpath).expanduser().resolve()
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
        """Check if file exists"""
        try:
            path = Path(filepath).expanduser().resolve()
            exists = path.exists()

            return {
                "success": True,
                "exists": exists,
                "is_file": path.is_file() if exists else False,
                "is_dir": path.is_dir() if exists else False
            }
        except Exception as e:
            return {"success": False, "message": f"Error checking file: {str(e)}"}
