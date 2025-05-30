import os
import json
from typing import Dict, Any, List
from datetime import datetime
import shutil

class FileManager:
    """File management tool (placeholder implementation with limited scope for safety)"""
    
    @staticmethod
    def get_tool_info() -> Dict[str, Any]:
        """Get tool information for LLM"""
        return {
            "name": "file_manager",
            "description": "Manage files and directories including listing, reading, writing, and organizing files",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "File operation to perform",
                        "enum": ["list_files", "read_file", "write_file", "create_directory", "delete_file", "move_file", "copy_file", "get_file_info"]
                    },
                    "path": {
                        "type": "string",
                        "description": "File or directory path"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to file (for write_file action)"
                    },
                    "destination": {
                        "type": "string",
                        "description": "Destination path (for move_file, copy_file actions)"
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "Whether to perform operation recursively (default: false)"
                    },
                    "filter_extension": {
                        "type": "string",
                        "description": "Filter files by extension (e.g., '.txt', '.py')"
                    }
                },
                "required": ["action", "path"]
            }
        }
    
    @staticmethod
    def execute(action: str, path: str, content: str = None, destination: str = None, 
                recursive: bool = False, filter_extension: str = None) -> Dict[str, Any]:
        """Execute file management operation (limited for safety)"""
        try:
            # Safety check - only allow operations in safe directories
            safe_paths = ["./documents", "./temp", "./downloads", "./workspace"]
            if not any(path.startswith(safe_path) for safe_path in safe_paths):
                return {"error": "File operations are restricted to safe directories: " + ", ".join(safe_paths)}
            
            if action == "list_files":
                return FileManager._list_files(path, recursive, filter_extension)
            elif action == "read_file":
                return FileManager._read_file(path)
            elif action == "write_file":
                return FileManager._write_file(path, content)
            elif action == "create_directory":
                return FileManager._create_directory(path)
            elif action == "delete_file":
                return FileManager._delete_file(path)
            elif action == "move_file":
                return FileManager._move_file(path, destination)
            elif action == "copy_file":
                return FileManager._copy_file(path, destination)
            elif action == "get_file_info":
                return FileManager._get_file_info(path)
            else:
                return {"error": f"Unknown file action: {action}"}
                
        except Exception as e:
            return {"error": f"File operation error: {str(e)}"}
    
    @staticmethod
    def _list_files(path: str, recursive: bool = False, filter_extension: str = None) -> Dict[str, Any]:
        """List files in directory"""
        if not os.path.exists(path):
            return {"error": f"Path does not exist: {path}"}
        
        if not os.path.isdir(path):
            return {"error": f"Path is not a directory: {path}"}
        
        files = []
        directories = []
        
        try:
            if recursive:
                for root, dirs, filenames in os.walk(path):
                    for filename in filenames:
                        if filter_extension is None or filename.endswith(filter_extension):
                            file_path = os.path.join(root, filename)
                            stat = os.stat(file_path)
                            files.append({
                                "name": filename,
                                "path": file_path,
                                "size": stat.st_size,
                                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                                "type": "file"
                            })
                    for dirname in dirs:
                        dir_path = os.path.join(root, dirname)
                        directories.append({
                            "name": dirname,
                            "path": dir_path,
                            "type": "directory"
                        })
            else:
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    if os.path.isfile(item_path):
                        if filter_extension is None or item.endswith(filter_extension):
                            stat = os.stat(item_path)
                            files.append({
                                "name": item,
                                "path": item_path,
                                "size": stat.st_size,
                                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                                "type": "file"
                            })
                    elif os.path.isdir(item_path):
                        directories.append({
                            "name": item,
                            "path": item_path,
                            "type": "directory"
                        })
            
            return {
                "action": "list_files",
                "path": path,
                "files": files,
                "directories": directories,
                "total_files": len(files),
                "total_directories": len(directories),
                "recursive": recursive,
                "filter_extension": filter_extension
            }
            
        except PermissionError:
            return {"error": f"Permission denied: {path}"}
    
    @staticmethod
    def _read_file(path: str) -> Dict[str, Any]:
        """Read file content"""
        if not os.path.exists(path):
            return {"error": f"File does not exist: {path}"}
        
        if not os.path.isfile(path):
            return {"error": f"Path is not a file: {path}"}
        
        try:
            # Check file size (limit to 1MB for safety)
            if os.path.getsize(path) > 1024 * 1024:
                return {"error": "File too large (>1MB). Use a file chunk reader for large files."}
            
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            stat = os.stat(path)
            return {
                "action": "read_file",
                "path": path,
                "content": content,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "lines": len(content.split('\n'))
            }
            
        except UnicodeDecodeError:
            return {"error": "File contains binary data or unsupported encoding"}
        except PermissionError:
            return {"error": f"Permission denied: {path}"}
    
    @staticmethod
    def _write_file(path: str, content: str = "") -> Dict[str, Any]:
        """Write content to file"""
        if content is None:
            content = ""
        
        try:
            # Create directories if they don't exist
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            stat = os.stat(path)
            return {
                "action": "write_file",
                "path": path,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "lines_written": len(content.split('\n')),
                "message": f"Successfully wrote {len(content)} characters to {path}"
            }
            
        except PermissionError:
            return {"error": f"Permission denied: {path}"}
    
    @staticmethod
    def _create_directory(path: str) -> Dict[str, Any]:
        """Create directory"""
        try:
            os.makedirs(path, exist_ok=True)
            return {
                "action": "create_directory",
                "path": path,
                "message": f"Directory created: {path}"
            }
        except PermissionError:
            return {"error": f"Permission denied: {path}"}
    
    @staticmethod
    def _delete_file(path: str) -> Dict[str, Any]:
        """Delete file or directory"""
        if not os.path.exists(path):
            return {"error": f"Path does not exist: {path}"}
        
        try:
            if os.path.isfile(path):
                os.remove(path)
                return {
                    "action": "delete_file",
                    "path": path,
                    "message": f"File deleted: {path}"
                }
            elif os.path.isdir(path):
                shutil.rmtree(path)
                return {
                    "action": "delete_file",
                    "path": path,
                    "message": f"Directory deleted: {path}"
                }
        except PermissionError:
            return {"error": f"Permission denied: {path}"}
    
    @staticmethod
    def _move_file(path: str, destination: str) -> Dict[str, Any]:
        """Move file or directory"""
        if not os.path.exists(path):
            return {"error": f"Source path does not exist: {path}"}
        
        try:
            shutil.move(path, destination)
            return {
                "action": "move_file",
                "source": path,
                "destination": destination,
                "message": f"Moved {path} to {destination}"
            }
        except PermissionError:
            return {"error": "Permission denied"}
        except shutil.Error as e:
            return {"error": f"Move operation failed: {str(e)}"}
    
    @staticmethod
    def _copy_file(path: str, destination: str) -> Dict[str, Any]:
        """Copy file or directory"""
        if not os.path.exists(path):
            return {"error": f"Source path does not exist: {path}"}
        
        try:
            if os.path.isfile(path):
                shutil.copy2(path, destination)
            elif os.path.isdir(path):
                shutil.copytree(path, destination)
            
            return {
                "action": "copy_file",
                "source": path,
                "destination": destination,
                "message": f"Copied {path} to {destination}"
            }
        except PermissionError:
            return {"error": "Permission denied"}
        except shutil.Error as e:
            return {"error": f"Copy operation failed: {str(e)}"}
    
    @staticmethod
    def _get_file_info(path: str) -> Dict[str, Any]:
        """Get file information"""
        if not os.path.exists(path):
            return {"error": f"Path does not exist: {path}"}
        
        try:
            stat = os.stat(path)
            return {
                "action": "get_file_info",
                "path": path,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "is_file": os.path.isfile(path),
                "is_directory": os.path.isdir(path),
                "permissions": oct(stat.st_mode)[-3:]
            }
        except PermissionError:
            return {"error": f"Permission denied: {path}"} 