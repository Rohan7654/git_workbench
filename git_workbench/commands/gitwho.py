import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

from git_workbench.utils.git_helpers import GitHelper
from git_workbench.utils.ui_helpers import UIHelper

console = Console()


@click.command()
@click.option("--detailed", "-d", is_flag=True, help="Show detailed per-file breakdown")
@click.option("--limit", "-l", default=20, help="Limit number of contributors shown")
def who(detailed, limit):
    """Show who contributed what percentage of code"""

    if not GitHelper.is_git_repo():
        UIHelper.print_error("Not a git repository")
        return

    UIHelper.print_header("Git Who", "Analyze code contributions by author")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Analyzing contributions...", total=None)

        # Get contributor stats
        contributors = GitHelper.get_contributors()

        if not contributors:
            UIHelper.print_error("No contributors found")
            return

        # Calculate total commits
        total_commits = sum(c["commits"] for c in contributors.values())

        # Get line-based stats (this is more accurate but slower)
        blame_stats = {}
        if detailed:
            progress.add_task(description="Analyzing code ownership...", total=None)
            blame_stats = GitHelper.get_blame_stats()

    # Sort by commits
    sorted_contributors = sorted(
        contributors.items(), key=lambda x: x[1]["commits"], reverse=True
    )[:limit]

    # Display commit-based contributions
    console.print("\n[bold]Contributions by Commits[/bold]\n")

    table = Table(box=box.ROUNDED, show_lines=False)
    table.add_column("Rank", style="yellow", width=6, justify="center")
    table.add_column("Author", style="cyan", width=30)
    table.add_column("Commits", style="green", width=10, justify="right")
    table.add_column("Percentage", style="magenta", width=12, justify="right")
    table.add_column("Contribution", width=35)

    for i, (name, data) in enumerate(sorted_contributors, 1):
        percentage = (data["commits"] / total_commits) * 100
        bar_length = int(percentage / 3)
        bar = "█" * bar_length + "░" * (33 - bar_length)

        # Determine rank emoji
        rank_emoji = ""
        if i == 1:
            rank_emoji = "1st"
        elif i == 2:
            rank_emoji = "2nd"
        elif i == 3:
            rank_emoji = "3rd"

        table.add_row(
            f"{rank_emoji}" if rank_emoji else str(i),
            name[:30],
            str(data["commits"]),
            f"{percentage:.1f}%",
            f"[green]{bar}[/green]",
        )

    console.print(table)
    console.print(
        f"\n[dim]Total commits: {total_commits} | Total contributors: {len(contributors)}[/dim]"
    )

    # Display line-based contributions if detailed
    if detailed and blame_stats:
        total_lines = sum(blame_stats.values())

        console.print("\n[bold]Contributions by Lines of Code[/bold]\n")

        sorted_blame = sorted(blame_stats.items(), key=lambda x: x[1], reverse=True)[
            :limit
        ]

        lines_table = Table(box=box.ROUNDED, show_lines=False)
        lines_table.add_column("Author", style="cyan", width=30)
        lines_table.add_column("Lines", style="green", width=10, justify="right")
        lines_table.add_column("Percentage", style="magenta", width=12, justify="right")
        lines_table.add_column("Ownership", width=35)

        for name, lines in sorted_blame:
            percentage = (lines / total_lines) * 100
            bar_length = int(percentage / 3)
            bar = "█" * bar_length + "░" * (33 - bar_length)

            lines_table.add_row(
                name[:30], str(lines), f"{percentage:.1f}%", f"[blue]{bar}[/blue]"
            )

        console.print(lines_table)
        console.print(f"\n[dim]Total lines analyzed: {total_lines}[/dim]")

    # Show recent activity
    console.print("\n[bold]Recent Activity[/bold]\n")

    commits = GitHelper.get_commits(30)

    # Group by author
    recent_activity = {}
    for commit in commits:
        author = commit.author
        if author not in recent_activity:
            recent_activity[author] = {
                "count": 0,
                "last_commit": commit.date,
                "last_message": commit.message,
            }
        recent_activity[author]["count"] += 1

    sorted_recent = sorted(
        recent_activity.items(), key=lambda x: x[1]["last_commit"], reverse=True
    )[:5]

    for author, data in sorted_recent:
        days_ago = (commits[0].date - data["last_commit"]).days if commits else 0
        time_str = "today" if days_ago == 0 else f"{days_ago} days ago"
        console.print(
            f"  [cyan]{author}[/cyan]: {data['count']} commits in last 30 days "
            f"[dim](last: {time_str})[/dim]"
        )
