---
name: pr
description: Create a pull request from the current branch with auto-generated title and structured body
disable-model-invocation: true
---

# Pull Request

Create a PR from the current branch. Auto-generates a title from commits and writes a structured body.

## Process

1. **Survey the branch**: Run these in parallel to understand the full scope:
   - `git status` — check for uncommitted changes
   - `git log --oneline main..HEAD` — all commits on this branch
   - `git diff main...HEAD --stat` — files changed vs main
   - `git branch -vv` — check if branch tracks a remote

2. **Handle uncommitted changes**: If there are uncommitted changes, warn the user and ask whether to commit them first (using /commit style) or proceed without them.

3. **Generate PR content**:
   - **Title**: Derive from the commits. Keep it under 70 chars, terse, lowercase. If there's one commit, use its message. If multiple, write a summary.
   - **Body**: Use this structure:
     ```
     ## Summary
     - bullet point per logical change

     ## Test plan
     - [ ] checklist items for verifying the changes
     ```

4. **Push if needed**: If the branch has no upstream or is ahead of remote:
   - `git push -u origin HEAD`

5. **Create the PR**:
   ```bash
   gh pr create --title "..." --body "$(cat <<'EOF'
   ## Summary
   ...

   ## Test plan
   ...
   EOF
   )"
   ```

6. **Report**: Print the PR URL when done.

## Rules

- Default base branch is `main` — if the repo uses a different default, detect it with `gh repo view --json defaultBranchRef`
- Do NOT force-push
- Do NOT create draft PRs unless the user asks
- If a PR already exists for this branch, tell the user and show the URL instead of creating a duplicate
- Check for existing PR with `gh pr view HEAD` before creating
