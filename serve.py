#!/usr/bin/env python3
"""Optional local preview server with HTTP Range support for audio seeking.

GitHub Pages deployment does not use this script; run `python3 -m http.server` instead.
"""

from __future__ import annotations

import json
import os
import re
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent
PORT = 8765
_RANGE_RE = re.compile(r"bytes=(\d+)-(\d*)")
NOTEBOOK_PATH = ROOT / "notebook_ru.txt"


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self._range_length: int | None = None
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/notebook":
            content = NOTEBOOK_PATH.read_text(encoding="utf-8") if NOTEBOOK_PATH.exists() else ""
            body = json.dumps({"content": content, "lang": "ru"}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/api/notebook":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", 0))
        payload = json.loads(self.rfile.read(length).decode("utf-8"))
        content = payload.get("content", "")
        NOTEBOOK_PATH.write_text(content, encoding="utf-8")
        body = json.dumps({"ok": True, "lang": "ru"}, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_head(self):
        path = self.translate_path(self.path)
        if os.path.isdir(path):
            return super().send_head()

        if not os.path.isfile(path):
            self.send_error(404, "File not found")
            return None

        ctype = self.guess_type(path)
        try:
            file_obj = open(path, "rb")
        except OSError:
            self.send_error(404, "File not found")
            return None

        fs = os.fstat(file_obj.fileno())
        size = fs.st_size
        range_header = self.headers.get("Range")

        if range_header:
            match = _RANGE_RE.match(range_header.strip())
            if match:
                start = int(match.group(1))
                end = int(match.group(2)) if match.group(2) else size - 1
                end = min(end, size - 1)
                if start >= size or start > end:
                    self.send_error(416, "Requested Range Not Satisfiable")
                    file_obj.close()
                    return None
                length = end - start + 1
                self.send_response(206)
                self.send_header("Content-Type", ctype)
                self.send_header("Accept-Ranges", "bytes")
                self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
                self.send_header("Content-Length", str(length))
                self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
                self.end_headers()
                file_obj.seek(start)
                self._range_length = length
                return file_obj

        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(size))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        return file_obj

    def copyfile(self, source, outputfile):
        if self._range_length is not None:
            remaining = self._range_length
            while remaining > 0:
                chunk = source.read(min(64 * 1024, remaining))
                if not chunk:
                    break
                outputfile.write(chunk)
                remaining -= len(chunk)
            self._range_length = None
            return
        super().copyfile(source, outputfile)

    def log_message(self, fmt: str, *args) -> None:
        print(f"[{self.log_date_time_string()}] {fmt % args}")


def main() -> None:
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Serving {ROOT}")
    print(f"Open http://localhost:{PORT}")
    print("Notebook file: notebook_ru.txt (gitignored)")
    server.serve_forever()


if __name__ == "__main__":
    main()
