import click
import re
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from git_workbench.utils.git_helpers import GitHelper
from git_workbench.utils.ui_helpers import UIHelper

console = Console()


# Conventional commit types
COMMIT_TYPES = {
    "feat": "A new feature",
    "fix": "A bug fix",
    "docs": "Documentation only changes",
    "style": "Changes that do not affect the meaning of the code",
    "refactor": "A code change that neither fixes a bug nor adds a feature",
    "perf": "A code change that improves performance",
    "test": "Adding missing tests or correcting existing tests",
    "build": "Changes that affect the build system or external dependencies",
    "ci": "Changes to CI configuration files and scripts",
    "chore": "Other changes that don't modify src or test files",
    "revert": "Reverts a previous commit",
}

# Conventional commit pattern
CONVENTIONAL_PATTERN = re.compile(
    r"^(?P<type>" + "|".join(COMMIT_TYPES.keys()) + r")"
    r"(?:\((?P<scope>[a-zA-Z0-9_-]+)\))?"
    r"(?P<breaking>!)?"
    r": (?P<description>.+)$"
)


@click.command()
@click.option("--check", "-c", default=10, help="Number of commits to check")
@click.option(
    "--fix", "-f", is_flag=True, help="Interactive mode to create valid commits"
)
@click.option(
    "--strict", "-s", is_flag=True, help="Enforce strict conventional commits"
)
def lint(check, fix, strict):
    """Enforce and validate conventional commit messages"""

    if not GitHelper.is_git_repo():
        UIHelper.print_error("Not a git repository")
        return

    UIHelper.print_header("Commit Lint", "Validate conventional commit messages")

    if fix:
        interactive_commit()
        return

    # Show conventional commit format
    show_format_help()

    # Get recent commits
    commits = GitHelper.get_commits(check)

    if not commits:
        UIHelper.print_warning("No commits found")
        return

    console.print(f"\n[bold]Checking last {len(commits)} commits...[/bold]\n")

    valid_count = 0
    invalid_count = 0

    results_table = Table(box=box.ROUNDED)
    results_table.add_column("Status", width=8, justify="center")
    results_table.add_column("Hash", style="yellow", width=8)
    results_table.add_column("Type", style="cyan", width=10)
    results_table.add_column("Message", width=50)
    results_table.add_column("Issue", style="red", width=25)

    for commit in commits:
        result = validate_commit(commit.message, strict)

        if result["valid"]:
            valid_count += 1
            status = "[green]✓[/green]"
            issue = ""
        else:
            invalid_count += 1
            status = "[red]✗[/red]"
            issue = result["error"]

        results_table.add_row(
            status,
            commit.short_hash,
            result.get("type", "-"),
            commit.message[:50] + ("..." if len(commit.message) > 50 else ""),
            issue[:25] if issue else "",
        )

    console.print(results_table)

    # Summary
    console.print("\n[bold]Summary:[/bold]")
    console.print(f"  [green]Valid:[/green] {valid_count}")
    console.print(f"  [red]Invalid:[/red] {invalid_count}")

    percentage = (valid_count / len(commits)) * 100

    if percentage == 100:
        console.print(
            f"\n[bold green]Perfect! All commits follow conventional format.[/bold green]"
        )
    elif percentage >= 80:
        console.print(
            f"\n[bold yellow]Good! {percentage:.0f}% of commits are valid.[/bold yellow]"
        )
    else:
        console.print(
            f"\n[bold red]Needs improvement. Only {percentage:.0f}% of commits are valid.[/bold red]"
        )

    # Offer to create a valid commit
    if UIHelper.confirm("\nWould you like to create a new conventional commit?"):
        interactive_commit()


def validate_commit(message: str, strict: bool = False) -> dict:
    """Validate a commit message against conventional commits format"""
    result = {
        "valid": False,
        "type": None,
        "scope": None,
        "breaking": False,
        "description": None,
        "error": None,
    }

    # Check if empty
    if not message or not message.strip():
        result["error"] = "Empty message"
        return result

    # Get first line
    first_line = message.split("\n")[0].strip()

    # Check length
    if len(first_line) > 72:
        result["error"] = "Too long (max 72 chars)"
        if strict:
            return result

    # Match against pattern
    match = CONVENTIONAL_PATTERN.match(first_line)

    if not match:
        # Check for common issues
        if ":" not in first_line:
            result["error"] = "Missing type prefix"
        elif first_line[0].isupper():
            result["error"] = "Type should be lowercase"
        else:
            result["error"] = "Invalid format"
        return result

    result["type"] = match.group("type")
    result["scope"] = match.group("scope")
    result["breaking"] = bool(match.group("breaking"))
    result["description"] = match.group("description")

    # Additional strict checks
    if strict:
        desc = result["description"]

        if desc[0].isupper():
            result["error"] = "Description should start lowercase"
            return result

        if desc.endswith("."):
            result["error"] = "No period at end"
            return result

        if len(desc) < 10:
            result["error"] = "Description too short"
            return result

    result["valid"] = True
    return result


def show_format_help():
    """Display conventional commit format help"""
    format_panel = """[bold]Conventional Commit Format:[/bold]

[cyan]<type>[/cyan]([yellow]<scope>[/yellow]): [white]<description>[/white]

[blank line]
[body]

[blank line]
[footer]

[bold]Examples:[/bold]
  [cyan]feat[/cyan]: add user authentication
  [cyan]fix[/cyan]([yellow]api[/yellow]): resolve null pointer exception
  [cyan]docs[/cyan]: update README with new examples
  [cyan]feat[/cyan]!: drop support for Python 2
"""
    console.print(
        Panel(format_panel, title="Conventional Commits", border_style="blue")
    )

    # Show types
    console.print("\n[bold]Available Types:[/bold]")

    type_table = Table(box=box.SIMPLE, show_header=False)
    type_table.add_column("Type", style="cyan", width=12)
    type_table.add_column("Description", width=50)

    for type_name, description in COMMIT_TYPES.items():
        type_table.add_row(type_name, description)

    console.print(type_table)


def interactive_commit():
    """Interactive mode to create a valid conventional commit"""
    console.print("\n[bold]Create a Conventional Commit[/bold]\n")

    # Select type
    type_choices = [(f"{t} - {d}", t) for t, d in COMMIT_TYPES.items()]
    commit_type = UIHelper.select("Select commit type", type_choices)

    if not commit_type:
        return

    # Optional scope
    scope = UIHelper.text_input("Scope (optional, e.g., api, ui, auth)")

    # Breaking change?
    breaking = UIHelper.confirm("Is this a breaking change?", default=False)

    # Description
    description = UIHelper.text_input("Short description (imperative mood)")

    if not description:
        UIHelper.print_error("Description is required")
        return

    # Ensure lowercase start
    description = description[0].lower() + description[1:] if description else ""

    # Remove trailing period
    description = description.rstrip(".")

    # Optional body
    body = ""
    if UIHelper.confirm("Add a longer description?", default=False):
        body = UIHelper.text_input("Longer description")

    # Optional footer
    footer = ""
    if UIHelper.confirm("Add footer (e.g., Closes #123)?", default=False):
        footer = UIHelper.text_input("Footer")

    # Build commit message
    if scope:
        commit_msg = f"{commit_type}({scope})"
    else:
        commit_msg = commit_type

    if breaking:
        commit_msg += "!"

    commit_msg += f": {description}"

    if body:
        commit_msg += f"\n\n{body}"

    if footer:
        commit_msg += f"\n\n{footer}"

    # Preview
    console.print("\n[bold]Commit Message Preview:[/bold]")
    console.print(Panel(commit_msg, border_style="green"))

    # Validate
    result = validate_commit(commit_msg, strict=True)

    if result["valid"]:
        UIHelper.print_success("Message is valid!")
    else:
        UIHelper.print_warning(f"Warning: {result['error']}")

    # Check if there are staged changes
    status = GitHelper.get_status()

    if not status["staged"]:
        UIHelper.print_warning("No staged changes")
        if status["modified"] or status["untracked"]:
            if UIHelper.confirm("Stage all changes?"):
                GitHelper.stage_all()
            else:
                return
        else:
            UIHelper.print_error("Nothing to commit")
            return

    # Commit
    if UIHelper.confirm("Create this commit?"):
        success, output = GitHelper.run_command(["git", "commit", "-m", commit_msg])
        if success:
            UIHelper.print_success("Commit created successfully!")
            console.print(f"[dim]{output}[/dim]")
        else:
            UIHelper.print_error(f"Commit failed: {output}")
