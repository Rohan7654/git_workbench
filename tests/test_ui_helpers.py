import pytest
from git_workbench.utils.ui_helpers import UIHelper
from rich.table import Table
from rich.tree import Tree

def test_create_table():
    title = "Test Table"
    columns = ["Col1", "Col2"]
    rows = [["1", "2"], ["3", "4"]]
    table = UIHelper.create_table(title, columns, rows)
    
    assert isinstance(table, Table)
    assert table.title == title
    assert len(table.columns) == 2
    assert table.row_count == 2

def test_create_tree():
    title = "Test Tree"
    items = {"Key1": "Value1", "Key2": {"SubKey": "SubValue"}}
    tree = UIHelper.create_tree(title, items)
    
    assert isinstance(tree, Tree)
    assert str(tree.label) == f"[bold cyan]{title}[/bold cyan]"
