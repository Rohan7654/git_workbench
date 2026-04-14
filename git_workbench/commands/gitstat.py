import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn
from rich import box
from datetime import datetime

from git_workbench.utils.git_helpers import GitHelper
from git_workbench.utils.ui_helpers import UIHelper

console = Console()


@click.command()
@click.option("--detailed", "-d", is_flag=True, help="Show detailed statistics")
def stats(detailed):
    """Display beautiful git statistics for the repository"""

    if not GitHelper.is_git_repo():
        UIHelper.print_error("Not a git repository")
        return

    UIHelper.print_header("Git Statistics", "Comprehensive repository analysis")

    with console.status("[bold green]Analyzing repository..."):
        repo_stats = GitHelper.get_repo_stats()
        contributors = GitHelper.get_contributors()
        file_stats = GitHelper.get_file_stats()

    # Overview Panel
    overview = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    overview.add_column("Metric", style="cyan")
    overview.add_column("Value", style="white")

    overview.add_row("Total Commits", str(repo_stats["total_commits"]))
    overview.add_row("Contributors", str(repo_stats["total_contributors"]))
    overview.add_row("Total Files", str(repo_stats["total_files"]))
    overview.add_row("Branches", str(repo_stats["total_branches"]))

    if repo_stats["first_commit_date"]:
        age = (
            datetime.now() - repo_stats["first_commit_date"].replace(tzinfo=None)
        ).days
        overview.add_row("Repository Age", f"{age} days")
        overview.add_row(
            "First Commit", repo_stats["first_commit_date"].strftime("%Y-%m-%d")
        )

    if repo_stats["last_commit_date"]:
        overview.add_row(
            "Last Commit", repo_stats["last_commit_date"].strftime("%Y-%m-%d %H:%M")
        )

    console.print(
        Panel(overview, title="[bold]Repository Overview[/bold]", border_style="cyan")
    )

    # Contributors Table
    if contributors:
        console.print("\n[bold]Top Contributors[/bold]\n")

        total_commits = sum(c["commits"] for c in contributors.values())
        sorted_contributors = sorted(
            contributors.items(), key=lambda x: x[1]["commits"], reverse=True
        )

        contrib_table = Table(box=box.ROUNDED)
        contrib_table.add_column("Rank", style="yellow", width=6)
        contrib_table.add_column("Author", style="cyan", width=25)
        contrib_table.add_column("Commits", style="green", width=10)
        contrib_table.add_column("Percentage", style="magenta", width=15)
        contrib_table.add_column("Bar", width=30)

        for i, (name, data) in enumerate(sorted_contributors[:10], 1):
            percentage = (data["commits"] / total_commits) * 100
            bar_length = int(percentage / 5)
            bar = "█" * bar_length + "░" * (20 - bar_length)

            contrib_table.add_row(
                f"#{i}",
                name[:25],
                str(data["commits"]),
                f"{percentage:.1f}%",
                f"[green]{bar}[/green]",
            )

        console.print(contrib_table)

    # File Types
    if file_stats:
        console.print("\n[bold]File Types[/bold]\n")

        sorted_types = sorted(file_stats.items(), key=lambda x: x[1], reverse=True)
        total_files = sum(file_stats.values())

        type_table = Table(box=box.ROUNDED)
        type_table.add_column("Extension", style="cyan", width=15)
        type_table.add_column("Count", style="green", width=10)
        type_table.add_column("Percentage", style="magenta", width=15)

        for ext, count in sorted_types[:15]:
            percentage = (count / total_files) * 100
            type_table.add_row(ext or "(no ext)", str(count), f"{percentage:.1f}%")

        console.print(type_table)

    # Recent Activity
    if detailed:
        console.print("\n[bold]Recent Activity[/bold]\n")

        commits = GitHelper.get_commits(30)

        # Group commits by date
        activity = {}
        for commit in commits:
            date = commit.date.strftime("%Y-%m-%d")
            activity[date] = activity.get(date, 0) + 1

        if activity:
            activity_table = Table(box=box.SIMPLE)
            activity_table.add_column("Date", style="cyan")
            activity_table.add_column("Commits", style="green")
            activity_table.add_column("Activity", width=40)

            max_commits = max(activity.values())
            for date, count in sorted(activity.items(), reverse=True)[:10]:
                bar_length = int((count / max_commits) * 30)
                bar = "█" * bar_length
                activity_table.add_row(date, str(count), f"[green]{bar}[/green]")

            console.print(activity_table)

    # Branches
    branches = GitHelper.get_all_branches()
    merged_count = sum(1 for b in branches if b.is_merged)

    console.print(f"\n[bold]🌿 Branch Summary[/bold]")
    console.print(f"  Total: {len(branches)}")
    console.print(f"  Merged: {merged_count}")
    console.print(f"  Active: {len(branches) - merged_count}")
