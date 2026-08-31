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

**1. Is the server already running?**

```bash
curl -s -o /dev/null --max-time 1 http://localhost:8787/
```

**2. If not, start it** from this skill's directory:

```bash
nohup python3 server.py > server.log 2>&1 &
```

Give it ~1.5s to bind the port.

**3. Open the file**, URL-encoding the absolute path:

```bash
ENC=$(python3 -c 'import sys,urllib.parse;print(urllib.parse.quote(sys.argv[1]))' "/abs/path/to/file.md")
open "http://localhost:8787/?file=$ENC"      # macOS
xdg-open "http://localhost:8787/?file=$ENC"  # Linux
```

Omit `?file=` to open the editor's own file picker.

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
