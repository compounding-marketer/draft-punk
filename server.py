#!/usr/bin/env python3
"""Local Markdown editor server.

Serves an in-browser editor that can open, edit, and save any .md file
anywhere on this machine. No dependencies beyond the stdlib.
Binds to 127.0.0.1 only — never reachable from the network.

Endpoints:
  GET  /                      -> editor UI (index.html)
  GET  /api/browse?dir=PATH   -> directory listing (folders + md files)
  GET  /api/recent            -> recently opened files
  GET  /api/file?path=PATH    -> {path, content}
  POST /api/save              -> body {path, content}; writes file to disk
"""

import json
import os
import pathlib
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

APP_DIR = pathlib.Path(__file__).resolve().parent
HOME = pathlib.Path.home()
PORT = 8787
EXTS = (".md", ".markdown", ".mdx", ".txt")
RECENT_FILE = APP_DIR / "recent.json"
ALLOWED_HOSTS = {f"localhost:{PORT}", f"127.0.0.1:{PORT}"}


def safe_resolve(path_str: str) -> pathlib.Path:
    """Resolve a client-supplied file path; only markdown/text files are allowed."""
    if not path_str:
        raise PermissionError("empty path")
    p = pathlib.Path(os.path.expanduser(path_str)).resolve()
    if p.suffix.lower() not in EXTS:
        raise PermissionError(f"only {'/'.join(EXTS)} files are editable: {path_str}")
    return p


def load_recent():
    try:
        return json.loads(RECENT_FILE.read_text())
    except Exception:
        return []


def touch_recent(path: pathlib.Path):
    recent = [r for r in load_recent() if r["path"] != str(path)]
    recent.insert(0, {"path": str(path), "name": path.name})
    RECENT_FILE.write_text(json.dumps(recent[:30], indent=1))


STICKY_FILE = APP_DIR / "stickies.json"


def load_stickies():
    """All sticky notes, keyed by the document they belong to.

    Kept in this app's folder rather than beside the user's files, so opening a
    document never leaves stray sidecar files in their directories.
    """
    try:
        return json.loads(STICKY_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError):
        return {}


def save_stickies(data):
    STICKY_FILE.write_text(json.dumps(data, indent=1), encoding="utf-8")


def locate(name: str, size: int):
    """Find where a dropped file lives, so Recent and Save-by-path still work.

    Browsers hand a dropped file's name but not its path. We look in the usual
    places, newest first, and require an exact size match to avoid false hits.
    """
    if not name or name.startswith(".") or "/" in name:
        return None
    roots = [HOME / d for d in ("Downloads", "Desktop", "Documents")] + [HOME]
    seen = set()
    for root in roots:
        if not root.is_dir() or root in seen:
            continue
        seen.add(root)
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames
                           if not d.startswith(".") and d not in
                           {"Library", "node_modules", "__pycache__", ".git"}]
            if name in filenames:
                p = pathlib.Path(dirpath) / name
                try:
                    if size < 0 or p.stat().st_size == size:
                        return str(p)
                except OSError:
                    continue
    return None


def browse(dir_str: str):
    d = pathlib.Path(os.path.expanduser(dir_str or "~")).resolve()
    if not d.is_dir():
        d = d.parent if d.parent.is_dir() else HOME
    dirs, files = [], []
    try:
        for entry in sorted(d.iterdir(), key=lambda p: p.name.lower()):
            if entry.name.startswith("."):
                continue
            try:
                if entry.is_dir():
                    dirs.append(entry.name)
                elif entry.suffix.lower() in EXTS:
                    files.append({"name": entry.name, "mtime": entry.stat().st_mtime})
            except (PermissionError, OSError):
                continue
    except PermissionError:
        return {"dir": str(d), "parent": str(d.parent), "home": str(HOME),
                "dirs": [], "files": [], "error": "macOS denied access to this folder"}
    return {"dir": str(d), "parent": str(d.parent) if d != d.parent else None,
            "home": str(HOME), "dirs": dirs, "files": files}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # keep server logs quiet

    def _send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _host_ok(self):
        # Reject DNS-rebinding style requests: only true localhost origins allowed.
        if self.headers.get("Host") not in ALLOWED_HOSTS:
            self._send(403, {"error": "forbidden host"})
            return False
        return True

    def do_GET(self):
        if not self._host_ok():
            return
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)

        if parsed.path == "/":
            html = (APP_DIR / "index.html").read_bytes()
            self._send(200, html, "text/html; charset=utf-8")
        elif parsed.path == "/api/browse":
            self._send(200, browse(qs.get("dir", [""])[0]))
        elif parsed.path == "/api/stickies":
            key = qs.get("path", [""])[0]
            self._send(200, {"notes": load_stickies().get(key, [])})
        elif parsed.path == "/api/locate":
            name = qs.get("name", [""])[0]
            try:
                size = int(qs.get("size", ["-1"])[0])
            except ValueError:
                size = -1
            self._send(200, {"path": locate(name, size)})
        elif parsed.path == "/api/recent":
            self._send(200, {"files": [r for r in load_recent()
                                       if pathlib.Path(r["path"]).exists()]})
        elif parsed.path == "/api/file":
            raw = qs.get("path", [""])[0]
            try:
                p = safe_resolve(raw)
                content = p.read_text(encoding="utf-8")
                touch_recent(p)
                self._send(200, {"path": str(p), "content": content})
            except PermissionError as e:
                self._send(403, {"error": str(e)})
            except FileNotFoundError:
                self._send(404, {"error": f"not found: {raw}"})
            except OSError as e:
                self._send(403, {"error": f"cannot read {raw}: {e}"})
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        if not self._host_ok():
            return
        if self.path == "/api/stickies":
            length = int(self.headers.get("Content-Length", 0))
            try:
                body = json.loads(self.rfile.read(length))
                data = load_stickies()
                key = body["path"]
                notes = body.get("notes") or []
                if notes:
                    data[key] = notes
                else:
                    data.pop(key, None)
                save_stickies(data)
                self._send(200, {"ok": True, "count": len(notes)})
            except Exception as e:
                self._send(400, {"error": str(e)})
            return
        if self.path != "/api/save":
            self._send(404, {"error": "not found"})
            return
        length = int(self.headers.get("Content-Length", 0))
        try:
            body = json.loads(self.rfile.read(length))
            p = safe_resolve(body["path"])
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(body["content"], encoding="utf-8")
            touch_recent(p)
            self._send(200, {"ok": True, "path": str(p)})
        except PermissionError as e:
            self._send(403, {"error": str(e)})
        except Exception as e:
            self._send(400, {"error": str(e)})


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"md-editor serving on http://localhost:{PORT}")
    server.serve_forever()
