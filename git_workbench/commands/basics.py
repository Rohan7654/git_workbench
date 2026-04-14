import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
import inquirer

from git_workbench.utils.git_helpers import GitHelper
from git_workbench.utils.ui_helpers import UIHelper

console = Console()


# Command definitions with explanations
GIT_COMMANDS = {
    "init": {
        "command": "git init",
        "description": "Initializes a new Git repository in the current directory. Creates a hidden .git folder that tracks all changes.",
        "example": "$ git init\nInitialized empty Git repository in /path/to/repo/.git/",
        "category": "setup",
    },
    "clone": {
        "command": "git clone <url>",
        "description": "Creates a copy of a remote repository on your local machine. Downloads all files, branches, and commit history.",
        "example": "$ git clone https://github.com/user/repo.git\nCloning into 'repo'...",
        "category": "setup",
    },
    "status": {
        "command": "git status",
        "description": "Shows the current state of your working directory. Displays which files are staged, modified, or untracked.",
        "example": "$ git status\nOn branch main\nChanges not staged for commit:\n  modified: file.txt",
        "category": "info",
    },
    "add": {
        "command": "git add <file>",
        "description": "Stages changes for the next commit. Adds file contents to the staging area (index).",
        "example": "$ git add file.txt      # Add specific file\n$ git add .             # Add all files\n$ git add -A            # Add all including deletions",
        "category": "staging",
    },
    "commit": {
        "command": 'git commit -m "message"',
        "description": "Records staged changes to the repository with a descriptive message. Creates a new commit in the history.",
        "example": '$ git commit -m "Add new feature"\n[main abc1234] Add new feature\n 1 file changed, 10 insertions(+)',
        "category": "staging",
    },
    "push": {
        "command": "git push",
        "description": "Uploads local commits to a remote repository. Syncs your local branch with the remote.",
        "example": "$ git push origin main\nCounting objects: 3, done.\nWriting objects: 100%",
        "category": "remote",
    },
    "pull": {
        "command": "git pull",
        "description": "Downloads and integrates changes from a remote repository. Combines 'git fetch' and 'git merge'.",
        "example": "$ git pull origin main\nUpdating abc1234..def5678\nFast-forward\n file.txt | 2 ++",
        "category": "remote",
    },
    "fetch": {
        "command": "git fetch",
        "description": "Downloads objects and refs from a remote repository WITHOUT merging. Lets you review changes before integrating.",
        "example": "$ git fetch origin\nremote: Counting objects: 3, done.\n * [new branch] feature -> origin/feature",
        "category": "remote",
    },
    "branch": {
        "command": "git branch",
        "description": "Lists, creates, or deletes branches. Branches are independent lines of development.",
        "example": "$ git branch              # List branches\n$ git branch feature      # Create branch\n$ git branch -d feature   # Delete branch",
        "category": "branching",
    },
    "checkout": {
        "command": "git checkout <branch>",
        "description": "Switches branches or restores working tree files. Updates files in the working directory to match the version stored in that branch.",
        "example": "$ git checkout feature\nSwitched to branch 'feature'\n$ git checkout -b new-feature  # Create and switch",
        "category": "branching",
    },
    "switch": {
        "command": "git switch <branch>",
        "description": "Modern way to switch branches (Git 2.23+). Clearer alternative to 'git checkout' for branch switching.",
        "example": "$ git switch feature\nSwitched to branch 'feature'\n$ git switch -c new-feature  # Create and switch",
        "category": "branching",
    },
    "merge": {
        "command": "git merge <branch>",
        "description": "Combines changes from one branch into another. Integrates the history of the specified branch into the current branch.",
        "example": "$ git merge feature\nUpdating abc1234..def5678\nFast-forward\n file.txt | 5 +++++",
        "category": "branching",
    },
    "rebase": {
        "command": "git rebase <branch>",
        "description": "Reapplies commits on top of another base. Creates a linear history by moving your branch's commits to the tip of the target branch.",
        "example": "$ git rebase main\nFirst, rewinding head to replay your work on top of it...\nApplying: Your commit message",
        "category": "branching",
    },
    "stash": {
        "command": "git stash",
        "description": "Temporarily stores modified files in a stack. Saves your local modifications away and reverts the working directory to match HEAD.",
        "example": "$ git stash                    # Stash changes\n$ git stash list               # List stashes\n$ git stash pop                # Apply and remove\n$ git stash apply              # Apply and keep",
        "category": "staging",
    },
    "log": {
        "command": "git log",
        "description": "Shows the commit history. Displays commits with their hash, author, date, and message.",
        "example": "$ git log --oneline            # Compact view\n$ git log --graph              # Visual branch graph\n$ git log -5                   # Last 5 commits",
        "category": "info",
    },
    "diff": {
        "command": "git diff",
        "description": "Shows differences between commits, branches, or files. Displays what has changed in your working directory.",
        "example": "$ git diff                     # Unstaged changes\n$ git diff --staged            # Staged changes\n$ git diff branch1 branch2     # Between branches",
        "category": "info",
    },
    "reset": {
        "command": "git reset",
        "description": "Undoes changes by moving the current branch tip. Can unstage files or undo commits depending on the mode.",
        "example": "$ git reset HEAD file.txt      # Unstage file\n$ git reset --soft HEAD~1      # Undo commit, keep changes\n$ git reset --hard HEAD~1      # Undo commit, discard changes",
        "category": "undo",
    },
    "revert": {
        "command": "git revert <commit>",
        "description": "Creates a new commit that undoes changes from a previous commit. Safe way to undo changes without rewriting history.",
        "example": '$ git revert abc1234\n[main def5678] Revert "Previous commit message"',
        "category": "undo",
    },
    "cherry-pick": {
        "command": "git cherry-pick <commit>",
        "description": "Applies changes from a specific commit to the current branch. Useful for selectively moving commits between branches.",
        "example": "$ git cherry-pick abc1234\n[main def5678] Cherry-picked commit message",
        "category": "advanced",
    },
    "tag": {
        "command": "git tag",
        "description": "Creates, lists, or deletes tags. Tags mark specific points in history, typically used for releases.",
        "example": '$ git tag v1.0.0               # Lightweight tag\n$ git tag -a v1.0.0 -m "msg"   # Annotated tag\n$ git push origin v1.0.0       # Push tag',
        "category": "setup",
    },
    "remote": {
        "command": "git remote",
        "description": "Manages remote repository connections. Add, remove, or view remote repositories.",
        "example": "$ git remote -v                        # List remotes\n$ git remote add origin <url>          # Add remote\n$ git remote remove origin             # Remove remote",
        "category": "remote",
    },
    "config": {
        "command": "git config",
        "description": "Gets and sets repository or global options. Configure user name, email, editor, and other settings.",
        "example": '$ git config --global user.name "Your Name"\n$ git config --global user.email "you@example.com"\n$ git config --list',
        "category": "setup",
    },
}


@click.group(invoke_without_command=True)
@click.pass_context
def basics(ctx):
    """Git Basics - Learn and execute basic git commands with explanations"""
    if ctx.invoked_subcommand is None:
        ctx.invoke(learn)


@basics.command()
def learn():
    """Interactive learning mode for git commands"""
    if not GitHelper.is_git_repo():
        UIHelper.print_warning(
            "Not in a git repository. Some commands won't work here."
        )

    UIHelper.print_header("Git Basics", "Learn and execute basic git commands")

    categories = {
        "Setup & Config": "setup",
        "Information": "info",
        "Staging & Commits": "staging",
        "Branching & Merging": "branching",
        "Remote Operations": "remote",
        "Undo Operations": "undo",
        "Advanced": "advanced",
        "Show All Commands": "all",
        "Exit": "exit",
    }

    while True:
        console.print()
        category_choice = UIHelper.select(
            "Select a category to explore", list(categories.items())
        )

        if category_choice == "exit" or category_choice is None:
            break

        if category_choice == "all":
            show_all_commands()
            continue

        # Filter commands by category
        filtered_commands = {
            k: v for k, v in GIT_COMMANDS.items() if v["category"] == category_choice
        }

        if not filtered_commands:
            UIHelper.print_warning("No commands in this category")
            continue

        command_choices = [
            (f"{v['command']} - {v['description'][:50]}...", k)
            for k, v in filtered_commands.items()
        ]
        command_choices.append(("Back", "back"))

        while True:
            cmd_choice = UIHelper.select("Select a command to learn", command_choices)

            if cmd_choice == "back" or cmd_choice is None:
                break

            cmd_info = GIT_COMMANDS[cmd_choice]
            UIHelper.print_command_info(
                cmd_info["command"], cmd_info["description"], cmd_info["example"]
            )

            # Offer to run the command if applicable
            if cmd_choice in ["status", "log", "branch", "remote", "stash", "diff"]:
                if UIHelper.confirm("Would you like to run this command now?"):
                    run_basic_command(cmd_choice)


def show_all_commands():
    """Display all commands in a table"""
    table = Table(title="Git Commands Reference", box=box.ROUNDED, show_lines=True)
    table.add_column("Command", style="cyan", width=25)
    table.add_column("Description", style="white", width=60)
    table.add_column("Category", style="yellow", width=12)

    for cmd, info in GIT_COMMANDS.items():
        table.add_row(
            info["command"],
            (
                info["description"][:60] + "..."
                if len(info["description"]) > 60
                else info["description"]
            ),
            info["category"],
        )

    console.print(table)


def run_basic_command(cmd: str):
    """Run a basic git command and show output"""
    command_map = {
        "status": ["git", "status"],
        "log": ["git", "log", "--oneline", "-10"],
        "branch": ["git", "branch", "-a"],
        "remote": ["git", "remote", "-v"],
        "stash": ["git", "stash", "list"],
        "diff": ["git", "diff", "--stat"],
    }

    if cmd in command_map:
        success, output = GitHelper.run_command(command_map[cmd])
        if success:
            console.print(
                Panel(output or "[dim]No output[/dim]", title=f"Output: {cmd}")
            )
        else:
            UIHelper.print_error(f"Command failed: {output}")


@basics.command()
def status():
    """Show current git status with explanation"""
    if not GitHelper.is_git_repo():
        UIHelper.print_error("Not a git repository")
        return

    UIHelper.print_header("📋 Git Status", "Current state of your working directory")

    status = GitHelper.get_status()
    UIHelper.print_git_status(status)

    # Show current branch
    branch = GitHelper.get_current_branch()
    if branch:
        console.print(f"\n[bold]Current branch:[/bold] [cyan]{branch}[/cyan]")


@basics.command()
@click.option("--all", "-a", is_flag=True, help="Stage all changes")
@click.argument("files", nargs=-1)
def add(all, files):
    """Stage files for commit"""
    if not GitHelper.is_git_repo():
        UIHelper.print_error("Not a git repository")
        return

    UIHelper.print_command_info(
        "git add",
        "Stages changes for the next commit. Adds file contents to the staging area.",
        "git add file.txt    # Stage specific file\ngit add .           # Stage all files",
    )

    if all or not files:
        if UIHelper.confirm("Stage all changes?"):
            success, output = GitHelper.stage_all()
            if success:
                UIHelper.print_success("All changes staged")
            else:
                UIHelper.print_error(f"Failed: {output}")
    else:
        for file in files:
            success, output = GitHelper.run_command(["git", "add", file])
            if success:
                UIHelper.print_success(f"Staged: {file}")
            else:
                UIHelper.print_error(f"Failed to stage {file}: {output}")


@basics.command()
@click.option("--message", "-m", help="Commit message")
def commit(message):
    """Commit staged changes"""
    if not GitHelper.is_git_repo():
        UIHelper.print_error("Not a git repository")
        return

    UIHelper.print_command_info(
        "git commit",
        "Records staged changes to the repository. Creates a new commit with your message.",
        'git commit -m "Add new feature"',
    )

    # Check if there are staged changes
    status = GitHelper.get_status()
    if not status["staged"]:
        UIHelper.print_warning("No staged changes to commit")
        if UIHelper.confirm("Would you like to stage all changes first?"):
            GitHelper.stage_all()
        else:
            return

    if not message:
        message = UIHelper.text_input("Enter commit message")

    if not message:
        UIHelper.print_error("Commit message is required")
        return

    success, output = GitHelper.run_command(["git", "commit", "-m", message])
    if success:
        UIHelper.print_success(f"Committed: {message}")
        console.print(f"[dim]{output}[/dim]")
    else:
        UIHelper.print_error(f"Commit failed: {output}")


@basics.command()
def stash():
    """Stash your changes with interactive options"""
    if not GitHelper.is_git_repo():
        UIHelper.print_error("Not a git repository")
        return

    UIHelper.print_command_info(
        "git stash",
        "Temporarily stores your modified files in a stack. Saves your local modifications and reverts the working directory to match HEAD. Useful when you need to switch branches but aren't ready to commit.",
        "git stash           # Stash changes\ngit stash pop       # Apply and remove latest stash\ngit stash list      # Show all stashes",
    )

    choices = [
        ("📥 Stash current changes", "push"),
        ("📤 Pop latest stash (apply and remove)", "pop"),
        ("📋 Apply latest stash (keep in stash)", "apply"),
        ("📝 List all stashes", "list"),
        ("🗑️ Drop latest stash", "drop"),
        ("🧹 Clear all stashes", "clear"),
        ("⬅️ Back", "back"),
    ]

    choice = UIHelper.select("What would you like to do?", choices)

    if choice == "back" or choice is None:
        return

    if choice == "push":
        message = UIHelper.text_input("Enter stash message (optional)")
        success, output = GitHelper.stash(message)
        if success:
            UIHelper.print_success("Changes stashed successfully")
        else:
            UIHelper.print_error(f"Failed: {output}")

    elif choice == "pop":
        success, output = GitHelper.stash_pop()
        if success:
            UIHelper.print_success("Stash applied and removed")
        else:
            UIHelper.print_error(f"Failed: {output}")

    elif choice == "apply":
        success, output = GitHelper.run_command(["git", "stash", "apply"])
        if success:
            UIHelper.print_success("Stash applied (still in stash list)")
        else:
            UIHelper.print_error(f"Failed: {output}")

    elif choice == "list":
        stashes = GitHelper.stash_list()
        if stashes:
            console.print("\n[bold]Stash List:[/bold]")
            for stash in stashes:
                console.print(f"  {stash}")
        else:
            UIHelper.print_info("No stashes found")

    elif choice == "drop":
        if UIHelper.confirm("Drop the latest stash?"):
            success, output = GitHelper.run_command(["git", "stash", "drop"])
            if success:
                UIHelper.print_success("Latest stash dropped")
            else:
                UIHelper.print_error(f"Failed: {output}")

    elif choice == "clear":
        if UIHelper.confirm("Clear ALL stashes? This cannot be undone!"):
            success, output = GitHelper.run_command(["git", "stash", "clear"])
            if success:
                UIHelper.print_success("All stashes cleared")
            else:
                UIHelper.print_error(f"Failed: {output}")


@basics.command()
def log():
    """Show commit history with visual options"""
    if not GitHelper.is_git_repo():
        UIHelper.print_error("Not a git repository")
        return

    UIHelper.print_command_info(
        "git log",
        "Shows the commit history of the repository. Displays commits with their hash, author, date, and message.",
        "git log --oneline   # Compact view\ngit log --graph     # Visual branch graph",
    )

    commits = GitHelper.get_commits(15)

    if not commits:
        UIHelper.print_warning("No commits found")
        return

    table = Table(title="Recent Commits", box=box.ROUNDED)
    table.add_column("Hash", style="yellow", width=8)
    table.add_column("Author", style="cyan", width=20)
    table.add_column("Date", style="green", width=12)
    table.add_column("Message", style="white", width=50)

    for commit in commits:
        table.add_row(
            commit.short_hash,
            commit.author[:20],
            commit.date.strftime("%Y-%m-%d"),
            commit.message[:50] + "..." if len(commit.message) > 50 else commit.message,
        )

    console.print(table)


@basics.command()
def branches():
    """List and manage branches"""
    if not GitHelper.is_git_repo():
        UIHelper.print_error("Not a git repository")
        return

    UIHelper.print_command_info(
        "git branch",
        "Lists, creates, or deletes branches. Branches are independent lines of development allowing you to work on features without affecting the main codebase.",
        "git branch              # List branches\ngit branch feature      # Create new branch\ngit checkout feature    # Switch to branch",
    )

    branches = GitHelper.get_all_branches(include_remote=True)
    current = GitHelper.get_current_branch()

    console.print(f"\n[bold]Current branch:[/bold] [cyan]{current}[/cyan]\n")

    local_branches = [b for b in branches if not b.name.startswith("origin/")]
    remote_branches = [b for b in branches if b.name.startswith("origin/")]

    if local_branches:
        console.print("[bold]Local branches:[/bold]")
        for branch in local_branches:
            marker = "→ " if branch.is_current else "  "
            merged = " [dim](merged)[/dim]" if branch.is_merged else ""
            console.print(f"  {marker}[cyan]{branch.name}[/cyan]{merged}")

    if remote_branches:
        console.print("\n[bold]Remote branches:[/bold]")
        for branch in remote_branches[:10]:  # Limit to 10
            console.print(f"  [dim]{branch.name}[/dim]")
        if len(remote_branches) > 10:
            console.print(f"  [dim]... and {len(remote_branches) - 10} more[/dim]")


@basics.command()
def quick():
    """Quick reference card for common commands"""
    UIHelper.print_header("⚡ Git Quick Reference", "Most commonly used commands")

    sections = {
        "Starting": [
            ("git init", "Create new repository"),
            ("git clone <url>", "Clone a repository"),
        ],
        "Daily Workflow": [
            ("git status", "Check current state"),
            ("git add .", "Stage all changes"),
            ('git commit -m "msg"', "Commit changes"),
            ("git push", "Push to remote"),
            ("git pull", "Pull from remote"),
        ],
        "Branching": [
            ("git branch <name>", "Create branch"),
            ("git checkout <name>", "Switch branch"),
            ("git merge <branch>", "Merge branch"),
        ],
        "Undo": [
            ("git reset HEAD <file>", "Unstage file"),
            ("git checkout -- <file>", "Discard changes"),
            ("git revert <commit>", "Revert commit"),
        ],
        "Stashing": [
            ("git stash", "Stash changes"),
            ("git stash pop", "Apply stash"),
            ("git stash list", "List stashes"),
        ],
    }

    for section, commands in sections.items():
        console.print(f"\n[bold yellow]{section}[/bold yellow]")
        for cmd, desc in commands:
            console.print(f"  [cyan]{cmd:<30}[/cyan] {desc}")
