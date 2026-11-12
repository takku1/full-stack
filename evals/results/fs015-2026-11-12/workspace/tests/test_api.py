"""End-to-end tests: real server subprocess, real HTTP, real restart."""
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.error
import urllib.request

APP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "app.py")


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class ApiTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = os.path.join(self.tmp.name, "t.db")
        self.proc = None
        self.start()

    def tearDown(self):
        self.stop()
        self.tmp.cleanup()

    def start(self):
        self.port = free_port()
        self.proc = subprocess.Popen(
            [sys.executable, APP, "--port", str(self.port), "--db", self.db])
        for _ in range(100):
            try:
                socket.create_connection(("127.0.0.1", self.port), 0.1).close()
                return
            except OSError:
                time.sleep(0.05)
        self.fail("server did not start")

    def stop(self):
        if self.proc:
            self.proc.terminate()
            self.proc.wait(5)
            self.proc = None

    def call(self, method, path, token=None, body=None, raw=None):
        data = raw if raw is not None else (
            json.dumps(body).encode() if body is not None else None)
        req = urllib.request.Request(
            f"http://127.0.0.1:{self.port}{path}", data=data, method=method)
        if token:
            req.add_header("Authorization", f"Bearer {token}")
        try:
            with urllib.request.urlopen(req) as r:
                return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read())

    def user(self):
        s, b = self.call("POST", "/users", body={})
        self.assertEqual(s, 201)
        return b["id"], b["token"]

    def test_user_and_list_flow(self):
        _, t = self.user()
        s, b = self.call("POST", "/lists", t, {"title": "groceries"})
        self.assertEqual(s, 201)
        lid = b["id"]
        s, b = self.call("GET", "/lists", t)
        self.assertEqual((s, [x["id"] for x in b["lists"]]), (200, [lid]))
        s, b = self.call("GET", f"/lists/{lid}", t)
        self.assertEqual((s, b["title"]), (200, "groceries"))

    def test_users_post_without_body(self):
        s, b = self.call("POST", "/users")
        self.assertEqual(s, 201)
        self.assertTrue(b["token"])

    def test_isolation(self):
        _, a = self.user()
        _, b = self.user()
        _, r = self.call("POST", "/lists", a, {"title": "mine"})
        self.assertEqual(self.call("GET", f"/lists/{r['id']}", b)[0], 404)
        self.assertEqual(self.call("GET", "/lists", b), (200, {"lists": []}))
        self.assertEqual(self.call("GET", "/lists/9999", a)[0], 404)

    def test_unauthorized(self):
        for method, path in [("GET", "/lists"), ("GET", "/lists/1"), ("POST", "/lists")]:
            self.assertEqual(self.call(method, path, body={"title": "x"} if method == "POST" else None)[0], 401)
            self.assertEqual(self.call(method, path, "bogus", {"title": "x"} if method == "POST" else None)[0], 401)

    def test_bad_input(self):
        _, t = self.user()
        for body in ({}, {"title": ""}, {"title": 5}, {"title": "  "}):
            self.assertEqual(self.call("POST", "/lists", t, body)[0], 400)
        self.assertEqual(self.call("POST", "/lists", t, raw=b"{nope")[0], 400)
        self.assertEqual(self.call("POST", "/lists", t, raw=b"[1]")[0], 400)

    def test_injection_title_is_inert(self):
        _, t = self.user()
        evil = "x'); DROP TABLE lists;--"
        _, r = self.call("POST", "/lists", t, {"title": evil})
        self.assertEqual(self.call("GET", f"/lists/{r['id']}", t)[1]["title"], evil)

    def test_persistence_across_restart(self):
        uid, t = self.user()
        _, r = self.call("POST", "/lists", t, {"title": "keep"})
        self.stop()
        self.start()
        s, b = self.call("GET", f"/lists/{r['id']}", t)
        self.assertEqual((s, b["title"]), (200, "keep"))
        _, t2 = self.user()  # ids/tokens keep working and stay distinct
        self.assertNotEqual(t, t2)
        self.assertEqual(self.call("GET", "/lists", t2), (200, {"lists": []}))

    def test_token_not_stored_plaintext(self):
        _, t = self.user()
        with open(self.db, "rb") as f:
            self.assertNotIn(t.encode(), f.read())


if __name__ == "__main__":
    unittest.main()
