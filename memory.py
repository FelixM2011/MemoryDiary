#!/usr/bin/env python3
"""Memory Tagebuch — append one timestamped entry to a per-chat Markdown journal.

Usage:
    memory.py -c CHAT_ID [-d DATA_DIR] [-y|--yearly] message word(s)...

CHAT-ID may be negative (Telegram group ids start with '-'); pass it as a bare
token after -c, e.g.:  -c "-1001234567890"
Data dir precedence: --data-dir > $MEMORY_TAGEBUCH_DIR > ~/.hermes/workspace/memory_data.
Exit 0 silently on empty input (idempotent). Stdlib only, no API key required.
"""
import os
import sys
from datetime import datetime


def default_data_dir() -> str:
    env = os.environ.get("MEMORY_TAGEBUCH_DIR", "").strip()
    if env:
        return env
    home = os.path.expanduser("~")
    return f"{home}/.hermes/workspace/memory_data"


def parse_args(argv):
    """Small hand parser so negative chat ids are not mistaken for options."""
    opts = {"chat_id": None, "data_dir": None, "yearly": False}
    msg_words = []
    i, n = 0, len(argv)

    def take_value(flag):
        nonlocal i
        if argv[i] == flag:  # "-c VALUE" form
            if i + 1 >= n:
                raise SystemExit(f"error: {flag} needs a value")
            val, i = argv[i + 1], i + 2
        else:  # "--flag=VALUE" form (caller already checked the prefix)
            val, i = argv[i][len(flag) + 1:], i + 1
        return val or None

    while i < n:
        a = argv[i]
        matched = False
        for flag in ("-c", "--chat-id"):
            if a == flag or (a.startswith(flag + "=") and len(a) > len(flag)):
                val = take_value(flag)
                opts["chat_id"] = val or None  # keep negative ids exactly as given
                matched = True
                break
        if not matched:
            for flag in ("-d", "--data-dir"):
                if a == flag or (a.startswith(flag + "=") and len(a) > len(flag)):
                    opts["data_dir"] = take_value(flag)
                    matched = True
                    break
        if not matched:
            if a in ("-y", "--yearly"):
                opts["yearly"] = True
                i += 1
            elif a in ("-h", "--help"):
                print(__doc__.strip())
                raise SystemExit(0)
            else:
                msg_words.append(a)
                i += 1

    return opts, " ".join(msg_words).strip()


def save_message(chat_id, message, data_dir, yearly):
    """Append exactly one timed entry to {data_dir}[/{YYYY}]/{chat_id}.md."""
    if not chat_id or not message:
        return  # idempotent: never duplicate entries on empty input

    base = data_dir.rstrip("/")
    os.makedirs(base, exist_ok=True)
    year = datetime.now().strftime("%Y")
    sub = f"{base}/{year}" if yearly else base
    os.makedirs(sub, exist_ok=True)

    file_path = f"{sub}/{chat_id}.md"
    fresh = not os.path.exists(file_path) or os.path.getsize(file_path) == 0
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M]")
    text = message.replace("\\n", "\n")

    with open(file_path, "a", encoding="utf-8") as f:
        if fresh:
            safe_id = chat_id.replace("/", "-")
            f.write(f"# Memory Tagebuch — {safe_id}\n\n")
        entry = f"\n{timestamp}\n{text}\n\n[GESPEICHERT]\n\n"
        f.write(entry)

    print(f"Memory saved for chat {chat_id}")


def main():
    opts, message = parse_args(sys.argv[1:])
    if not opts["chat_id"]:
        print("error: missing --chat-id / -c (negative ids are fine, e.g. -c \"-100...\" or --chat-id=-100...)", file=sys.stderr)
        raise SystemExit(2)
    data_dir = opts["data_dir"] or default_data_dir()
    save_message(opts["chat_id"], message, data_dir, opts["yearly"])


if __name__ == "__main__":
    main()
