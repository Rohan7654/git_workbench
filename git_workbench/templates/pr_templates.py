class PRTemplates:
    """Collection of PR description templates"""

    STANDARD = """## Description
{description}

## Changes Made
{changes}

## Type of Change
{change_type}

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings generated

## Related Issues
{issues}

## Screenshots (if applicable)
<!-- Add screenshots here -->

## Additional Notes
{notes}
"""

    MINIMAL = """## What
{description}

## Why
{reason}

## Changes
{changes}
"""

    FEATURE = """## New Feature

### Description
{description}

### Implementation Details
{changes}

### How to Test
1. {test_steps}

### Screenshots
<!-- Add screenshots here -->

### Breaking Changes
{breaking_changes}

### Related Issues
Closes #{issue_number}
"""

    BUGFIX = """## Bug Fix

### Problem
{problem}

### Solution
{solution}

### Changes Made
{changes}

### Root Cause
{root_cause}

### Testing
- [ ] Verified fix resolves the issue
- [ ] Added regression tests
- [ ] Tested edge cases

### Related Issues
Fixes #{issue_number}
"""

    HOTFIX = """## Hotfix

### Critical Issue
{issue}

### Fix Applied
{fix}

### Impact
{impact}

### Rollback Plan
{rollback}

### Verification Steps
1. {verification}
"""

    REFACTOR = """## Refactoring

### What was refactored
{description}

### Why
{reason}

### Changes
{changes}

### Performance Impact
{performance}

### Breaking Changes
- [ ] No breaking changes
- [ ] Breaking changes (described below)

{breaking_description}
"""

    DOCS = """## Documentation Update

### What was updated
{description}

### Sections Changed
{sections}

### Reason for Update
{reason}
"""

    @classmethod
    def get_template(cls, template_type: str) -> str:
        """Get template by type"""
        templates = {
            "standard": cls.STANDARD,
            "minimal": cls.MINIMAL,
            "feature": cls.FEATURE,
            "bugfix": cls.BUGFIX,
            "hotfix": cls.HOTFIX,
            "refactor": cls.REFACTOR,
            "docs": cls.DOCS,
        }
        return templates.get(template_type.lower(), cls.STANDARD)

    @classmethod
    def list_templates(cls) -> list:
        """List available templates"""
        return [
            "standard",
            "minimal",
            "feature",
            "bugfix",
            "hotfix",
            "refactor",
            "docs",
        ]
