---
name: draft-punk
description: |
  Open, read, and edit Markdown files in Draft Punk — a local formatted
  Markdown viewer and editor served on localhost. Use when the user says
  "open this in Draft Punk", "show me this markdown formatted", "view this
  .md nicely", "let me edit this markdown visually", or otherwise wants a
  rendered, editable view of a Markdown file instead of raw text in the
  terminal. Requires Python 3 (no other dependencies).
---

# Draft Punk

Serves a formatted, editable view of any Markdown file on the local disk at
`http://localhost:8787`. Edits save back to the original file.

## Opening a file

**If `Draft Punk.app` is installed (macOS), use it — one command does everything:**

```bash
open -a "Draft Punk.app" "/abs/path/to/file.md"
```

It starts the server if needed and opens that file. Prefer this: on macOS the app
owns the permission grant that lets the server read files in Documents, Desktop
and Downloads.

**Otherwise**, start the server and open the URL:

```bash
# 1. already running?
curl -s -o /dev/null --max-time 1 http://localhost:8787/

# 2. if not, start it — see the macOS warning below
nohup python3 server.py > server.log 2>&1 &   # give it ~1.5s to bind

# 3. open the file
ENC=$(python3 -c 'import sys,urllib.parse;print(urllib.parse.quote(sys.argv[1]))' "/abs/path/to/file.md")
open "http://localhost:8787/?file=$ENC"      # macOS
xdg-open "http://localhost:8787/?file=$ENC"  # Linux
```

Omit `?file=` to open the editor's own file picker.

> **macOS permissions.** A server started detached from an agent's shell can lose
> access to protected folders (Documents, Desktop, Downloads) and then fail every
> read with `PermissionError: [Errno 1] Operation not permitted` — while still
> holding the port, so it looks alive. Use the `open -a` form above, or have the
> user run `python3 server.py` in the foreground from their own Terminal, so a
> real app owns the permission. This does not affect Linux.

## HTTP API

Useful if you want to read or write Markdown programmatically rather than
opening a browser.

| Endpoint | Purpose |
|---|---|
| `GET /api/file?path=PATH` | `{path, content}` for one file |
| `GET /api/browse?dir=PATH` | folders + `.md` files in a directory |
| `GET /api/recent` | recently opened files |
| `POST /api/save` | body `{path, content}` — writes to disk |

## Troubleshooting

**The port is held but nothing responds.** A stale server process can keep
listening after losing filesystem permissions, and the launcher won't replace
it because the port looks occupied. Kill and restart:

```bash
kill -9 $(lsof -ti:8787); nohup python3 server.py > server.log 2>&1 &
```

## No-server alternative

`share/draft-punk.html` is a standalone build — open it directly in Chrome,
Edge, Arc, or Brave. No server, no Python, works on any OS. Saving back to the
original file uses the File System Access API, so Safari and Firefox will
download a copy instead.
