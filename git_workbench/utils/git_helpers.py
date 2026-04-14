import subprocess
import os
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CommitInfo:
    hash: str
    short_hash: str
    author: str
    email: str
    date: datetime
    message: str
    files_changed: int = 0
    insertions: int = 0
    deletions: int = 0


@dataclass
class BranchInfo:
    name: str
    is_current: bool
    is_merged: bool
    last_commit_date: Optional[datetime] = None
    author: str = ""


class GitHelper:
    """Helper class for Git operations"""

    @staticmethod
    def run_command(cmd: List[str], cwd: Optional[str] = None) -> Tuple[bool, str]:
        """Run a git command and return success status and output"""
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=cwd or os.getcwd()
            )
            if result.returncode == 0:
                return True, result.stdout.strip()
            return False, result.stderr.strip()
        except Exception as e:
            return False, str(e)

    @staticmethod
    def is_git_repo(path: Optional[str] = None) -> bool:
        """Check if current directory is a git repository"""
        success, _ = GitHelper.run_command(["git", "rev-parse", "--git-dir"], path)
        return success

    @staticmethod
    def get_current_branch() -> Optional[str]:
        """Get the current branch name"""
        success, output = GitHelper.run_command(["git", "branch", "--show-current"])
        return output if success else None

    @staticmethod
    def get_all_branches(include_remote: bool = False) -> List[BranchInfo]:
        """Get all branches with their info"""
        cmd = ["git", "branch", "-a"] if include_remote else ["git", "branch"]
        success, output = GitHelper.run_command(cmd)

        if not success:
            return []

        branches = []
        current_branch = GitHelper.get_current_branch()
        merged_branches = GitHelper.get_merged_branches()

        for line in output.split("\n"):
            if not line.strip():
                continue

            is_current = line.startswith("*")
            name = line.strip().lstrip("* ")

            if name.startswith("remotes/"):
                name = name[8:]  # Remove 'remotes/' prefix

            branches.append(
                BranchInfo(
                    name=name, is_current=is_current, is_merged=name in merged_branches
                )
            )

        return branches

    @staticmethod
    def get_merged_branches() -> List[str]:
        """Get list of merged branches"""
        success, output = GitHelper.run_command(["git", "branch", "--merged"])
        if not success:
            return []

        branches = []
        for line in output.split("\n"):
            branch = line.strip().lstrip("* ")
            if branch and branch not in ["main", "master", "develop"]:
                branches.append(branch)

        return branches

    @staticmethod
    def delete_branch(branch: str, force: bool = False) -> Tuple[bool, str]:
        """Delete a branch"""
        flag = "-D" if force else "-d"
        return GitHelper.run_command(["git", "branch", flag, branch])

    @staticmethod
    def get_commits(limit: int = 50) -> List[CommitInfo]:
        """Get recent commits"""
        format_str = "%H|%h|%an|%ae|%aI|%s"
        success, output = GitHelper.run_command(
            ["git", "log", f"-{limit}", f"--format={format_str}"]
        )

        if not success:
            return []

        commits = []
        for line in output.split("\n"):
            if not line.strip():
                continue

            parts = line.split("|", 5)
            if len(parts) >= 6:
                commits.append(
                    CommitInfo(
                        hash=parts[0],
                        short_hash=parts[1],
                        author=parts[2],
                        email=parts[3],
                        date=datetime.fromisoformat(parts[4]),
                        message=parts[5],
                    )
                )

        return commits

    @staticmethod
    def get_last_commit() -> Optional[CommitInfo]:
        """Get the last commit"""
        commits = GitHelper.get_commits(1)
        return commits[0] if commits else None

    @staticmethod
    def get_contributors() -> Dict[str, Dict]:
        """Get contributors with their statistics"""
        success, output = GitHelper.run_command(["git", "shortlog", "-sne", "HEAD"])

        if not success:
            return {}

        contributors = {}
        for line in output.split("\n"):
            if not line.strip():
                continue

            parts = line.strip().split("\t")
            if len(parts) >= 2:
                count = int(parts[0].strip())
                author_info = parts[1]

                # Extract email if present
                if "<" in author_info and ">" in author_info:
                    name = author_info[: author_info.index("<")].strip()
                    email = author_info[
                        author_info.index("<") + 1 : author_info.index(">")
                    ]
                else:
                    name = author_info
                    email = ""

                contributors[name] = {"commits": count, "email": email}

        return contributors

    @staticmethod
    def get_file_stats() -> Dict[str, int]:
        """Get file statistics"""
        success, output = GitHelper.run_command(["git", "ls-files"])

        if not success:
            return {}

        files = output.split("\n")
        stats = {}

        for file in files:
            if not file:
                continue
            ext = os.path.splitext(file)[1] or "no extension"
            stats[ext] = stats.get(ext, 0) + 1

        return stats

    @staticmethod
    def get_repo_stats() -> Dict:
        """Get comprehensive repository statistics"""
        stats = {
            "total_commits": 0,
            "total_contributors": 0,
            "total_files": 0,
            "total_branches": 0,
            "first_commit_date": None,
            "last_commit_date": None,
        }

        # Total commits
        success, output = GitHelper.run_command(["git", "rev-list", "--count", "HEAD"])
        if success:
            stats["total_commits"] = int(output)

        # Contributors
        contributors = GitHelper.get_contributors()
        stats["total_contributors"] = len(contributors)

        # Files
        success, output = GitHelper.run_command(["git", "ls-files"])
        if success:
            stats["total_files"] = len([f for f in output.split("\n") if f])

        # Branches
        branches = GitHelper.get_all_branches()
        stats["total_branches"] = len(branches)

        # First and last commit dates
        commits = GitHelper.get_commits(1)
        if commits:
            stats["last_commit_date"] = commits[0].date

        success, output = GitHelper.run_command(
            ["git", "log", "--reverse", "--format=%aI", "-1"]
        )
        if success and output:
            stats["first_commit_date"] = datetime.fromisoformat(output.strip())

        return stats

    @staticmethod
    def get_blame_stats() -> Dict[str, int]:
        """Get line count per author across all files"""
        success, files_output = GitHelper.run_command(["git", "ls-files"])

        if not success:
            return {}

        author_lines = {}
        files = [f for f in files_output.split("\n") if f]

        for file in files[:100]:  # Limit to first 100 files for performance
            success, blame_output = GitHelper.run_command(
                ["git", "blame", "--line-porcelain", file]
            )

            if success:
                for line in blame_output.split("\n"):
                    if line.startswith("author "):
                        author = line[7:]
                        author_lines[author] = author_lines.get(author, 0) + 1

        return author_lines

    @staticmethod
    def stage_all() -> Tuple[bool, str]:
        """Stage all changes"""
        return GitHelper.run_command(["git", "add", "-A"])

    @staticmethod
    def unstage_all() -> Tuple[bool, str]:
        """Unstage all changes"""
        return GitHelper.run_command(["git", "reset", "HEAD"])

    @staticmethod
    def stash(message: Optional[str] = None) -> Tuple[bool, str]:
        """Stash changes"""
        cmd = ["git", "stash"]
        if message:
            cmd.extend(["push", "-m", message])
        return GitHelper.run_command(cmd)

    @staticmethod
    def stash_pop() -> Tuple[bool, str]:
        """Pop stashed changes"""
        return GitHelper.run_command(["git", "stash", "pop"])

    @staticmethod
    def stash_list() -> List[str]:
        """List all stashes"""
        success, output = GitHelper.run_command(["git", "stash", "list"])
        if success and output:
            return output.split("\n")
        return []

    @staticmethod
    def reset_soft(ref: str = "HEAD~1") -> Tuple[bool, str]:
        """Soft reset to a reference"""
        return GitHelper.run_command(["git", "reset", "--soft", ref])

    @staticmethod
    def reset_hard(ref: str = "HEAD~1") -> Tuple[bool, str]:
        """Hard reset to a reference"""
        return GitHelper.run_command(["git", "reset", "--hard", ref])

    @staticmethod
    def reset_mixed(ref: str = "HEAD~1") -> Tuple[bool, str]:
        """Mixed reset to a reference"""
        return GitHelper.run_command(["git", "reset", "--mixed", ref])

    @staticmethod
    def revert_commit(commit_hash: str) -> Tuple[bool, str]:
        """Revert a specific commit"""
        return GitHelper.run_command(["git", "revert", "--no-commit", commit_hash])

    @staticmethod
    def get_status() -> Dict:
        """Get detailed git status"""
        status = {"staged": [], "modified": [], "untracked": [], "deleted": []}

        success, output = GitHelper.run_command(["git", "status", "--porcelain"])

        if not success:
            return status

        for line in output.split("\n"):
            if not line:
                continue

            code = line[:2]
            file = line[3:]

            if code[0] in ["A", "M", "D", "R"]:
                status["staged"].append(file)
            if code[1] == "M":
                status["modified"].append(file)
            if code == "??":
                status["untracked"].append(file)
            if code[1] == "D":
                status["deleted"].append(file)

        return status

    @staticmethod
    def get_diff_stats() -> Tuple[int, int]:
        """Get insertions and deletions for staged changes"""
        success, output = GitHelper.run_command(
            ["git", "diff", "--cached", "--numstat"]
        )

        insertions = 0
        deletions = 0

        if success:
            for line in output.split("\n"):
                if line:
                    parts = line.split("\t")
                    if len(parts) >= 2:
                        try:
                            insertions += int(parts[0]) if parts[0] != "-" else 0
                            deletions += int(parts[1]) if parts[1] != "-" else 0
                        except ValueError:
                            pass

        return insertions, deletions
