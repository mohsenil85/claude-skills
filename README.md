# claude-skills

Reusable [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skills for everyday development workflows.

## Skills

| Skill | Description |
|-------|-------------|
| `/commit` | Intelligently group dirty changes into clean, logical commits |
| `/pr` | Create a PR with auto-generated title and structured body |
| `/review` | Review code changes for bugs, security issues, and style |
| `/tidy` | Clean up code without changing behavior |
| `/undo` | Interactively undo recent git operations |

## Install

Clone the repo and symlink each skill into your Claude Code skills directory:

```bash
git clone https://github.com/nnnnicholas/claude-skills.git ~/Projects/claude-skills

mkdir -p ~/.claude/skills
for skill in commit pr review tidy undo; do
  ln -sf ~/Projects/claude-skills/$skill ~/.claude/skills/$skill
done
```

## Usage

In any Claude Code session, type `/<skill-name>` to invoke a skill:

```
/commit          # group and commit dirty changes
/pr              # create a pull request
/review          # review current diff
/review 42       # review PR #42
/tidy            # clean up code
/undo            # undo recent git operations
```
