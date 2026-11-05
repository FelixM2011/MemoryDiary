---
name: memory-diary
category: productivity
version: 1.0.0
author: Felix Morocutti (https://github.com/FelixM2011)
description: Appends chat messages, memories and life experiences to per-chat Markdown daily journals on disk.
metadata:
  hermes:
    tags: [memory, journal, logs, persistence, experience]
    related_skills: []
---

## When to Use
Use whenever the agent should durably record what was said or experienced in a chat — e.g. automatically logging every message from specific groups ("save this to memory"), post-mortems of experiences, or answering "what did we talk about on date X?". The script appends one timestamped entry per message to a per-chat Markdown journal file (optional yearly rotation via `--yearly`), then confirms with `[GESPEICHERT]`.

# Memory Tagebuch 📔🇩🇪

Local, keyless experience logger. Every call appends exactly one timed entry to `{data_dir}/{chat_id}.md` by default (or `{data_dir}/YYYY/{chat_id}.md` with `--yearly`). No cloud, no API — state lives in plain Markdown files that humans can open and grep directly.

## Running
```bash
python3 <this-skill>/memory.py --chat-id "<chat or group id>" \
    [--data-dir DIR] [--yearly] "--message text... additional words..."
```
- The **message is everything after the options**, joined with single spaces; literal newlines may be passed as `\n`.
- Data dir precedence: `--data-dir` flag > `$MEMORY_TAGEBUCH_DIR` env var > default `~/.hermes/workspace/memory_data`.
- Stdlib only, no API key required.

Examples:
```bash
python3 memory.py --chat-id "-1001234567890" --yearly "Guten Morgen - heute Testlauf"
MEMORY_TAGEBUCH_DIR=/var/lib/tagebuch python3 memory.py --chat-id 42 "Lebenserfahrung: erst planen, dann schrauben"
```

## Return contract (agent side)
- On success prints `Memory saved for chat <chat_id>` — in automated group-logging mode the agent confirms with a single `[GESPEICHERT]` line and nothing else. Silent on empty input by design (idempotent re-triggers write no duplicates).

## Output format (appended per file)
```markdown
[YYYY-MM-DD HH:MM]
<message text>

[GESPEICHERT]
```
Newest entries at the bottom of each file. `grep "2026-11" <file>.md` finds a date range instantly — no database needed; journal files can be archived as plain text forever and searched locally (see README).

## Notes / pitfalls
- Filesystem writes only — **never** store secrets/tokens in journals; treat every file as human-readable data.
- Timestamps are server-local time (`datetime.now()`), not UTC: fine for a personal journal, but state it in any aggregated report.
- Assumes one writer per chat id (a single agent turn loop); under heavy multi-process usage you would need an explicit file lock — out of scope by design.
