import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from git_workbench.utils.git_helpers import GitHelper
from git_workbench.utils.ui_helpers import UIHelper

console = Console()


UNDO_OPTIONS = [
    (
        "Last commit (keep changes staged)",
        "soft_reset",
        "Undoes the last commit but keeps all changes staged. Use this when you want to modify the commit message or add more changes.",
    ),
    (
        "Last commit (keep changes unstaged)",
        "mixed_reset",
        "Undoes the last commit and unstages the changes. Files remain modified in your working directory.",
    ),
    (
        "Last commit (discard all changes)",
        "hard_reset",
        "DANGEROUS: Completely removes the last commit AND all changes. Cannot be recovered!",
    ),
    (
        "Last merge",
        "undo_merge",
        "Undoes the last merge commit. Useful when a merge introduced problems.",
    ),
    (
        "Staged files (unstage all)",
        "unstage_all",
        "Removes all files from the staging area. Files remain modified in your working directory.",
    ),
    (
        "Staged file (unstage specific)",
        "unstage_file",
        "Removes a specific file from the staging area.",
    ),
    (
        "All uncommitted changes",
        "discard_all",
        "DANGEROUS: Discards ALL uncommitted changes in tracked files. Cannot be recovered!",
    ),
    (
        "Changes in specific file",
        "discard_file",
        "Discards changes in a specific file. Cannot be recovered!",
    ),
    (
        "Revert a specific commit",
        "revert_commit",
        "Creates a new commit that undoes changes from a previous commit. Safe for shared branches.",
    ),
    (
        "Recover stashed changes",
        "stash_pop",
        "Applies the most recent stash and removes it from the stash list.",
    ),
    ("Cancel", "cancel", ""),
]


@click.command()
def undo():
    """Easily undo git operations with interactive prompts"""

    if not GitHelper.is_git_repo():
        UIHelper.print_error("Not a git repository")
        return

    UIHelper.print_header("Git Undo", "Safely undo git operations with guidance")

    # Show current status
    status = GitHelper.get_status()
    last_commit = GitHelper.get_last_commit()

    console.print("\n[bold]Current State:[/bold]")
    if last_commit:
        console.print(
            f"  Last commit: [cyan]{last_commit.short_hash}[/cyan] - {last_commit.message[:50]}"
        )

    staged_count = len(status["staged"])
    modified_count = len(status["modified"])
    untracked_count = len(status["untracked"])

    console.print(
        f"  Staged: [green]{staged_count}[/green] | Modified: [yellow]{modified_count}[/yellow] | Untracked: [red]{untracked_count}[/red]"
    )

    console.print("\n[bold yellow]What do you want to undo?[/bold yellow]\n")

    # Display options with descriptions
    choices = [(f"{opt[0]}", opt[1]) for opt in UNDO_OPTIONS]

    selected = UIHelper.select("Select an operation", choices)

    if selected == "cancel" or selected is None:
        return

    # Get the description for the selected option
    description = next((opt[2] for opt in UNDO_OPTIONS if opt[1] == selected), "")

    if description:
        console.print(
            Panel(description, title="[bold]What this does[/bold]", border_style="blue")
        )

    # Execute the selected operation
    if selected == "soft_reset":
        undo_last_commit_soft()
    elif selected == "mixed_reset":
        undo_last_commit_mixed()
    elif selected == "hard_reset":
        undo_last_commit_hard()
    elif selected == "undo_merge":
        undo_last_merge()
    elif selected == "unstage_all":
        unstage_all_files()
    elif selected == "unstage_file":
        unstage_specific_file()
    elif selected == "discard_all":
        discard_all_changes()
    elif selected == "discard_file":
        discard_file_changes()
    elif selected == "revert_commit":
        revert_specific_commit()
    elif selected == "stash_pop":
        recover_stash()


def undo_last_commit_soft():
    """Undo last commit, keep changes staged"""
    last_commit = GitHelper.get_last_commit()
    if not last_commit:
        UIHelper.print_error("No commits to undo")
        return

    console.print(
        f"\n[bold]Will undo:[/bold] {last_commit.short_hash} - {last_commit.message}"
    )

    if UIHelper.confirm("Proceed with soft reset?"):
        success, output = GitHelper.reset_soft("HEAD~1")
        if success:
            UIHelper.print_success("Commit undone! Changes are still staged.")
            console.print("[dim]You can now modify and recommit.[/dim]")
        else:
            UIHelper.print_error(f"Failed: {output}")


def undo_last_commit_mixed():
    """Undo last commit, keep changes unstaged"""
    last_commit = GitHelper.get_last_commit()
    if not last_commit:
        UIHelper.print_error("No commits to undo")
        return

    console.print(
        f"\n[bold]Will undo:[/bold] {last_commit.short_hash} - {last_commit.message}"
    )

    if UIHelper.confirm("Proceed with mixed reset?"):
        success, output = GitHelper.reset_mixed("HEAD~1")
        if success:
            UIHelper.print_success("Commit undone! Changes are unstaged but preserved.")
            console.print("[dim]Use 'git add' to re-stage changes.[/dim]")
        else:
            UIHelper.print_error(f"Failed: {output}")


def undo_last_commit_hard():
    """Undo last commit and discard all changes"""
    last_commit = GitHelper.get_last_commit()
    if not last_commit:
        UIHelper.print_error("No commits to undo")
        return

    console.print(f"\n[bold red]WARNING: This will permanently delete:[/bold red]")
    console.print(f"  Commit: {last_commit.short_hash} - {last_commit.message}")
    console.print(f"  All changes in that commit")

    if UIHelper.confirm("Are you SURE? This cannot be undone!", default=False):
        if UIHelper.confirm("Really sure? Type 'yes' to confirm", default=False):
            success, output = GitHelper.reset_hard("HEAD~1")
            if success:
                UIHelper.print_success("Commit and changes permanently removed!")
            else:
                UIHelper.print_error(f"Failed: {output}")


def undo_last_merge():
    """Undo the last merge"""
    console.print("\n[bold]Undoing last merge...[/bold]")

    if UIHelper.confirm("This will undo the last merge. Proceed?"):
        success, output = GitHelper.run_command(["git", "merge", "--abort"])
        if not success:
            # Try resetting to before merge
            success, output = GitHelper.run_command(
                ["git", "reset", "--merge", "ORIG_HEAD"]
            )

        if success:
            UIHelper.print_success("Merge undone!")
        else:
            UIHelper.print_error(f"Failed: {output}")


def unstage_all_files():
    """Unstage all staged files"""
    status = GitHelper.get_status()

    if not status["staged"]:
        UIHelper.print_info("No staged files to unstage")
        return

    console.print(f"\n[bold]Will unstage {len(status['staged'])} file(s):[/bold]")
    for f in status["staged"][:10]:
        console.print(f"  - {f}")
    if len(status["staged"]) > 10:
        console.print(f"  ... and {len(status['staged']) - 10} more")

    if UIHelper.confirm("Proceed?"):
        success, output = GitHelper.unstage_all()
        if success:
            UIHelper.print_success("All files unstaged!")
        else:
            UIHelper.print_error(f"Failed: {output}")


def unstage_specific_file():
    """Unstage a specific file"""
    status = GitHelper.get_status()

    if not status["staged"]:
        UIHelper.print_info("No staged files to unstage")
        return

    selected = UIHelper.multi_select(
        "Select files to unstage", [(f, f) for f in status["staged"]]
    )

    if not selected:
        return

    for file in selected:
        success, output = GitHelper.run_command(["git", "reset", "HEAD", file])
        if success:
            UIHelper.print_success(f"Unstaged: {file}")
        else:
            UIHelper.print_error(f"Failed to unstage {file}: {output}")


def discard_all_changes():
    """Discard all uncommitted changes"""
    status = GitHelper.get_status()

    changed = status["modified"] + status["deleted"]
    if not changed:
        UIHelper.print_info("No changes to discard")
        return

    console.print(
        f"\n[bold red]⚠️  WARNING: Will permanently discard changes in {len(changed)} file(s)[/bold red]"
    )

    if UIHelper.confirm("Are you SURE? This cannot be undone!", default=False):
        success, output = GitHelper.run_command(["git", "checkout", "--", "."])
        if success:
            UIHelper.print_success("All changes discarded!")
        else:
            UIHelper.print_error(f"Failed: {output}")


def discard_file_changes():
    """Discard changes in specific files"""
    status = GitHelper.get_status()

    changed = status["modified"]
    if not changed:
        UIHelper.print_info("No modified files to discard")
        return

    selected = UIHelper.multi_select(
        "Select files to discard changes", [(f, f) for f in changed]
    )

    if not selected:
        return

    console.print(f"\n[bold red]⚠️  This will permanently discard changes![/bold red]")

    if UIHelper.confirm("Proceed?", default=False):
        for file in selected:
            success, output = GitHelper.run_command(["git", "checkout", "--", file])
            if success:
                UIHelper.print_success(f"Discarded changes: {file}")
            else:
                UIHelper.print_error(f"Failed for {file}: {output}")


def revert_specific_commit():
    """Revert a specific commit"""
    commits = GitHelper.get_commits(20)

    if not commits:
        UIHelper.print_error("No commits found")
        return

    choices = [
        (f"{c.short_hash} - {c.message[:50]} ({c.author})", c.hash) for c in commits
    ]

    selected = UIHelper.select("Select commit to revert", choices)

    if not selected:
        return

    commit = next((c for c in commits if c.hash == selected), None)

    console.print(f"\n[bold]Will create a revert commit for:[/bold]")
    console.print(f"  {commit.short_hash} - {commit.message}")
    console.print(
        "\n[dim]This is safe for shared branches as it creates a new commit.[/dim]"
    )

    if UIHelper.confirm("Proceed?"):
        success, output = GitHelper.revert_commit(selected)
        if success:
            UIHelper.print_success("Revert commit created!")
            console.print("[dim]Don't forget to commit the revert.[/dim]")
        else:
            UIHelper.print_error(f"Failed: {output}")


def recover_stash():
    """Recover stashed changes"""
    stashes = GitHelper.stash_list()

    if not stashes:
        UIHelper.print_info("No stashes found")
        return

    choices = [(s, i) for i, s in enumerate(stashes)]

    selected = UIHelper.select("Select stash to recover", choices)

    if selected is None:
        return

    if UIHelper.confirm(f"Apply and remove stash@{{{selected}}}?"):
        success, output = GitHelper.run_command(
            ["git", "stash", "pop", f"stash@{{{selected}}}"]
        )
        if success:
            UIHelper.print_success("Stash applied and removed!")
        else:
            UIHelper.print_error(f"Failed: {output}")
