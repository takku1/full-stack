"""Small shared to-do service: stdlib only, SQLite storage.

Run: python app.py --port PORT --db PATH
"""
import argparse
import hashlib
import json
import re
import secrets
import sqlite3
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MAX_BODY = 64 * 1024
MAX_TITLE = 500

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token_hash TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS lists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_id INTEGER NOT NULL REFERENCES users(id),
    title TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS lists_owner ON lists(owner_id);
"""


class Store:
    """Owns all persistent state. One connection, serialized by a lock."""

    def __init__(self, path):
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.lock = threading.Lock()
        with self.lock, self.db:
            self.db.executescript(SCHEMA)

    @staticmethod
    def _hash(token):
        return hashlib.sha256(token.encode()).hexdigest()

    def create_user(self):
        token = secrets.token_urlsafe(32)
        with self.lock, self.db:
            cur = self.db.execute(
                "INSERT INTO users (token_hash) VALUES (?)", (self._hash(token),))
            return cur.lastrowid, token

    def user_for_token(self, token):
        with self.lock:
            row = self.db.execute(
                "SELECT id FROM users WHERE token_hash = ?", (self._hash(token),)
            ).fetchone()
        return row[0] if row else None

    def create_list(self, owner_id, title):
        with self.lock, self.db:
            cur = self.db.execute(
                "INSERT INTO lists (owner_id, title) VALUES (?, ?)", (owner_id, title))
            return cur.lastrowid

    def lists_for(self, owner_id):
        with self.lock:
            rows = self.db.execute(
                "SELECT id, title FROM lists WHERE owner_id = ? ORDER BY id",
                (owner_id,)).fetchall()
        return [{"id": r[0], "title": r[1]} for r in rows]

    def get_list(self, owner_id, list_id):
        with self.lock:
            row = self.db.execute(
                "SELECT id, title FROM lists WHERE id = ? AND owner_id = ?",
                (list_id, owner_id)).fetchone()
        return {"id": row[0], "title": row[1]} if row else None


class Handler(BaseHTTPRequestHandler):
    store = None  # set in main()
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):  # no tokens/paths in logs; keep quiet
        pass

    def _send(self, status, body):
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _body(self):
        """Parse the JSON object body; returns None after sending an error."""
        try:
            n = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            n = -1
        if n < 0 or n > MAX_BODY:
            self._send(400, {"error": "bad request"})
            return None
        raw = self.rfile.read(n) if n else b""
        try:
            obj = json.loads(raw or b"{}")
        except ValueError:
            obj = None
        if not isinstance(obj, dict):
            self._send(400, {"error": "body must be a JSON object"})
            return None
        return obj

    def _user(self):
        """Return the caller's user id, or send 401 and return None."""
        m = re.fullmatch(r"Bearer (\S+)", self.headers.get("Authorization", ""))
        uid = self.store.user_for_token(m.group(1)) if m else None
        if uid is None:
            self._send(401, {"error": "unauthorized"})
        return uid

    def do_POST(self):
        path = self.path.split("?")[0]
        if path == "/users":
            if self._body() is None:
                return
            uid, token = self.store.create_user()
            return self._send(201, {"id": uid, "token": token})
        if path == "/lists":
            uid = self._user()
            if uid is None:
                return
            body = self._body()
            if body is None:
                return
            title = body.get("title")
            if not isinstance(title, str) or not title.strip() or len(title) > MAX_TITLE:
                return self._send(400, {"error": "title must be a non-empty string"})
            return self._send(201, {"id": self.store.create_list(uid, title)})
        self._send(404, {"error": "not found"})

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/lists" or re.fullmatch(r"/lists/\d+", path):
            uid = self._user()
            if uid is None:
                return
            if path == "/lists":
                return self._send(200, {"lists": self.store.lists_for(uid)})
            item = self.store.get_list(uid, int(path.rsplit("/", 1)[1]))
            if item is None:
                return self._send(404, {"error": "not found"})
            return self._send(200, item)
        self._send(404, {"error": "not found"})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, required=True)
    ap.add_argument("--db", required=True)
    args = ap.parse_args()
    Handler.store = Store(args.db)
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
