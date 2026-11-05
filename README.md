# Memory diary 📔

A [Hermes agent skill](https://hermes-agent.nousresearch.com/docs) that durably records chat messages, memories and life experiences into plain-Markdown daily journals on disk — one file per chat (or per year + chat), zero cloud, zero API key. Built for the "save every message from this group / remember this experience" workflow: the agent appends exactly one timestamped entry per event and confirms with `[GESPEICHERT]`.

> Author: Felix [Morocutti](https://github.com/FelixM2011) · License: [MIT](LICENSE)

## What it does

- Appends a `[YYYY-MM-DD HH:MM]` timestamped entry to `~/.hermes/workspace/memory_data/<chat_id>.md`
- **One file per chat id** (Telegram group ids with leading `-` work out of the box — no argparse traps), newest entries at file bottom
- Optional yearly rotation (`--yearly`) into `<data_dir>/YYYY/<chat_id>.md` for clean annual archives
- Overridable storage location: `--data-dir DIR` flag > `$MEMORY_TAGEBUCH_DIR` env var > default path
- `\n` inside the message becomes a real newline on disk; first write stamps a per-chat file header
- Idempotent & silent on empty input, so cron/pattern re-triggers never duplicate entries

## Install (Hermes)

```bash
git clone https://github.com/FelixM2011/MemoryTagebuch.git ~/.hermes/skills/memory-tagebuch
chmod +x ~/.hermes/skills/memory-tagebuch/memory.py
```

Required toolsets: none — `memory.py` is stdlib-only Python 3. Tagged in the skill frontmatter, so Hermes picks it up directly.

## Usage

Interactively — ask e.g.: „*Speichere unsere Konversation heute ins Tagebuch*" and the agent runs:

```bash
python3 ~/.hermes/skills/memory-tagebuch/memory.py \
    -c "<chat or group id>" [--data-dir DIR] [--yearly] "message text… additional words"
```

As an automated rule / cron hook for a specific group (e.g. after every incoming message): call the script with the fixed chat id, then answer `[GESPEICHERT]` — nothing else. The stdout contract is exactly: `Memory saved for chat <id>` on success or silent exit 0 on empty input.

## Output format (per journal file, appended)

```markdown
# Memory Tagebuch — -100384829019   ← written once on first save

[2026-11-05 14:32]
Guten Morgen Martin - heute Testlauf

[GESPEICHERT]
```

See [`references/sample-journal.md`](references/sample-journal.md) for a real sample produced by this script. Because journals are plain text you can archive them forever (`git`, `rsync` to any backup target) and search locally:

```bash
grep -n "2026-11" memory_data/-100384829019.md | head   # find a date range
```

## Notes & pitfalls

- **Never store secrets or tokens in journals** — every file is plain, human-readable text. For sensitive chats encrypt the parent volume instead.
- Timestamps are server-local time (`datetime.now()`), not UTC: fine for a personal journal, but state it if you aggregate reports across machines.
- Assumes one writer per chat id (a single agent turn loop). Under heavy multi-process access you would need an explicit file lock — deliberately out of scope by design.
