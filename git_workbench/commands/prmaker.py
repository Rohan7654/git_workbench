import click
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
import pyperclip

from git_workbench.utils.git_helpers import GitHelper
from git_workbench.utils.ui_helpers import UIHelper
from git_workbench.templates.pr_templates import PRTemplates

console = Console()


@click.command()
@click.option(
    "--template",
    "-t",
    type=click.Choice(PRTemplates.list_templates()),
    required=False,
    help="PR template to use",
)
@click.option("--commits", "-c", default=10, help="Number of recent commits to include")
@click.option("--copy", is_flag=True, help="Copy to clipboard")
def create_pr(template, commits, copy):
    """Generate PR descriptions from commits using templates"""

    if not GitHelper.is_git_repo():
        UIHelper.print_error("Not a git repository")
        return

    UIHelper.print_header(
        "PR Description Generator", "Create beautiful PR descriptions from commits"
    )

    # Get recent commits
    recent_commits = GitHelper.get_commits(commits)

    if not recent_commits:
        UIHelper.print_error("No commits found")
        return

    # Show commits
    console.print("\n[bold]Recent Commits:[/bold]")
    for c in recent_commits[:5]:
        console.print(f"  [yellow]{c.short_hash}[/yellow] {c.message[:60]}")
    if len(recent_commits) > 5:
        console.print(f"  [dim]... and {len(recent_commits) - 5} more[/dim]")

    # Select template if not provided
    if template is None:
        template_choices = [
            (f"{t.capitalize()} - {get_template_description(t)}", t)
            for t in PRTemplates.list_templates()
        ]
        console.print()  # Add spacing
        template = UIHelper.select("Select a template", template_choices)

        if template is None:  # User cancelled or something
            template = "standard"

    console.print(f"\n[bold]Template:[/bold] [cyan]{template}[/cyan]")

    # Gather information
    console.print("\n[bold]Let's create your PR description![/bold]\n")

    description = UIHelper.text_input(
        "PR Description (what does this PR do?)",
        default=recent_commits[0].message if recent_commits else "",
    )

    # Generate changes list from commits
    changes_list = "\n".join([f"- {c.message}" for c in recent_commits[:10]])

    if UIHelper.confirm("Would you like to edit the changes list?", default=False):
        console.print("\n[dim]Current changes (from commits):[/dim]")
        console.print(changes_list)
        custom_changes = UIHelper.text_input(
            "Enter custom changes (or press Enter to keep)"
        )
        if custom_changes:
            changes_list = custom_changes

    # Template-specific inputs
    template_data = {
        "description": description,
        "changes": changes_list,
        "change_type": "",
        "issues": "",
        "notes": "",
        "reason": "",
        "problem": "",
        "solution": "",
        "root_cause": "",
        "issue_number": "",
        "test_steps": "",
        "breaking_changes": "None",
        "issue": "",
        "fix": "",
        "impact": "",
        "rollback": "",
        "verification": "",
        "performance": "No significant impact",
        "breaking_description": "",
        "sections": "",
    }

    if template == "standard":
        change_types = [
            ("Bug fix", "- [x] Bug fix"),
            ("New feature", "- [x] New feature"),
            ("Breaking change", "- [x] Breaking change"),
            ("Documentation", "- [x] Documentation update"),
            ("Style/Refactor", "- [x] Code style/refactoring"),
            ("Tests", "- [x] Test updates"),
        ]
        selected_type = UIHelper.select("Type of change", change_types)
        template_data["change_type"] = selected_type or "- [ ] Bug fix"

        template_data["issues"] = (
            UIHelper.text_input(
                "Related issue numbers (e.g., #123, #456)", default="N/A"
            )
            or "N/A"
        )
        template_data["notes"] = (
            UIHelper.text_input("Additional notes (optional)", default="None") or "None"
        )

    elif template == "feature":
        template_data["test_steps"] = (
            UIHelper.text_input(
                "How to test this feature?", default="Run the application and verify"
            )
            or ""
        )
        template_data["breaking_changes"] = (
            UIHelper.text_input("Any breaking changes?", default="None") or "None"
        )
        template_data["issue_number"] = (
            UIHelper.text_input("Related issue number", default="N/A") or "N/A"
        )

    elif template == "bugfix":
        template_data["problem"] = (
            UIHelper.text_input("What was the problem?") or description
        )
        template_data["solution"] = (
            UIHelper.text_input("How did you fix it?") or "See changes"
        )
        template_data["root_cause"] = (
            UIHelper.text_input(
                "What was the root cause?", default="Investigated and fixed"
            )
            or ""
        )
        template_data["issue_number"] = (
            UIHelper.text_input("Issue number this fixes", default="N/A") or "N/A"
        )

    elif template == "hotfix":
        template_data["issue"] = (
            UIHelper.text_input("What is the critical issue?") or description
        )
        template_data["fix"] = (
            UIHelper.text_input("What fix was applied?") or "See changes"
        )
        template_data["impact"] = (
            UIHelper.text_input(
                "What is the impact?", default="Resolves critical issue"
            )
            or ""
        )
        template_data["rollback"] = (
            UIHelper.text_input("Rollback plan?", default="Revert this commit") or ""
        )
        template_data["verification"] = (
            UIHelper.text_input(
                "How to verify the fix?", default="Test the affected functionality"
            )
            or ""
        )

    elif template == "refactor":
        template_data["reason"] = (
            UIHelper.text_input("Why was this refactoring needed?")
            or "Code improvement"
        )
        template_data["performance"] = (
            UIHelper.text_input("Performance impact?", default="No significant impact")
            or ""
        )
        template_data["breaking_description"] = (
            UIHelper.text_input("Breaking changes description (if any)", default="")
            or ""
        )

    elif template == "docs":
        template_data["sections"] = (
            UIHelper.text_input("Which sections were updated?") or "See changes"
        )
        template_data["reason"] = (
            UIHelper.text_input(
                "Why was this update needed?", default="Documentation improvement"
            )
            or ""
        )

    elif template == "minimal":
        template_data["reason"] = (
            UIHelper.text_input("Why are these changes needed?") or "Improvement"
        )

    # Generate PR description
    pr_template = PRTemplates.get_template(template)

    try:
        pr_description = pr_template.format(**template_data)
    except KeyError as e:
        # Handle missing keys by providing defaults
        pr_description = pr_template
        for key in template_data:
            pr_description = pr_description.replace(
                "{" + key + "}", template_data.get(key, "")
            )

    # Display the generated PR
    console.print("\n" + "=" * 60)
    console.print("[bold green]Generated PR Description:[/bold green]")
    console.print("=" * 60 + "\n")

    syntax = Syntax(pr_description, "markdown", theme="monokai", line_numbers=False)
    console.print(Panel(syntax, border_style="green"))

    # Copy to clipboard
    if copy:
        try:
            pyperclip.copy(pr_description)
            UIHelper.print_success("PR description copied to clipboard!")
        except Exception:
            UIHelper.print_warning("Could not copy to clipboard. Please copy manually.")
    else:
        if UIHelper.confirm("Copy to clipboard?"):
            try:
                pyperclip.copy(pr_description)
                UIHelper.print_success("PR description copied to clipboard!")
            except Exception:
                UIHelper.print_warning(
                    "Could not copy to clipboard. Please copy manually."
                )

    # Option to save to file
    if UIHelper.confirm("Save to file?", default=False):
        filename = UIHelper.text_input("Filename", default="PR_DESCRIPTION.md")
        try:
            with open(filename, "w") as f:
                f.write(pr_description)
            UIHelper.print_success(f"Saved to {filename}")
        except Exception as e:
            UIHelper.print_error(f"Could not save file: {e}")


def get_template_description(template_type: str) -> str:
    """Get a short description for each template type"""
    descriptions = {
        "standard": "Comprehensive template with checklist",
        "minimal": "Simple and concise format",
        "feature": "For new feature PRs",
        "bugfix": "For bug fix PRs",
        "hotfix": "For critical/urgent fixes",
        "refactor": "For code refactoring",
        "docs": "For documentation updates",
    }
    return descriptions.get(template_type, "PR template")
