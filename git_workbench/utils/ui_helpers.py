from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.tree import Tree
from rich.text import Text
from rich.style import Style
from rich import box
from rich.align import Align
from typing import List, Dict, Optional, Any
import time


console = Console()


class UIHelper:
    """Helper class for Rich UI components"""

    @staticmethod
    def print_banner():
        """Print the Git Workbench banner"""
        banner = r"""  
         _____ _ _    __          __        _    _                     _     
        / ____(_) |   \ \        / /       | |  | |                   | |    
       | |  __ _| |_   \ \  /\  / /__  _ __| | _| |__   ___ _ __   ___| |__  
       | | |_ | | __|   \ \/  \/ / _ \| '__| |/ / '_ \ / _ \ '_ \ / __| '_ \ 
       | |__| | | |_     \  /\  / (_) | |  |   <| |_) |  __/ | | | (__| | | |
        \_____|_|\__|     \/  \/ \___/|_|  |_|\_\_.__/ \___|_| |_|\___|_| |_|
        """
        console.print(f"[bold green]{banner}[/bold green]", justify="center")

    @staticmethod
    def print_header(title: str, subtitle: str = ""):
        """Print a styled header"""
        content = Align.center(subtitle) if subtitle else ""

        console.print(
            Panel(
                content,
                title=f"[bold cyan] {title} [/bold cyan]",
                title_align="center",
                style="white",
                border_style="cyan",
                box=box.ROUNDED,
                padding=(1, 2),
                expand=False,
            )
        )

    @staticmethod
    def print_success(message: str):
        """Print a success message"""
        console.print(f"[green]Success:[/green] {message}")

    @staticmethod
    def print_error(message: str):
        """Print an error message"""
        console.print(f"[red]Error:[/red] {message}")

    @staticmethod
    def print_warning(message: str):
        """Print a warning message"""
        console.print(f"[yellow]Warning:[/yellow] {message}")

    @staticmethod
    def print_info(message: str):
        """Print an info message"""
        console.print(f"[blue]Info:[/blue] {message}")

    @staticmethod
    def print_command_info(command: str, description: str, example: str = ""):
        """Print command information with explanation"""
        panel_content = Text()
        panel_content.append("Command: ", style="bold")
        panel_content.append(f"{command}\n\n", style="cyan")
        panel_content.append("What it does:\n", style="bold")
        panel_content.append(f"{description}\n", style="white")

        if example:
            panel_content.append("\nExample:\n", style="bold")
            panel_content.append(example, style="dim")

        console.print(Panel(panel_content, border_style="blue", expand=False))

    @staticmethod
    def create_table(
        title: str, columns: List[str], rows: List[List[Any]], show_header: bool = True
    ) -> Table:
        """Create a styled table"""
        table = Table(title=title, show_header=show_header, box=box.ROUNDED)

        colors = ["cyan", "green", "yellow", "magenta", "blue"]
        for i, col in enumerate(columns):
            table.add_column(col, style=colors[i % len(colors)])

        for row in rows:
            table.add_row(*[str(cell) for cell in row])

        return table

    @staticmethod
    def create_tree(title: str, items: Dict) -> Tree:
        """Create a tree structure"""
        tree = Tree(f"[bold cyan]{title}[/bold cyan]")

        def add_items(parent, data):
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, dict):
                        branch = parent.add(f"[yellow]{key}[/yellow]")
                        add_items(branch, value)
                    else:
                        parent.add(f"[green]{key}[/green]: {value}")
            elif isinstance(data, list):
                for item in data:
                    parent.add(str(item))

        add_items(tree, items)
        return tree

    @staticmethod
    def with_spinner(message: str):
        """Context manager for showing a spinner"""
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        )

    @staticmethod
    def confirm(message: str, default: bool = False) -> bool:
        """Show a confirmation prompt"""
        import inquirer

        questions = [
            inquirer.Confirm("confirm", message=message, default=default),
        ]
        answers = inquirer.prompt(questions)
        return answers.get("confirm", False) if answers else False

    @staticmethod
    def select(message: str, choices: List[tuple]) -> Optional[str]:
        """Show a selection prompt"""
        import inquirer

        questions = [
            inquirer.List("selection", message=message, choices=choices),
        ]
        answers = inquirer.prompt(questions)
        return answers.get("selection") if answers else None

    @staticmethod
    def multi_select(message: str, choices: List[tuple]) -> List[str]:
        """Show a multi-selection prompt"""
        import inquirer

        questions = [
            inquirer.Checkbox("selections", message=message, choices=choices),
        ]
        answers = inquirer.prompt(questions)
        return answers.get("selections", []) if answers else []

    @staticmethod
    def text_input(message: str, default: str = "") -> Optional[str]:
        """Show a text input prompt"""
        import inquirer

        questions = [
            inquirer.Text("input", message=message, default=default),
        ]
        answers = inquirer.prompt(questions)
        return answers.get("input") if answers else None

    @staticmethod
    def print_git_status(status: Dict):
        """Print formatted git status"""
        if not any(status.values()):
            console.print("[green]✓ Working tree clean[/green]")
            return

        if status["staged"]:
            console.print("\n[green]Staged changes:[/green]")
            for file in status["staged"]:
                console.print(f"  [green]+ {file}[/green]")

        if status["modified"]:
            console.print("\n[yellow]Modified files:[/yellow]")
            for file in status["modified"]:
                console.print(f"  [yellow]~ {file}[/yellow]")

        if status["untracked"]:
            console.print("\n[red]Untracked files:[/red]")
            for file in status["untracked"]:
                console.print(f"  [red]? {file}[/red]")

        if status["deleted"]:
            console.print("\n[red]Deleted files:[/red]")
            for file in status["deleted"]:
                console.print(f"  [red]- {file}[/red]")
