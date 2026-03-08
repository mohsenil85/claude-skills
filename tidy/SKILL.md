---
name: tidy
description: Clean up code without changing behavior — dead imports, unused vars, formatting
disable-model-invocation: true
---

# Tidy

Clean up code in the current repo without changing behavior. Remove dead imports, unused variables, trailing whitespace, and formatting issues.

## Process

1. **Survey the codebase**: Run `git status` to see what's being worked on. Check the primary language(s) and any existing linter/formatter configs (e.g., `.eslintrc`, `pyproject.toml`, `.editorconfig`, `rustfmt.toml`).

2. **Identify cleanup targets**: Look for:
   - Dead/unused imports
   - Unused variables and functions
   - Trailing whitespace
   - Inconsistent indentation (tabs vs spaces — match existing style)
   - Blank line issues (excessive blank lines, missing blank lines between functions)
   - Debug/console statements left behind (e.g., `console.log`, `print("debug")`)
   - Commented-out code blocks (not explanatory comments — dead code)

3. **Respect existing style**: Do NOT impose new conventions. If the project uses single quotes, keep single quotes. If it uses tabs, keep tabs. Match what's already there.

4. **Make changes**: Edit files to clean them up. Keep changes purely cosmetic/hygienic — nothing that alters behavior.

5. **Verify**: Run any available linter or formatter to confirm changes are consistent. If the project has tests, run them to confirm nothing broke.

6. **Commit**: Stage and commit the cleanup using /commit style messages (terse, lowercase, imperative). Group related cleanups logically — e.g., one commit for "remove unused imports" across files, another for "fix trailing whitespace".

## Rules

- Do NOT change behavior — if you're unsure whether a removal changes behavior, leave it
- Do NOT add new code, features, or abstractions
- Do NOT reorganize file structure or move code between files
- Do NOT add type annotations, docstrings, or comments
- Do NOT change variable names (even if you think yours is better)
- Do NOT "improve" working code — this is strictly cleanup
- If there's nothing to clean up, say so and stop
- If the project has a formatter (prettier, black, gofmt), prefer running it over manual edits
