import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from git_workbench.commands import (
    basics,
    gitclean,
    gitstat,
    gitundo,
    prmaker,
    gitwho,
    commitlint,
)

console = Console()

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


class BannerGroup(click.Group):
    def format_help(self, ctx, formatter):
        from git_workbench.utils.ui_helpers import UIHelper
        from rich.table import Table
        from rich import box

        UIHelper.print_banner()

        UIHelper.print_header(
            "Git Workbench Help", "A professional Git & GitHub workspace"
        )

        console.print("\n[bold cyan]Available Commands:[/bold cyan]")

        table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
        table.add_column("Command", style="cyan", width=15)
        table.add_column("Description", style="white")

        # Get all subcommands and their help messages
        for name in sorted(self.list_commands(ctx)):
            cmd = self.get_command(ctx, name)
            if cmd:
                # Extract first line of docstring for summary
                help_text = (
                    cmd.help.split("\n")[0] if cmd.help else "No description"
                )
                table.add_row(name, help_text)

        console.print(table)

        console.print("\n[bold yellow]Usage:[/bold yellow]")
        console.print("  gw [cyan][COMMAND][/cyan] [args...]")
        console.print("  gw [cyan]--help[/cyan] / [cyan]-h[/cyan]")
        console.print(
            "\nRun '[cyan]gw COMMAND --help[/cyan]' for more information on a specific command.\n"
        )


@click.group(
    cls=BannerGroup, invoke_without_command=True, context_settings=CONTEXT_SETTINGS
)
@click.version_option(version="1.0.0", prog_name="Git Workbench")
@click.pass_context
def cli(ctx):
    """Git Workbench - A comprehensive Git & GitHub workspace

    A collection of powerful tools to enhance your Git workflow.
    """

    # Banner is handled by BannerGroup for help.
    # We do NOT print it for subcommands anymore based on user feedback.

    if ctx.invoked_subcommand is None:
        ctx.invoke(menu)


# Register all command groups
cli.add_command(basics.basics, name="basics")
cli.add_command(gitclean.clean, name="clean")
cli.add_command(gitstat.stats, name="stats")
cli.add_command(gitundo.undo, name="undo")
cli.add_command(prmaker.create_pr, name="pr")
cli.add_command(gitwho.who, name="who")
cli.add_command(commitlint.lint, name="lint")


@cli.command()
def menu():
    """Interactive menu to access all tools"""
    import inquirer

    # Banner is handled by cli() now for subcommands
    from git_workbench.utils.ui_helpers import UIHelper

    UIHelper.print_header("Git Workbench Suite", "Select a tool to get started")

    choices = [
        ("Git Basics - Learn & execute basic git commands", "basics"),
        ("Git Clean - Remove merged branches, clean up repos", "clean"),
        ("Git Stats - Beautiful git statistics for a repo", "stats"),
        ("Git Undo - Easily undo git operations", "undo"),
        ("PR Maker - Generate PR descriptions from commits", "pr"),
        ("Git Who - Show who contributed what % of code", "who"),
        ("Commit Lint - Enforce conventional commit messages", "lint"),
        ("Exit", "exit"),
    ]

    questions = [
        inquirer.List(
            "tool",
            message="Select a tool",
            choices=choices,
        ),
    ]

    answers = inquirer.prompt(questions)

    if answers and answers["tool"] != "exit":
        # Get the command object from the CLI group
        ctx = click.get_current_context()
        cmd = cli.get_command(ctx, answers["tool"])

        if cmd:
            # properly invoke the command
            ctx.invoke(cmd)


if __name__ == "__main__":
    cli()
