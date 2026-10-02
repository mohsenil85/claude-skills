#!/usr/bin/env python3
"""batch-query — system of record + OpenRouter Batch API client.

SQLite DB (system of record): ~/.pi/agent/state/batch-query.db

Subcommands:
  estimate <model> <prompt-file> [max_tokens]   -- preflight cost report, no submit
  submit  <model> <prompt-file> [--max-tokens N] [--digest "one liner"]
                                               -- preflight + submit 1-item batch
  submit-many <model> <prompts-dir>             -- one batch, N requests (one file each)
  queue                                        -- list ledger rows
  status  <id>                                 -- poll single row once, update db
  collect <id>                                 -- fetch results to disk, update db
  poll-loop [--interval 600]                   -- zmx poller: loop until all rows terminal
  spend                                        -- lifetime + recent cost report
"""
import json, os, sqlite3, sys, time, urllib.request, urllib.error

DB_PATH = os.path.expanduser("~/.pi/agent/state/batch-query.db")
RESULTS_DIR = os.path.expanduser("~/.pi/agent/state/batch-query-results")
PROMPTS_DIR = os.path.expanduser("~/.pi/agent/state/batch-query-prompts")
API = "https://openrouter.ai/api/beta/batches"
WINDOW_SECONDS = 24 * 3600
# per-token (per-M) pricing for known batch models; fallback fetch not attempted
PRICES = {
    "openai/gpt-6-astra:batch": (5.0, 25.0),
    "anthropic/claude-fable-5.1:batch": (5.0, 25.0),
}
TERMINAL = {"completed", "failed", "expired", "cancelled"}


def db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS queries (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          batch_ref TEXT,
          model TEXT NOT NULL,
          question_digest TEXT,
          prompt_path TEXT,
          est_cost_usd REAL,
          max_tokens INTEGER,
          n_requests INTEGER DEFAULT 1,
          submitted_at TEXT,
          deadline_at TEXT,
          status TEXT DEFAULT 'pending',
          actual_cost_usd REAL,
          usage_json TEXT,
          result_path TEXT,
          collected_at TEXT
        );
        """
    )
    return con


def http(method, url, body=None):
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        sys.exit("OPENROUTER_API_KEY not set")
    req = urllib.request.Request(url, method=method)
    req.add_header("Authorization", f"Bearer {key}")
    if body is not None:
        req.add_header("Content-Type", "application/json")
        data = json.dumps(body).encode()
    else:
        data = None
    try:
        with urllib.request.urlopen(req, data=data) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code} from {url}: {e.read().decode()[:500]}")


def count_tokens(text):
    # cheap estimate: chars/4. Good enough for a preflight estimate.
    return max(1, len(text) // 4)


def estimate(model, prompt, max_tokens):
    if model not in PRICES:
        sys.exit(f"Unknown batch model {model!r}. Known: {', '.join(PRICES)}")
    pin, pout = PRICES[model]
    tin = count_tokens(prompt)
    lo = tin / 1e6 * pin
    # worst case: model uses all max_tokens
    hi = lo + max_tokens / 1e6 * pout
    return tin, lo, hi


def preflight_report(model, prompt, max_tokens):
    # gate: batch API is text-only
    for ch in prompt:
        if ord(ch) > 0xFFFF:
            print("WARNING: unusual characters in prompt — verify text-only content.")
            break
    tin, lo, hi = estimate(model, prompt, max_tokens)
    print(f"model:        {model}")
    print(f"prompt chars: {len(prompt)}  (~{tin} tokens est)")
    print(f"max_tokens:   {max_tokens}  (hard cap — this bounds the bill)")
    # worst case is the number to plan on: reasoning models routinely
    # consume most of max_tokens
    print(f"cost est:     ${lo:.4f} (prompt only)  ..  ${hi:.4f} (WORST CASE — plan on this)")
    print(f"sync equiv:   ~${2*hi:.4f} worst case (batch is 50% off)")
    return tin, lo, hi


def freeze_prompt(model, prompt, label="prompt"):
    os.makedirs(PROMPTS_DIR, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    safe = "".join(c for c in label if c.isalnum() or c in "-_ ")[:40].strip().replace(" ", "_")
    path = os.path.join(PROMPTS_DIR, f"{stamp}-{model.replace('/', '_')}-{safe or label and 'q'}.md")
    path = os.path.join(PROMPTS_DIR, f"{stamp}-{model.replace('/', '_').replace(':','-')}.md")
    with open(path, "w") as f:
        f.write(prompt)
    return path


def build_request(prompt, max_tokens, idx=0):
    return {
        "custom_id": f"req-{idx:04d}",
        "body": {
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        },
    }


def cmd_estimate(args):
    model, prompt_file = args[0], args[1]
    max_tokens = int(args[2]) if len(args) > 2 else 16000
    prompt = open(prompt_file).read()
    preflight_report(model, prompt, max_tokens)


def submit(model, prompts, digests, max_tokens):
    if model not in PRICES:
        sys.exit(f"Unknown batch model {model!r}. Known: {', '.join(PRICES)}")
    # combined preflight
    total_lo = total_hi = 0.0
    for p in prompts:
        _, lo, hi = estimate(model, p, max_tokens)
        total_lo += lo
        total_hi += hi
    print(f"submitting {len(prompts)} request(s) to {model}")
    print(f"cost est: ${total_lo:.4f} .. ${total_hi:.4f} (worst case)")
    body = {
        "endpoint": "/v1/chat/completions",
        "model": model,
        "requests": [build_request(p, max_tokens, i) for i, p in enumerate(prompts)],
    }
    # NOTE: keys serialized in insertion order: endpoint, model, requests (stream-parse requirement)
    resp = http("POST", API, body)
    now = time.time()
    con = db()
    paths = []
    for i, p in enumerate(prompts):
        pp = freeze_prompt(model, p, digests[i] if i < len(digests) else "")
        paths.append(pp)
        con.execute(
            "INSERT INTO queries (batch_ref, model, question_digest, prompt_path, est_cost_usd, max_tokens, n_requests, submitted_at, deadline_at, status) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (
                resp.get("id"),
                model,
                digests[i] if i < len(digests) else f"req {i}",
                pp,
                (total_lo / len(prompts)) if len(prompts) else 0,
                max_tokens,
                len(prompts),
                time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(now)),
                time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(now + WINDOW_SECONDS)),
                resp.get("status", "validating"),
            ),
        )
    con.commit()
    rowid = con.execute("SELECT last_insert_rowid()").fetchone()[0]
    print(f"submitted: batch_ref={resp.get('id')} status={resp.get('status')} window=24h")
    print(f"ledger row(s) written (last id={rowid}); prompts frozen under {PROMPTS_DIR}")
    return resp.get("id")


def cmd_submit(args):
    model, prompt_file = args[0], args[1]
    max_tokens, digest = 16000, ""
    rest = args[2:]
    i = 0
    while i < len(rest):
        if rest[i] == "--max-tokens":
            max_tokens = int(rest[i + 1]); i += 2
        elif rest[i] == "--digest":
            digest = rest[i + 1]; i += 2
        else:
            i += 1
    prompt = open(prompt_file).read()
    if not digest:
        digest = prompt.strip().splitlines()[0][:70] if prompt.strip() else "untitled"
    submit(model, [prompt], [digest], max_tokens)


def cmd_submit_many(args):
    model, prompts_dir = args[0], args[1]
    files = sorted(f for f in os.listdir(prompts_dir) if f.endswith((".md", ".txt")))
    if not files:
        sys.exit("no .md/.txt files found")
    prompts = [open(os.path.join(prompts_dir, f)).read() for f in files]
    digests = [f for f in files]
    submit(model, prompts, digests, 16000)


def refresh(con, row):
    """Poll OpenRouter once for a row's batch; update status/usage/results."""
    if not row["batch_ref"] or row["status"] in TERMINAL and row["result_path"]:
        return row["status"]
    b = http("GET", f"{API}/{row['batch_ref']}")
    status = b.get("status", "unknown")
    usage = b.get("usage")
    result_path = row["result_path"]
    if status == "completed":
        os.makedirs(RESULTS_DIR, exist_ok=True)
        result_path = os.path.join(RESULTS_DIR, f"{row['batch_ref']}.json")
        with open(result_path, "w") as f:
            json.dump(b, f, indent=1)
        # also write human-readable answers
        answers = []
        for r in b.get("results") or []:
            cid = r.get("custom_id")
            if r.get("response"):
                choice = r["response"].get("body", {}).get("choices", [{}])[0]
                msg = choice.get("message", {}).get("content", "")
                answers.append(f"## {cid}\n\n{msg}\n")
                if choice.get("finish_reason") == "length":
                    answers.append(
                        f"\n> ⚠️ TRUNCATED — {cid} hit the max_tokens cap "
                        "(finish_reason=length) and was cut off mid-stream. "
                        "Fire a continuation prompt (include this tail) or resubmit "
                        "with a higher --max-tokens.\n"
                    )
                    print(f"WARNING: {cid} truncated (finish_reason=length, max_tokens cap reached)")
            elif r.get("error"):
                answers.append(f"## {cid}\n\nERROR: {r['error']}\n")
        md = result_path.replace(".json", ".md")
        with open(md, "w") as f:
            f.write("".join(answers))
        result_path = md
    con.execute(
        "UPDATE queries SET status=?, usage_json=?, actual_cost_usd=?, result_path=?, collected_at=? WHERE id=?",
        (
            status,
            json.dumps(usage) if usage else row["usage_json"],
            # batch-level usage.cost split evenly across rows sharing the batch
            ((usage or {}).get("cost") / row["n_requests"]) if (usage or {}).get("cost") is not None else row["actual_cost_usd"],
            result_path,
            time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) if status in TERMINAL else row["collected_at"],
            row["id"],
        ),
    )
    con.commit()
    return status


def cmd_queue(_):
    con = db()
    rows = con.execute("SELECT * FROM queries ORDER BY id DESC LIMIT 50").fetchall()
    if not rows:
        print("ledger is empty"); return
    print(f"{'id':>3}  {'status':<11} {'model':<34} {'est':>7} {'act':>7}  digest")
    for r in rows:
        est = f"${r['est_cost_usd']:.3f}" if r["est_cost_usd"] else "-"
        act = f"${r['actual_cost_usd']:.4f}" if r["actual_cost_usd"] is not None else "-"
        print(f"{r['id']:>3}  {r['status']:<11} {r['model']:<34} {est:>7} {act:>7}  {r['question_digest']}")


def cmd_status(args):
    con = db()
    row = con.execute("SELECT * FROM queries WHERE id=?", (int(args[0]),)).fetchone()
    if not row:
        sys.exit("no such row")
    s = refresh(con, row)
    row = con.execute("SELECT * FROM queries WHERE id=?", (row["id"],)).fetchone()
    print(f"id={row['id']} batch={row['batch_ref']} status={s}")
    print(f"  model:    {row['model']}  ({row['n_requests']} request(s))")
    print(f"  digest:   {row['question_digest']}")
    print(f"  deadline: {row['deadline_at']}")
    print(f"  est: ${row['est_cost_usd']:.4f}  actual: {row['actual_cost_usd']}")
    if row["usage_json"]:
        print(f"  usage:    {row['usage_json']}")
    if row["result_path"]:
        print(f"  results:  {row['result_path']}")


def cmd_collect(args):
    con = db()
    row = con.execute("SELECT * FROM queries WHERE id=?", (int(args[0]),)).fetchone()
    if not row:
        sys.exit("no such row")
    s = refresh(con, row)
    if s == "completed":
        print(f"collected -> see results under {RESULTS_DIR}")
    else:
        print(f"status={s} — not terminal yet; try again later")


def cmd_poll_loop(args):
    interval = 600
    if "--interval" in args:
        interval = int(args[args.index("--interval") + 1])
    con = db()
    print(f"poll-loop started (interval {interval}s). Ctrl-C to stop.")
    while True:
        rows = con.execute(
            "SELECT * FROM queries WHERE status NOT IN ('completed','failed','expired','cancelled')"
        ).fetchall()
        if not rows:
            print("all rows terminal — poller exiting")
            return
        for row in rows:
            try:
                s = refresh(con, row)
                print(f"[{time.strftime('%H:%M:%S')}] id={row['id']} {row['batch_ref']} -> {s}")
                if s in TERMINAL and row["est_cost_usd"]:
                    row2 = con.execute("SELECT actual_cost_usd FROM queries WHERE id=?", (row["id"],)).fetchone()
                    print(f"    est ${row['est_cost_usd']:.4f}  actual ${row2['actual_cost_usd'] or 0:.4f}")
            except SystemExit as e:
                print(f"    error: {e}")
        time.sleep(interval)


def cmd_spend(_):
    con = db()
    tot = con.execute("SELECT SUM(actual_cost_usd) s, COUNT(*) n FROM queries WHERE actual_cost_usd IS NOT NULL").fetchone()
    est = con.execute("SELECT SUM(est_cost_usd) s FROM queries WHERE actual_cost_usd IS NULL").fetchone()
    print(f"lifetime actual spend: ${tot['s'] or 0:.4f} across {tot['n']} completed batch query rows")
    if est["s"]:
        print(f"pending (estimated):  ${est['s']:.4f}")


def main():
    if len(sys.argv) < 2:
        print(__doc__); return
    cmd, args = sys.argv[1], sys.argv[2:]
    {
        "estimate": cmd_estimate,
        "submit": cmd_submit,
        "submit-many": cmd_submit_many,
        "queue": cmd_queue,
        "status": cmd_status,
        "collect": cmd_collect,
        "poll-loop": cmd_poll_loop,
        "spend": cmd_spend,
    }.get(cmd, lambda a: print(__doc__))(args)


if __name__ == "__main__":
    main()
