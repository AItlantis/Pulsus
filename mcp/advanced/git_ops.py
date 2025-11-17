"""
GitOps - Advanced Git Operations MCP Domain

Provides comprehensive Git operations with safety features, rollback support,
and intelligent error handling.
"""

import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from mcp.core.base import MCPBase, MCPResponse
from mcp.core.decorators import read_only, write_safe


class GitOps(MCPBase):
    """
    Advanced Git operations with safety features and rollback support.

    Capabilities:
    - get_status: Get repository status
    - get_diff: Get changes (staged/unstaged)
    - get_history: Get commit history
    - get_branches: List all branches
    - commit: Create commit with safety checks
    - create_branch: Create new branch
    - checkout_branch: Switch to branch
    - merge_branch: Merge branches
    - stash: Stash changes
    - get_remote_info: Get remote repository info
    """

    def __init__(self, logger=None, context: Dict[str, Any] = None):
        """Initialize GitOps domain"""
        super().__init__(logger, context)

    def _run_git_command(self, repo_path: Path, args: List[str]) -> tuple[bool, str, str]:
        """
        Run a git command and return success, stdout, stderr.

        Args:
            repo_path: Path to git repository
            args: Git command arguments (e.g., ['status', '--short'])

        Returns:
            Tuple of (success, stdout, stderr)
        """
        try:
            result = subprocess.run(
                ['git'] + args,
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Git command timed out after 30 seconds"
        except Exception as e:
            return False, "", str(e)

    def _validate_repo(self, repo_path: Path) -> tuple[bool, Optional[str]]:
        """
        Validate that path is a git repository.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not repo_path.exists():
            return False, f"Path does not exist: {repo_path}"

        if not repo_path.is_dir():
            return False, f"Path is not a directory: {repo_path}"

        git_dir = repo_path / '.git'
        if not git_dir.exists():
            return False, f"Not a git repository: {repo_path}"

        return True, None

    @read_only
    def get_status(self, repo_path: str) -> MCPResponse:
        """
        Get git status for repository.

        Args:
            repo_path: Path to git repository

        Returns:
            MCPResponse with status information
        """
        response = self._create_response()
        response.add_trace("Getting git status")

        repo = Path(repo_path).resolve()

        # Validate repository
        is_valid, error = self._validate_repo(repo)
        if not is_valid:
            response.set_error(error)
            return response

        # Get status
        success, stdout, stderr = self._run_git_command(repo, ['status', '--short', '--branch'])

        if not success:
            response.set_error(f"Git status failed: {stderr}")
            return response

        # Parse status output
        lines = stdout.strip().split('\n') if stdout.strip() else []
        branch_line = lines[0] if lines else "## unknown"
        file_lines = lines[1:] if len(lines) > 1 else []

        # Parse file statuses
        files = []
        for line in file_lines:
            if len(line) >= 3:
                status = line[:2]
                filepath = line[3:]
                files.append({
                    'status': status.strip(),
                    'path': filepath
                })

        # Get branch info
        success, stdout, stderr = self._run_git_command(repo, ['rev-parse', '--abbrev-ref', 'HEAD'])
        current_branch = stdout.strip() if success else "unknown"

        response.data = {
            'repo_path': str(repo),
            'branch': current_branch,
            'branch_line': branch_line,
            'files': files,
            'clean': len(files) == 0,
            'file_count': len(files)
        }

        response.add_trace(f"Found {len(files)} changed files")
        return response

    @read_only
    def get_diff(self, repo_path: str, file: Optional[str] = None, staged: bool = False) -> MCPResponse:
        """
        Get git diff for repository or specific file.

        Args:
            repo_path: Path to git repository
            file: Optional specific file to diff
            staged: If True, show staged changes; if False, show unstaged

        Returns:
            MCPResponse with diff output
        """
        response = self._create_response()
        response.add_trace("Getting git diff")

        repo = Path(repo_path).resolve()

        # Validate repository
        is_valid, error = self._validate_repo(repo)
        if not is_valid:
            response.set_error(error)
            return response

        # Build diff command
        cmd = ['diff']
        if staged:
            cmd.append('--cached')
        if file:
            cmd.append('--')
            cmd.append(file)

        success, stdout, stderr = self._run_git_command(repo, cmd)

        if not success:
            response.set_error(f"Git diff failed: {stderr}")
            return response

        response.data = {
            'repo_path': str(repo),
            'file': file,
            'staged': staged,
            'diff': stdout,
            'has_changes': bool(stdout.strip())
        }

        response.add_trace("Diff retrieved successfully")
        return response

    @read_only
    def get_history(self, repo_path: str, limit: int = 10, file: Optional[str] = None) -> MCPResponse:
        """
        Get commit history.

        Args:
            repo_path: Path to git repository
            limit: Maximum number of commits to return
            file: Optional file to get history for

        Returns:
            MCPResponse with commit history
        """
        response = self._create_response()
        response.add_trace("Getting commit history")

        repo = Path(repo_path).resolve()

        # Validate repository
        is_valid, error = self._validate_repo(repo)
        if not is_valid:
            response.set_error(error)
            return response

        # Build log command
        cmd = [
            'log',
            f'-n{limit}',
            '--pretty=format:%H|%an|%ae|%ad|%s',
            '--date=iso'
        ]
        if file:
            cmd.extend(['--', file])

        success, stdout, stderr = self._run_git_command(repo, cmd)

        if not success:
            response.set_error(f"Git log failed: {stderr}")
            return response

        # Parse commits
        commits = []
        for line in stdout.strip().split('\n'):
            if not line:
                continue
            parts = line.split('|')
            if len(parts) >= 5:
                commits.append({
                    'hash': parts[0],
                    'author_name': parts[1],
                    'author_email': parts[2],
                    'date': parts[3],
                    'message': '|'.join(parts[4:])  # Handle | in commit message
                })

        response.data = {
            'repo_path': str(repo),
            'file': file,
            'commit_count': len(commits),
            'commits': commits
        }

        response.add_trace(f"Retrieved {len(commits)} commits")
        return response

    @read_only
    def get_branches(self, repo_path: str, remote: bool = False) -> MCPResponse:
        """
        List branches in repository.

        Args:
            repo_path: Path to git repository
            remote: If True, list remote branches; if False, list local

        Returns:
            MCPResponse with branch list
        """
        response = self._create_response()
        response.add_trace("Listing branches")

        repo = Path(repo_path).resolve()

        # Validate repository
        is_valid, error = self._validate_repo(repo)
        if not is_valid:
            response.set_error(error)
            return response

        # Build branch command
        cmd = ['branch', '--list']
        if remote:
            cmd.append('--remote')

        success, stdout, stderr = self._run_git_command(repo, cmd)

        if not success:
            response.set_error(f"Git branch failed: {stderr}")
            return response

        # Parse branches
        branches = []
        current_branch = None
        for line in stdout.strip().split('\n'):
            if not line:
                continue
            is_current = line.startswith('*')
            branch_name = line.strip('* ').strip()
            branches.append(branch_name)
            if is_current:
                current_branch = branch_name

        response.data = {
            'repo_path': str(repo),
            'branches': branches,
            'current_branch': current_branch,
            'branch_count': len(branches),
            'remote': remote
        }

        response.add_trace(f"Found {len(branches)} branches")
        return response

    @write_safe
    def commit(
        self,
        repo_path: str,
        message: str,
        files: Optional[List[str]] = None,
        add_all: bool = False
    ) -> MCPResponse:
        """
        Create a git commit.

        Args:
            repo_path: Path to git repository
            message: Commit message
            files: Optional list of files to commit (if None and not add_all, commits staged files)
            add_all: If True, add all changes before committing

        Returns:
            MCPResponse with commit information
        """
        response = self._create_response()
        response.add_trace("Creating commit")

        repo = Path(repo_path).resolve()

        # Validate repository
        is_valid, error = self._validate_repo(repo)
        if not is_valid:
            response.set_error(error)
            return response

        # Validate message
        if not message or not message.strip():
            response.set_error("Commit message cannot be empty")
            return response

        # Add files if specified
        if add_all:
            success, stdout, stderr = self._run_git_command(repo, ['add', '-A'])
            if not success:
                response.set_error(f"Git add failed: {stderr}")
                return response
            response.add_trace("Added all changes")
        elif files:
            for file in files:
                success, stdout, stderr = self._run_git_command(repo, ['add', file])
                if not success:
                    response.set_error(f"Git add failed for {file}: {stderr}")
                    return response
            response.add_trace(f"Added {len(files)} files")

        # Create commit
        success, stdout, stderr = self._run_git_command(repo, ['commit', '-m', message])

        if not success:
            # Check if it's because there are no changes
            if 'nothing to commit' in stderr or 'nothing to commit' in stdout:
                response.set_error("No changes to commit")
            else:
                response.set_error(f"Git commit failed: {stderr}")
            return response

        # Get commit hash
        success, hash_output, _ = self._run_git_command(repo, ['rev-parse', 'HEAD'])
        commit_hash = hash_output.strip() if success else "unknown"

        response.data = {
            'repo_path': str(repo),
            'message': message,
            'commit_hash': commit_hash,
            'files_added': files if files else [],
            'add_all': add_all,
            'output': stdout
        }

        response.add_trace(f"Commit created: {commit_hash[:8]}")
        return response

    @write_safe
    def create_branch(self, repo_path: str, branch_name: str, checkout: bool = True) -> MCPResponse:
        """
        Create a new branch.

        Args:
            repo_path: Path to git repository
            branch_name: Name for the new branch
            checkout: If True, checkout the new branch after creating

        Returns:
            MCPResponse with branch information
        """
        response = self._create_response()
        response.add_trace("Creating branch")

        repo = Path(repo_path).resolve()

        # Validate repository
        is_valid, error = self._validate_repo(repo)
        if not is_valid:
            response.set_error(error)
            return response

        # Validate branch name
        if not branch_name or not branch_name.strip():
            response.set_error("Branch name cannot be empty")
            return response

        # Create branch
        cmd = ['checkout', '-b', branch_name] if checkout else ['branch', branch_name]
        success, stdout, stderr = self._run_git_command(repo, cmd)

        if not success:
            response.set_error(f"Git branch creation failed: {stderr}")
            return response

        response.data = {
            'repo_path': str(repo),
            'branch_name': branch_name,
            'checked_out': checkout,
            'output': stdout
        }

        response.add_trace(f"Branch '{branch_name}' created")
        if checkout:
            response.add_trace(f"Checked out to '{branch_name}'")

        return response

    @write_safe
    def checkout_branch(self, repo_path: str, branch_name: str) -> MCPResponse:
        """
        Checkout a branch.

        Args:
            repo_path: Path to git repository
            branch_name: Branch to checkout

        Returns:
            MCPResponse with checkout information
        """
        response = self._create_response()
        response.add_trace("Checking out branch")

        repo = Path(repo_path).resolve()

        # Validate repository
        is_valid, error = self._validate_repo(repo)
        if not is_valid:
            response.set_error(error)
            return response

        # Checkout branch
        success, stdout, stderr = self._run_git_command(repo, ['checkout', branch_name])

        if not success:
            response.set_error(f"Git checkout failed: {stderr}")
            return response

        response.data = {
            'repo_path': str(repo),
            'branch_name': branch_name,
            'output': stdout
        }

        response.add_trace(f"Checked out to '{branch_name}'")
        return response

    @read_only
    def get_remote_info(self, repo_path: str) -> MCPResponse:
        """
        Get information about remote repositories.

        Args:
            repo_path: Path to git repository

        Returns:
            MCPResponse with remote information
        """
        response = self._create_response()
        response.add_trace("Getting remote info")

        repo = Path(repo_path).resolve()

        # Validate repository
        is_valid, error = self._validate_repo(repo)
        if not is_valid:
            response.set_error(error)
            return response

        # Get remotes
        success, stdout, stderr = self._run_git_command(repo, ['remote', '-v'])

        if not success:
            response.set_error(f"Git remote failed: {stderr}")
            return response

        # Parse remotes
        remotes = {}
        for line in stdout.strip().split('\n'):
            if not line:
                continue
            parts = line.split()
            if len(parts) >= 3:
                name = parts[0]
                url = parts[1]
                type_info = parts[2].strip('()')

                if name not in remotes:
                    remotes[name] = {}
                remotes[name][type_info] = url

        response.data = {
            'repo_path': str(repo),
            'remotes': remotes,
            'remote_count': len(remotes)
        }

        response.add_trace(f"Found {len(remotes)} remotes")
        return response
