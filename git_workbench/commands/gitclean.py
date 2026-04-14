import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from git_workbench.utils.git_helpers import GitHelper
from git_workbench.utils.ui_helpers import UIHelper

console = Console()


@click.command()
@click.option(
    "--dry-run", "-n", is_flag=True, help="Show what would be deleted without deleting"
)
@click.option("--force", "-f", is_flag=True, help="Force delete branches")
@click.option(
    "--remote", "-r", is_flag=True, help="Also clean remote tracking branches"
)
def clean(dry_run, force, remote):
    """Remove merged branches and clean up the repository"""

    if not GitHelper.is_git_repo():
        UIHelper.print_error("Not a git repository")
        return

    UIHelper.print_header("Git Clean", "Remove merged branches and clean up the repo")

    # Show current state
    current_branch = GitHelper.get_current_branch()
    console.print(f"\n[bold]Current branch:[/bold] [cyan]{current_branch}[/cyan]")

    # Get merged branches
    merged_branches = GitHelper.get_merged_branches()

    # Filter out protected branches
    protected = ["main", "master", "develop", "development", current_branch]
    deletable = [b for b in merged_branches if b not in protected]

    if not deletable:
        UIHelper.print_success("No merged branches to clean up!")
        console.print(
            "[dim]Protected branches (main, master, develop) are never deleted.[/dim]"
        )
        return

    # Show branches to delete
    console.print(
        f"\n[bold]Found {len(deletable)} merged branch(es) that can be deleted:[/bold]\n"
    )

    table = Table(box=box.ROUNDED)
    table.add_column("Branch", style="yellow")
    table.add_column("Status", style="green")

    for branch in deletable:
        table.add_row(branch, "merged ✓")

    console.print(table)

    if dry_run:
        console.print("\n[yellow]Dry run mode - no branches were deleted[/yellow]")
        return

    # Confirm deletion
    selected = UIHelper.multi_select(
        "Select branches to delete", [(b, b) for b in deletable]
    )

    if not selected:
        UIHelper.print_info("No branches selected for deletion")
        return

    # Delete selected branches
    console.print()
    deleted = 0
    failed = 0

    for branch in selected:
        success, output = GitHelper.delete_branch(branch, force=force)
        if success:
            UIHelper.print_success(f"Deleted: {branch}")
            deleted += 1
        else:
            UIHelper.print_error(f"Failed to delete {branch}: {output}")
            failed += 1

    # Summary
    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"  [green]Deleted:[/green] {deleted}")
    if failed:
        console.print(f"  [red]Failed:[/red] {failed}")

    # Clean up remote tracking branches
    if remote:
        console.print("\n[bold]Cleaning remote tracking branches...[/bold]")
        success, output = GitHelper.run_command(["git", "remote", "prune", "origin"])
        if success:
            UIHelper.print_success("Remote tracking branches cleaned")
        else:
            UIHelper.print_error(f"Failed: {output}")

    # Run git gc
    if UIHelper.confirm("Run git gc to optimize the repository?"):
        success, output = GitHelper.run_command(["git", "gc", "--prune=now"])
        if success:
            UIHelper.print_success("Repository optimized")
        else:
            UIHelper.print_error(f"Optimization failed: {output}")
