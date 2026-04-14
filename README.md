# Git Workbench

[![PyPI version](https://img.shields.io/pypi/v/git-workbench.svg)](https://pypi.org/project/git-workbench/)
[![Python versions](https://img.shields.io/pypi/pyversions/git-workbench.svg)](https://pypi.org/project/git-workbench/)
[![Downloads](https://static.pepy.tech/badge/git-workbench)](https://pepy.tech/project/git-workbench)
[![Downloads per month](https://static.pepy.tech/badge/git-workbench/month)](https://pepy.tech/project/git-workbench)

Git Workbench is a powerful, professional CLI suite designed to enhance your Git and GitHub workflow. It provides a set of interactive tools to simplify common tasks, enforce conventions, and visualize repository data.

## Features

Git Workbench includes a comprehensive suite of tools:

*   **Git Basics**: Interactive guide to learn and execute core Git commands.
*   **Git Clean**: safely remove merged branches and keep your repository tidy.
*   **Git Stats**: Visualize repository statistics, including contributor activity and file breakdowns.
*   **Git Undo**: Interactive menu to safely undo recent Git operations (commits, merges, stages).
*   **PR Maker**: Generate professional Pull Request descriptions from your commit history using templates.
*   **Git Who**: Analyze code contributions by author with percentage breakdowns.
*   **Commit Lint**: Enforce and validate Conventional Commit messages.

## Installation

### Prerequisites
- Python 3.8 or higher
- Git installed and available in your PATH

### local Installation
Clone the repository and install in editable mode:

```bash
git clone https://github.com/Rohan7654/git_workbench.git
cd git_workbench
pip install -e .
```

## Usage

Once installed, you can use the `gw` command (or `git_workbench`) to access the suite.

### Main Menu
Launch the interactive main menu:
```bash
gw
```

### Direct Commands
You can also run specific tools directly:

```bash
# Clean up merged branches
gw clean

# View repository statistics
gw stats

# Interactive undo menu
gw undo

# Generate a PR description
gw pr

# Analyze contributors
gw who

# Validate commit messages
gw lint
```

## Interactive Demos

See what Git Workbench looks like in action.

### 1. Main Menu
Running `gw` launches the central hub:

```text
╭──────  Git Workbench Suite  ──────╮
│                                   │
│   Select a tool to get started    │
│                                   │
╰───────────────────────────────────╯
  Git Basics    Learn & execute basic git commands
  Git Clean     Remove merged branches, clean up repos
  Git Stats     Beautiful git statistics for a repo
  Git Undo      Easily undo git operations
  PR Maker      Generate PR descriptions from commits
  Git Who       Show who contributed what % of code
  Commit Lint   Enforce conventional commit messages
  Exit
```

### 2. Git Stats
`gw stats` gives you a comprehensive overview:

```text
╭──────────────── Git Statistics ─────────────────╮
│                                                 │
│        Comprehensive repository analysis        │
│                                                 │
╰─────────────────────────────────────────────────╯
Analyzing repository... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100%

╭────────────── Repository Overview ──────────────╮
│ Metric                Value                     │
│ ─────────────────────────────────────────────── │
│ Total Commits         1,243                     │
│ Contributors          12                        │
│ Total Files           89                        │
│ Branches              5                         │
│ Repository Age        245 days                  │
╰─────────────────────────────────────────────────╯
```

### 3. Git Undo
`gw undo` helps you recover from mistakes safely:

```text
╭────────────────── Git Undo ──────────────────╮
│                                              │
│    Safely undo git operations with guidance  │
│                                              │
╰──────────────────────────────────────────────╯

Current State:
  Last commit: a1b2c3d - Fix login bug
  Staged: 2 | Modified: 1 | Untracked: 0

[?] What do you want to undo?
 > Last commit (keep changes staged)
   Last commit (keep changes unstaged)
   Last commit (discard all changes)
   Last merge
   Staged files (unstage all)
```

### 4. PR Maker
`gw pr` generates descriptions from your work:

```text
╭────────── PR Description Generator ──────────╮
│                                              │
│ Create beautiful PR descriptions from commits│
│                                              │
╰──────────────────────────────────────────────╯

Recent Commits:
  a1b2c3d Fix login bug
  e4f5g6h Update documentation

[?] Select a template:
 > Standard - Comprehensive template with checklist
   Minimal  - Simple and concise format
   Feature  - For new feature PRs
   Bugfix   - For bug fix PRs
```

### 5. Git Clean
`gw clean` keeps your repository tidy:

```text
╭────────────────── Git Clean ───────────────────╮
│                                                │
│ Remove merged branches and clean up the repo   │
│                                                │
╰────────────────────────────────────────────────╯

[?] Select branches to delete:
 > [x] feature/login-page (merged)
   [ ] feature/new-api (merged)
   [x] hotfix/typo-fix (merged)
```

### 6. Git Basics
`gw basics` is your interactive guide:

```text
╭─────────────  Git Basics  ─────────────╮
│                                        │
│  Learn and execute basic git commands  │
│                                        │
╰────────────────────────────────────────╯

[?] Select a category to explore:
 > Setup & Config
   Information
   Staging & Commits
   Branching & Merging
   Remote Operations
   Undo Operations
   Advanced
   Show All Commands
```

### 7. Git Who
`gw who` reveals the top contributors:

```text
╭────────────────── Git Who ───────────────────╮
│                                              │
│ Analyze code contributions by author         │
│                                              │
╰──────────────────────────────────────────────╯
Analyzing contributions... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100%

Contributions by Commits

Rank   Author             Commits    Percentage   Contribution
1st    Dev One            450        36.2%        ████████████░░░░░░░░░░░░
2nd    Dev Two            320        25.7%        ████████░░░░░░░░░░░░░░░░
3rd    Dev Three          150        12.1%        ████░░░░░░░░░░░░░░░░░░░░
```

### 8. Commit Lint
`gw lint` enforces your commit standards:

```text
╭──────────────── Commit Lint ─────────────────╮
│                                              │
│ Validate conventional commit messages        │
│                                              │
╰──────────────────────────────────────────────╯
Checking last 10 commits...

╭─ Status ── Hash ──── Type ────── Message ────────────────────────╮
│    ✓     a1b2c3d    feat       Add new login page component      │
│    ✓     e4f5g6h    fix        Resolve issue with auth token     │
│    ✗     i7j8k9l    -          wip fixing stuff                  │
╰──────────────────────────────────────────────────────────────────╯

Summary:
  Valid: 9
  Invalid: 1

Needs improvement. Only 90% of commits are valid.
```

## Testing

GitAssist comes with a comprehensive test suite. To run the tests, install the development dependencies and use `pytest`:

```bash
pip install pytest pytest-mock
pytest
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
