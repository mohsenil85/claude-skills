---
name: batch-query
description: >
  Prep and submit self-contained prompts to OpenRouter batch-tier models (astra:batch, fable:batch) at 50% cost with a
  24h completion window, tracked in a shared SQLite ledger with cost reporting, and continue answers that were cut
  off. Use when asked to run a batch query, submit to batch, use astra/fable/fabel batch, /batch-query, or to check
  the batch queue, status, results, a continuation, or spend.
argument-hint: "[estimate|submit|continue|queue|status|collect|spend] ..."
---

# Batch Query

Submit prompts to half-price batch models through the OpenRouter Batch API: `openai/gpt-6-astra:batch` and
`anthropic/claude-fable-5.1:batch` ($5/M input, $25/M output, 1M context). Answers arrive within 24 hours. Astra has
taken 5 to 20 minutes; Fable anywhere from 10 minutes to about 12 hours.

Claude Code and pi share this skill and its state:

- **Tool:** `bq.py` next to this file. Run it as `python3 ~/.claude/skills/batch-query/bq.py` (pi sees the same file
  at `~/.pi/agent/skills/batch-query/bq.py`). It reads `OPENROUTER_API_KEY` from the environment.
- **State:** the ledger `~/.pi/agent/state/batch-query.db`, frozen prompts in `~/.pi/agent/state/batch-query-prompts/`,
  results in `~/.pi/agent/state/batch-query-results/` (JSON plus a readable `.md`).

## 1. Write the prompt

- **Self-contained.** There's no follow-up turn: put all context in one Markdown file and state your assumptions.
- **Instructions first.** For a long bundle (a codebase, a document set), put the task at the top and restate it
  briefly at the end.
- **Text only from `bq.py`.** The Batch API accepts images only as public `http(s)` URLs (never base64), and `bq.py`
  sends plain text, so describe visuals in words.

## 2. Estimate and get approval

```bash
python3 ~/.claude/skills/batch-query/bq.py estimate anthropic/claude-fable-5.1:batch /path/prompt.md 64000
```

- The estimate assumes 4 characters per token, which runs low. On a code-heavy bundle (HTML, CSS, Markdown), Claude's
  tokenizer billed about 1.7 times the estimate (64k estimated, 109k billed); GPT billed about 1.15 times. Scale the
  input figure before quoting a cost.
- Show the user the estimate before submitting unless they have approved a budget. State the trade-off: half price,
  answer within 24 hours.

## 3. Set max_tokens and reasoning

- Reasoning tokens count against `max_tokens` and are billed as output.
- On Claude models OpenRouter's default reasoning budget is large. A Fable run with `--max-tokens 32000` spent 24.6k
  tokens reasoning, which matches the `high` effort budget (80% of `max_tokens`), and its answer stopped after about
  3,000 words.
- For a long deliverable, raise `--max-tokens` (64000 or more), cap thinking with `--reasoning-effort medium` (50%) or
  `low` (20%) or `--reasoning-max-tokens N` (below `--max-tokens`), and ask for brief reasoning in the prompt.
- The `--reasoning-*` flags set OpenRouter's `reasoning` parameter. Batch request bodies take the chat-completions
  shape, but OpenRouter's batch docs don't mention `reasoning` explicitly: check the usage on the first result that
  uses it.

## 4. Submit

```bash
python3 ~/.claude/skills/batch-query/bq.py submit anthropic/claude-fable-5.1:batch /path/prompt.md \
  --max-tokens 64000 --reasoning-effort medium --digest "one-line summary"
```

- This writes a ledger row, freezes the prompt and submits a one-request batch.
- **`--dry-run`** prints the estimate and the request body without submitting.
- **The same question to several models:** run `submit` once per model with the same file.
- **Many questions to one model:** put one prompt per `.md`/`.txt` file in a directory and run
  `submit-many <model> <dir> [--max-tokens N]`; they become one batch.
- Unknown flags are rejected, so a typo can't silently fall back to the 16000-token default.

## 5. Track it

- **Persistent poller (survives the session):** the zmx session `batch-poller` polls every 10 minutes, saves results
  as they complete, and exits once every row is finished. Restart it after each new submission:

  ```bash
  zmx list | grep batch-poller     # an "ended=" field means it has exited
  zmx kill batch-poller            # only if it's listed with ended=
  zmx run batch-poller -d sh -c "/opt/homebrew/bin/python3 $HOME/.claude/skills/batch-query/bq.py poll-loop --interval 600"
  zmx history batch-poller | tail -3   # expect "poll-loop started"
  ```

  Use the absolute `/opt/homebrew/bin/python3`. zmx starts a login shell whose PATH finds an old Intel `python3` in
  `/usr/local/bin` first, which fails with "Bad CPU type" (exit 126).
- **Claude Code, to be told when a row finishes** (only while the session is open): run this with Bash
  `run_in_background`, replacing `<ID>`:

  ```bash
  until s=$(sqlite3 ~/.pi/agent/state/batch-query.db "select status from queries where id=<ID>;"); [[ "$s" =~ ^(completed|failed|expired|cancelled)$ ]]; do sleep 300; done; echo "row <ID>: $s"
  ```

- **On demand:** `queue`, `status <id>` (polls once), `collect <id>`, `spend`.

## 6. Collect and report

- Check for truncation first: the result `.md` carries a "TRUNCATED" note, and `completion_tokens` equals the cap.
- Report the key points, the actual cost against the estimate, and the running total from `spend`. The full text stays
  in the result files.

## 7. Continue an answer that was cut off

```bash
python3 ~/.claude/skills/batch-query/bq.py continue <id> --dry-run     # writes the prompt, shows the estimate
python3 ~/.claude/skills/batch-query/bq.py continue <id> --reasoning-effort medium --note-file /path/extra.md
```

- This sends the same model the original prompt, the cut-off answer, and an instruction to resume exactly where it
  stopped. The continuation is a new ledger row; the default `--max-tokens` is double the original's.
- Use `--note` or `--note-file` for specifics, such as what's still missing or facts checked since the first run.
- It refuses rows that weren't truncated (override with `--force`), rows with several requests, and answers with no
  text at all (resubmit with a higher cap instead).
- The two parts are separate results: join them when reporting.

## Notes

- Statuses run `validating → in_progress → finalizing → completed`; the final states are completed, failed, expired and
  cancelled.
- OpenRouter deletes batch artifacts after 30 days. Results are saved locally on completion, so nothing is lost.
- In pi, pair this with the `panel-query` skill: a quick answer now from the panel, and the thorough one from a batch
  model later.
- Unknown batch slugs are rejected. To add a model, check its OpenRouter page for a `:batch` variant and add it to
  `PRICES` in `bq.py`.
