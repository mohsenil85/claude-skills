# claude-skills

Reusable [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skills for everyday development workflows.

## Skills

| Skill | Description |
|-------|-------------|
| `/cmux` | Orchestrate cmux terminal sessions — parallel commands, output monitoring |
| `/commit` | Intelligently group dirty changes into clean, logical commits |
| `/health` | Run a health check across hosts and services |
| `/pi-worker` | Delegate coding work to cheaper local or OpenRouter models |
| `/plain` | Re-explain the previous answer in plain language, facts kept verbatim |
| `/pr` | Create a PR with auto-generated title and structured body |
| `/read-mail` | Daily mail triage — surface what needs action, process toward inbox zero |
| `/review` | Review code changes for bugs, security issues, and style |
| `/tidy` | Clean up code without changing behavior |
| `/undo` | Interactively undo recent git operations |

## Install

Clone the repo and symlink each skill directory into your Claude Code skills directory:

```bash
git clone https://github.com/mohsenil85/claude-skills.git ~/Projects/claude-skills

mkdir -p ~/.claude/skills
for skill in cmux commit health pi-worker plain pr read-mail review tidy undo; do
  ln -sf ~/Projects/claude-skills/$skill ~/.claude/skills/$skill
done
```

Symlink the whole skill *directory*, not the `SKILL.md` inside it. Skills are
resolved as directories, so linking the bare file drops the frontmatter
semantics (`disable-model-invocation`, `allowed-tools`) and leaves nowhere for a
skill to bundle helper scripts or reference files.

Skills that reference homelab hosts, credentials, or service layout live in a
separate private repo rather than here.

## Usage

In any Claude Code session, type `/<skill-name>` to invoke a skill:

```
/cmux            # orchestrate cmux terminal sessions
/commit          # group and commit dirty changes
/health          # health check across hosts and services
/pi-worker       # delegate work to a cheaper model
/plain           # re-explain the last answer in plain language
/pr              # create a pull request
/read-mail       # triage the inbox
/review          # review current diff
/review 42       # review PR #42
/tidy            # clean up code
/undo            # undo recent git operations
```
