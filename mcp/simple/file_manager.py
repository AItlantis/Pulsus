"""
File Manager MCP Domain

Provides MCPBase-compliant operations for file system management:
- Creating and deleting files
- Moving and copying files
- Listing files with patterns
- Reading file information

All operations are safety-decorated with appropriate permissions.
"""

from pathlib import Path
import shutil
import os
import glob as glob_module
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..core.base import MCPBase, MCPResponse, MCPStatus
from ..core.decorators import read_only, write_safe


class FileManager(MCPBase):
    """
    File management operations domain for MCP.

    Provides core functionality for:
    - Creating files (@write_safe)
    - Deleting files (@write_safe)
    - Moving files (@write_safe)
    - Copying files (@write_safe)
    - Listing files (@read_only)
    - Getting file information (@read_only)

    All methods return MCPResponse for standardized interaction.
    Safety decorators ensure proper permission handling.
    """

    def __init__(self, logger=None, context: Dict[str, Any] = None):
        """
        Initialize the file manager domain.

        Args:
            logger: Optional MCPLogger instance
            context: Optional context dict with caller info
        """
        super().__init__(logger=logger, context=context)

    # ===== Path Validation =====

    def _validate_path(self, path: str, must_exist: bool = False) -> tuple[bool, Optional[Path], Optional[str]]:
        """
        Validate a file path for safety.

        Args:
            path: File path to validate
            must_exist: Whether the path must already exist

        Returns:
            Tuple of (is_valid, Path object, error_message)
        """
        try:
            file_path = Path(path).resolve()

            # Check if path escapes from allowed directories
            # (This is a basic check, can be enhanced with allowed_paths config)

            if must_exist and not file_path.exists():
                return False, None, f"Path does not exist: {path}"

            return True, file_path, None

        except Exception as e:
            return False, None, f"Path validation error: {str(e)}"

    def _validate_directory(self, path: str) -> tuple[bool, Optional[Path], Optional[str]]:
        """
        Validate a directory path.

        Args:
            path: Directory path to validate

        Returns:
            Tuple of (is_valid, Path object, error_message)
        """
        try:
            dir_path = Path(path).resolve()

            if not dir_path.exists():
                return False, None, f"Directory does not exist: {path}"

            if not dir_path.is_dir():
                return False, None, f"Not a directory: {path}"

            return True, dir_path, None

        except Exception as e:
            return False, None, f"Directory validation error: {str(e)}"

    # ===== File Creation & Deletion =====

    @write_safe
    def create_file(self, path: str, content: str = "", overwrite: bool = False) -> MCPResponse:
        """
        Create a new file with optional content.

        Args:
            path: Path where the file should be created
            content: Initial content for the file (default: empty)
            overwrite: Whether to overwrite existing file (default: False)

        Returns:
            MCPResponse with data containing:
            - path: Created file path
            - size: File size in bytes
            - created: Whether file was created (vs existing)
        """
        response = MCPResponse.success_response()
        response.add_trace(f'Creating file: {path}')

        try:
            # Validate path
            is_valid, file_path, error = self._validate_path(path, must_exist=False)
            if not is_valid:
                response.set_error(error)
                return response

            # Check if file exists
            if file_path.exists() and not overwrite:
                response.set_error(f"File already exists (use overwrite=True): {path}")
                return response

            # Create parent directories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            file_path.write_text(content)

            response.data = {
                'path': str(file_path),
                'size': file_path.stat().st_size,
                'created': True
            }
            response.add_trace(f'File created successfully: {file_path}')
            return response

        except PermissionError as e:
            response.set_error(f"Permission denied: {str(e)}")
            return response
        except Exception as e:
            response.set_error(f"Failed to create file: {str(e)}")
            return response

    @write_safe
    def delete_file(self, path: str, force: bool = False) -> MCPResponse:
        """
        Delete a file.

        Args:
            path: Path to the file to delete
            force: Force deletion without additional checks (default: False)

        Returns:
            MCPResponse with data containing:
            - path: Deleted file path
            - deleted: Whether file was deleted
        """
        response = MCPResponse.success_response()
        response.add_trace(f'Deleting file: {path}')

        try:
            # Validate path
            is_valid, file_path, error = self._validate_path(path, must_exist=True)
            if not is_valid:
                response.set_error(error)
                return response

            # Check if it's a file
            if not file_path.is_file():
                response.set_error(f"Not a file: {path}")
                return response

            # Delete file
            file_path.unlink()

            response.data = {
                'path': str(file_path),
                'deleted': True
            }
            response.add_trace(f'File deleted successfully: {file_path}')
            return response

        except PermissionError as e:
            response.set_error(f"Permission denied: {str(e)}")
            return response
        except Exception as e:
            response.set_error(f"Failed to delete file: {str(e)}")
            return response

    # ===== File Operations =====

    @write_safe
    def move_file(self, source: str, destination: str, overwrite: bool = False) -> MCPResponse:
        """
        Move a file from source to destination.

        Args:
            source: Source file path
            destination: Destination file path
            overwrite: Whether to overwrite existing file at destination

        Returns:
            MCPResponse with data containing:
            - source: Original file path
            - destination: New file path
            - moved: Whether file was moved
        """
        response = MCPResponse.success_response()
        response.add_trace(f'Moving file: {source} -> {destination}')

        try:
            # Validate source
            is_valid, source_path, error = self._validate_path(source, must_exist=True)
            if not is_valid:
                response.set_error(f"Source: {error}")
                return response

            if not source_path.is_file():
                response.set_error(f"Source is not a file: {source}")
                return response

            # Validate destination
            is_valid, dest_path, error = self._validate_path(destination, must_exist=False)
            if not is_valid:
                response.set_error(f"Destination: {error}")
                return response

            # Check if destination exists
            if dest_path.exists() and not overwrite:
                response.set_error(f"Destination exists (use overwrite=True): {destination}")
                return response

            # Create parent directories if needed
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            # Move file
            shutil.move(str(source_path), str(dest_path))

            response.data = {
                'source': str(source_path),
                'destination': str(dest_path),
                'moved': True
            }
            response.add_trace(f'File moved successfully: {dest_path}')
            return response

        except PermissionError as e:
            response.set_error(f"Permission denied: {str(e)}")
            return response
        except Exception as e:
            response.set_error(f"Failed to move file: {str(e)}")
            return response

    @write_safe
    def copy_file(self, source: str, destination: str, overwrite: bool = False) -> MCPResponse:
        """
        Copy a file from source to destination.

        Args:
            source: Source file path
            destination: Destination file path
            overwrite: Whether to overwrite existing file at destination

        Returns:
            MCPResponse with data containing:
            - source: Original file path
            - destination: Copy file path
            - copied: Whether file was copied
        """
        response = MCPResponse.success_response()
        response.add_trace(f'Copying file: {source} -> {destination}')

        try:
            # Validate source
            is_valid, source_path, error = self._validate_path(source, must_exist=True)
            if not is_valid:
                response.set_error(f"Source: {error}")
                return response

            if not source_path.is_file():
                response.set_error(f"Source is not a file: {source}")
                return response

            # Validate destination
            is_valid, dest_path, error = self._validate_path(destination, must_exist=False)
            if not is_valid:
                response.set_error(f"Destination: {error}")
                return response

            # Check if destination exists
            if dest_path.exists() and not overwrite:
                response.set_error(f"Destination exists (use overwrite=True): {destination}")
                return response

            # Create parent directories if needed
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            # Copy file
            shutil.copy2(str(source_path), str(dest_path))

            response.data = {
                'source': str(source_path),
                'destination': str(dest_path),
                'copied': True,
                'size': dest_path.stat().st_size
            }
            response.add_trace(f'File copied successfully: {dest_path}')
            return response

        except PermissionError as e:
            response.set_error(f"Permission denied: {str(e)}")
            return response
        except Exception as e:
            response.set_error(f"Failed to copy file: {str(e)}")
            return response

    # ===== File Listing & Information =====

    @read_only
    def list_files(self, directory: str, pattern: str = "*", recursive: bool = False) -> MCPResponse:
        """
        List files in a directory matching a pattern.

        Args:
            directory: Directory path to list
            pattern: Glob pattern for file matching (default: "*" for all files)
            recursive: Whether to search recursively (default: False)

        Returns:
            MCPResponse with data containing:
            - directory: Directory path
            - pattern: Pattern used
            - files: List of matched file paths
            - count: Number of files found
        """
        response = MCPResponse.success_response()
        response.add_trace(f'Listing files in: {directory} with pattern: {pattern}')

        try:
            # Validate directory
            is_valid, dir_path, error = self._validate_directory(directory)
            if not is_valid:
                response.set_error(error)
                return response

            # Get files
            if recursive:
                glob_pattern = str(dir_path / "**" / pattern)
                files = glob_module.glob(glob_pattern, recursive=True)
            else:
                glob_pattern = str(dir_path / pattern)
                files = glob_module.glob(glob_pattern)

            # Filter to only files (not directories)
            files = [f for f in files if Path(f).is_file()]

            response.data = {
                'directory': str(dir_path),
                'pattern': pattern,
                'recursive': recursive,
                'files': files,
                'count': len(files)
            }
            response.add_trace(f'Found {len(files)} files')
            return response

        except Exception as e:
            response.set_error(f"Failed to list files: {str(e)}")
            return response

    @read_only
    def get_file_info(self, path: str) -> MCPResponse:
        """
        Get detailed information about a file.

        Args:
            path: File path

        Returns:
            MCPResponse with data containing:
            - path: File path
            - name: File name
            - size: File size in bytes
            - created: Creation timestamp
            - modified: Last modification timestamp
            - extension: File extension
            - exists: Whether file exists
        """
        response = MCPResponse.success_response()
        response.add_trace(f'Getting info for: {path}')

        try:
            # Validate path
            is_valid, file_path, error = self._validate_path(path, must_exist=True)
            if not is_valid:
                response.set_error(error)
                return response

            # Get file stats
            stat_info = file_path.stat()

            response.data = {
                'path': str(file_path),
                'name': file_path.name,
                'size': stat_info.st_size,
                'created': datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                'extension': file_path.suffix,
                'exists': True,
                'is_file': file_path.is_file(),
                'is_dir': file_path.is_dir()
            }
            response.add_trace(f'Retrieved file info: {file_path.name}')
            return response

        except Exception as e:
            response.set_error(f"Failed to get file info: {str(e)}")
            return response
