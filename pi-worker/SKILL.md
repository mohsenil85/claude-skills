---
name: pi-worker
description: Delegate coding work (implement, review, scout) to pi workers running on cheaper or local models — the local GPU (qwen3.8-27b via LiteLLM) or OpenRouter (DeepSeek, Kimi, GLM, Qwen, …) — through the `pi-worker` CLI, while you stay the orchestrator. Use when asked to delegate, "use pi", use the local/GPU/OpenRouter/qwen/deepseek model, fan work out in parallel, run a review loop, or keep your own context small on grunt work.
argument-hint: "[-b backend] [-r role] <task>"
---

# pi-worker: delegate to pi workers on other models

You are the orchestrator. `pi-worker` runs one non-interactive `pi` coding agent (its own tools: read/bash/edit/write/grep/find/ls) on a backend you choose, in a directory you choose, and prints the worker's final message plus a footer with run id, cost, tool counts, and changed files. Workers have **no memory of this conversation** — every task text must be self-contained.

## Commands

```bash
pi-worker [-b BACKEND] [-r ROLE] [-C DIR] [-w NAME] [--commit] [--thinking LVL] [--timeout S] "task"
pi-worker -f task.md ...                # long task from a file ('-' = stdin)
pi-worker --resume RUN_ID "follow-up"   # continue the same worker session (keeps its context)
pi-worker --trace RUN_ID                # compact tool-call trace when a result looks wrong
pi-worker --json ...                    # machine-readable envelope instead of text+footer
pi-worker --list-backends | --runs | --ping BACKEND
```

Result contract: the worker's final message ends with a `## Report` block (Outcome / Changes / Verification / Notes / Questions). Read Outcome first; `blocked` or `partial` means you decide next steps. Exit code is 1 on model error or timeout.

## Backends (`-b`) — see `pi-worker --list-backends`; edit `~/.config/pi-worker/config.json` to change

| alias | model | use for |
|---|---|---|
| `local` (default) | homelab/qwen3.8-27b — local GPU via LiteLLM | free, private, sequential grunt work |
| `or` | openrouter/deepseek/deepseek-v4-pro-0813 | default paid worker; parallel fan-out |
| `or-cheap` | openrouter/deepseek/deepseek-v4-flash | scouting, summaries, trivial edits |
| `or-kimi` / `or-glm` / `or-qwen` / `or-opus` | Kimi K3 / GLM 5.2 / Qwen 3.8 Max / Opus 4.8 | harder tasks; escalate deliberately |
| `or:<id>` / `local:<id>` / `provider/model[:thinking]` | anything in pi's models.json | ad hoc |

Local-backend rules (one GPU, one resident model): **never mix local model ids** in one session (each swap reloads a 27B model, ~2–5 min, and stalls everything else); run local jobs **sequentially**, and start with `pi-worker --ping local` to warm it. Fan-out belongs on OpenRouter. Cold local runs take minutes: run them in the background (Claude Code: Bash with `run_in_background: true`; pi: background/`&` with output to a file).

## Roles (`-r`)

- `worker` (default): all tools; implements, verifies with tests, never commits unless told; reports assumptions.
- `reviewer`: read-only + bash; findings as `[severity] file:line — issue — fix`; never edits.
- `scout`: read-only; maps relevant files, entry points, conventions, risks with `file:line` anchors.
- `none`: plain pi, no role prompt. Override tools with `-t read,grep,find,ls,bash,edit,write`.

Role prompts live in `~/.config/pi-worker/roles/*.md` (shared by every orchestrator) — edit them there, not per-task.

## Writing a good task (workers start blank)

Include: goal, exact paths/functions, constraints (style, deps, "no commits"), acceptance criteria, and how to verify (test command). Prefer `-f task.md` for anything over a paragraph. Say what NOT to touch. Don't ask the worker to make product decisions — decide, then delegate. Example:

```bash
pi-worker -b or -C ~/Projects/foo -f - <<'TASK'
Goal: add `--json` output to `foo/cli.py` (`main()`); emit the same fields as the text output.
Constraints: stdlib only; keep existing text output identical; follow the argparse style already in cli.py.
Verify: `python -m pytest tests/test_cli.py -q` must pass; add a test for --json.
Do not: touch files outside foo/cli.py and tests/test_cli.py; do not commit.
TASK
```

## Patterns

1. **Scout → plan → work → review → fix**: `-r scout` (or-cheap) to map code → you plan → `-r worker` implements → `-r reviewer` on the diff → `--resume WORKER_RUN "Address findings: …"` → re-review. Stop after 2–3 rounds; do the rest yourself.
2. **Parallel fan-out (OpenRouter only)**: one worker per independent unit, each in its own worktree: `pi-worker -b or -w unit-a --commit "…" ` etc. (Claude Code: several background Bash calls; pi: several `&` jobs). Then integrate: `git -C REPO merge pi/unit-a` (or `git diff main..pi/unit-a` to inspect / cherry-pick), and clean up: `git -C REPO worktree remove .worktrees/unit-a && git -C REPO branch -D pi/unit-a`. Worktrees live at `REPO/.worktrees/NAME` on branch `pi/NAME`; without `--commit` the worker leaves changes uncommitted there for you to review first.
3. **Second opinion**: `-r reviewer -b or-kimi` (or `or-opus`) on your own diff before you finish.
4. **Cheap bulk edits**: mechanical rewrites/migrations across files → `local` sequentially, or `or-cheap` in parallel worktrees.

## Judgment

- Delegate self-contained, verifiable units — not "figure out the design". Keep architecture, ambiguity, and integration for yourself.
- Trust but verify: read `Changes`/`Verification`, then check the diff (`git diff`) or run the tests yourself before merging. Use `--trace` when a report smells wrong.
- Cost shows in the footer for OpenRouter (`local` is free). Escalate models only when a cheaper one failed on the same task.
- Runs are recorded under `~/.local/state/pi-worker/runs/RUN_ID/` (task, events, session, result.json).
- If you ever call raw `pi -p` instead of `pi-worker`, redirect stdin: `pi -p ... </dev/null`. pi reads piped stdin to EOF when stdin isn't a TTY, and harness-held sockets never close → it hangs forever before sending a request. `pi-worker` does this for you.
- A local run failing with `Request timed out.` means the GPU box is busy/swapping (often another pi session hammering it) — check `pi-worker --ping local` before retrying; don't stack more local jobs on it.

## Orchestrator notes

- **Claude Code**: this skill lives at `~/.claude/skills/pi-worker/`; call `pi-worker` via Bash. Long/local runs → `run_in_background: true` and read the notification. Runs without prompts in auto mode; in prompting modes add `Bash(pi-worker:*)` to `permissions.allow` yourself.
- **pi as orchestrator**: same skill (pi loads it via `skills` in `~/.pi/agent/settings.json`), same CLI via the `bash` tool; `pi-subagents` is the native alternative when you want pi-managed children.
