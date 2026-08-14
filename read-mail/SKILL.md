---
name: read-mail
description: Daily mail triage — read unread, surface what needs action, and process the inbox toward zero (pin actions, archive reference, defer the rest)
---

# Read Mail (triage to zero)

Fetch unread inbox mail, present a GTD-style digest, and process the inbox toward empty: pin true next-actions, archive pure-reference/FYI, defer the rest. The goal is an inbox that ends at (or near) zero — not a pile marked "read."

Background: the inbox is now a real in-tray. Machine noise is auto-filed by Sieve rules (banks → `Reference/Finance`, USPS → `Reference/Shipping`, Amazon-orders/Discogs → `Reference/Receipts`) and newsletters live in Miniflux (`rss.lan`). So unread inbox mail is mostly human correspondence and genuine decisions.

## Process

1. **Get mailboxes**: `mcp__fastmail__list_mailboxes` → note the Inbox, Archive, and `Someday` IDs.

2. **Fetch unread**: `mcp__fastmail__search_emails` for unread in Inbox. Also glance at Spam (last 24h) for false positives.

3. **Read & classify** each unread message (`get_email` for content; batch 5–10). Assign one GTD disposition:
   - **Do-now (<2 min)** — a quick reply / click / confirm. Do it, then archive.
   - **Action (>2 min, yours)** — needs real work → **Pin** (it floats to the top as your Next-Actions list).
   - **Waiting** — blocked on someone else → suggest **Snooze** to the chase-up date.
   - **Reference / FYI** — no action, might-need-later → **Archive**.
   - **Reading** — an article / long read → suggest forwarding to `rss+readlater@mohseni.io`, then archive.
   - **Someday** — not now, maybe never → move to `Someday`.

4. **Present the digest**:
   - **⚡ Action** (to pin) — sender · subject · what's needed
   - **⏳ Waiting / defer** — with a suggested snooze date
   - **📥 Archived as reference** — one line, grouped by type, with counts
   - **🗑 Spam false-positives** — only if any look legitimate

5. **Process toward zero** (do the mechanical sort; ask before anything ambiguous):
   - **Pin** the Action items (`mcp__fastmail__pin_email` or `bulk_pin`).
   - **Archive** the Reference/FYI items (`mcp__fastmail__bulk_move` to Archive).
   - Leave Waiting / Someday items; report the suggested snooze/move for the user to confirm.
   - End state: the inbox holds only live, pinned action items (ideally a handful) — triaged to zero.

## Rules

- Read full content before classifying — don't judge by subject alone.
- When unsure about archiving something, **leave it and flag it** — never bury a real action.
- Never auto-delete; **archive** (reversible) is the default for reference.
- Don't touch Spam except to flag false positives.
- Be concise. If >30 unread, group by sender/category, process the clear ones, and list the rest for a decision.
- The pinned set is the Next-Actions list; the canonical view is the `is:flagged` saved search.
- This is the daily pass. The **weekly review** (~20–30 min, calendared) is separate: re-read pinned actions, skim `Someday` + Snoozed, skim Miniflux.
