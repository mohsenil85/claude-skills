---
name: commit
description: Intelligently group dirty working tree changes into clean, logical commits
disable-model-invocation: true
---

# Smart Commit

Take all uncommitted changes (staged, unstaged, and untracked) and create a series of clean, logical commits.

## Process

1. **Survey changes**: Run `git status` and `git diff` (staged + unstaged) to see everything. Also check `git log --oneline -5` to understand recent commit style.

2. **Analyze and group**: Study every changed/added/deleted file and the actual diff content. Group changes into logical units — each commit should represent one coherent change (e.g., "add DVD import docs", "update network inventory", "fix nginx config"). Files that are related to the same logical change go in the same commit. Unrelated changes get separate commits.

3. **Plan commits**: Before executing, briefly list the planned commits and what files go in each. Keep it short.

4. **Execute commits sequentially**: For each logical group:
   - Stage only the files for that group: `git add <specific files>`
   - If a file has changes belonging to multiple groups, use `git add -p` or commit the whole file with whichever group it fits best
   - Commit with a terse, lowercase message (no period, no conventional-commits prefix unless the repo uses them)
   - Use imperative mood (e.g., "add x", "fix y", "update z")

## Commit message style

- Terse — ideally under 50 chars
- Lowercase
- Imperative mood ("add", "fix", "update", "remove", not "added", "fixes")
- No trailing period
- No `Co-Authored-By` or attribution lines
- No body unless genuinely needed for a non-obvious change

## Rules

- Do NOT use `git add -A` or `git add .` — always add specific files
- Do NOT amend existing commits
- Do NOT combine unrelated changes into one commit just because they're small
- It's fine to have single-file commits
- If there's only one logical change, just make one commit
- Respect .gitignore — don't commit ignored files
- If unsure whether changes are related, err on the side of separate commits
