<!-- daily-code-journal: topic_id=git-status -->
# Inspect working-tree changes

**Date (IST):** 2026-11-27  
**Category:** Git and GitHub  
**Publishing method:** Automated from a curated, reviewed topic library.

## Explanation

`git status --short` shows concise status codes for staged, unstaged, and untracked paths. Review changes before staging or committing.

## Practical example

```bash
git status --short
```

## Expected output or usage

```text
Example: ?? notes.md (untracked file)
```

## Time and space complexity

Command cost depends on repository file count and filesystem state.

## Key learning points

- Inspect the worktree before staging.
- Untracked files are marked with ?? in short status.

---

*Scheduled publication is automated; it does not imply live coding on this date.*
