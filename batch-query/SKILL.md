---
name: batch-query
description: >
  Prep and submit questions to OpenRouter batch-tier models (astra:batch,
  fable:batch) at 50% cost with a 24h completion window, tracked in a SQLite
  system of record with cost reporting. Use when asked to run a batch query,
  submit to batch, use astra/fabel batch, /batch, or to check batch queue,
  status, collect, or spend.
---

# Batch Query

Submit questions to half-price batch models (`openai/gpt-6-astra:batch`,
`anthropic/claude-fable-5.1:batch`, both $5/M in $25/M out, 1M ctx) via the
OpenRouter Batch API. Answers arrive within 24h (usually much sooner).
Everything is tracked in SQLite: `~/.pi/agent/state/batch-query.db`.

Tooling: `bq.py` next to this file. It reads `OPENROUTER_API_KEY` from env.

## Procedure

### 1. Pre-flight (always, before any submit)

- **Prompt is self-contained and text-only.** Batch has no follow-up and
  rejects images/files. Bake all context into the prompt; state assumptions
  explicitly ("Assume X unless stated"). Extract any session context into the
  prompt text before freezing it.
- **Dry-run the cost estimate**:

  ```bash
  python3 ~/.pi/agent/skills/batch-query/bq.py estimate \
    anthropic/claude-fable-5.1:batch /tmp/prompt.md [max_tokens]
  ```

  Shows token estimate, cost range (prompt-only .. worst case at max_tokens),
  and the sync-equivalent price for comparison. Default max_tokens is 16000.
- **Present the estimate to the user before submitting** unless they said
  "just submit it". The tradeoff to state: half price, answer within 24h.

### 2. Submit

```bash
python3 bq.py submit <model> <prompt-file> --max-tokens 16000 --digest "one-line summary"
```

Writes the ledger row (prompt frozen under
`~/.pi/agent/state/batch-query-prompts/`), submits a 1-item batch, prints the
batch_ref. For many questions at once: put one prompt per `.md`/`.txt` file in
a directory and use `submit-many <model> <dir>` — all become one batch.

### 3. Start the zmx poller (after submitting, if not already running)

```bash
# via zmx_run (persistent session, non-blocking):
sh -c "python3 ~/.pi/agent/skills/batch-query/bq.py poll-loop --interval 600"
```

Run it in the zmx session `batch-poller`. It polls every 10 min, updates the
DB in place, fetches results on completion (saved under
`~/.pi/agent/state/batch-query-results/` as JSON + readable .md), and exits
when every row is terminal. Idempotent/resumable — if in doubt whether it's
running, starting it again is safe (check `zmx_list` first to avoid dupes).

### 4. Inspect / report

- `bq.py queue` — table: id, status, model, est vs actual cost, digest
- `bq.py status <id>` — poll once, full detail (usage, deadline, result path)
- `bq.py collect <id>` — fetch results for one row now
- `bq.py spend` — lifetime actual + pending estimated spend

On collect, report to the user: answer headline/key points, **actual vs
estimated cost**, and running total from `spend`. Full text stays in the
result files.

## Notes

- Statuses: `validating → in_progress → finalizing → completed` (terminal:
  completed/failed/expired/cancelled).
- OpenRouter deletes batch artifacts after 30 days — results are saved
  locally on completion, so this is handled.
- Good pattern (panel crossover): run the panel-query skill now for a cheap
  immediate answer, and queue the same question to a batch model for the
  authoritative version.
- Unknown batch slugs are rejected by `bq.py` — check the model's OpenRouter
  page for a `:batch` variant and add it to `PRICES` in `bq.py` if new.
