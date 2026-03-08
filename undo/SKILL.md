---
name: undo
description: Interactively undo recent git operations — commits, staging, or file changes
disable-model-invocation: true
---

# Undo

Survey recent git state and help undo operations safely.

## Process

1. **Survey current state**: Run these in parallel:
   - `git log --oneline -10` — recent commits
   - `git status` — staged/unstaged/untracked changes
   - `git diff --stat` — what's changed
   - `git diff --staged --stat` — what's staged

2. **Present options**: Based on the state, show what can be undone:
   - **Last commit** (if there are recent commits): "Undo last commit — keeps changes staged"
   - **Last N commits**: "Undo last N commits — keeps changes staged"
   - **Staged changes**: "Unstage all / specific files"
   - **Unstaged changes**: "Discard changes to specific files"
   - **Untracked files**: "Remove untracked files"

3. **Ask the user** what they want to undo. Don't assume.

4. **Execute** the appropriate operation:

| Action | Command |
|--------|---------|
| Undo last commit (keep changes) | `git reset --soft HEAD~1` |
| Undo last N commits (keep changes) | `git reset --soft HEAD~N` |
| Undo last commit (discard changes) | `git reset --hard HEAD~1` |
| Unstage all files | `git reset HEAD` |
| Unstage specific file | `git restore --staged <file>` |
| Discard unstaged changes to file | `git restore <file>` |
| Discard all unstaged changes | `git restore .` |
| Remove untracked files | `git clean -fd` |

5. **Confirm before destructive ops**: Any operation that discards changes (`--hard`, `restore`, `clean`) requires explicit user confirmation before executing. Show exactly what will be lost.

6. **Report result**: Show `git status` and `git log --oneline -5` after the operation so the user can verify.

## Rules

- NEVER force-push after undoing commits — that's the user's decision
- NEVER undo commits that have been pushed without warning the user
- Check `git log --oneline -1 --format='%D'` to see if HEAD commit has been pushed (shows remote tracking)
- Default to `--soft` reset (keeps changes) unless user explicitly asks to discard
- If the user asks to undo something ambiguous, ask for clarification
- Show what will happen before doing it
