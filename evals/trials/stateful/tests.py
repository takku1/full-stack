import argparse
from html import escape
import http.client
from pathlib import Path
import platform
import re
import sqlite3
import subprocess
import sys
import tempfile
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--phase', choices=['initial', 'followup'], default='followup')
args = parser.parse_args()
print(f'ENV Python={sys.version} platform={platform.platform()} SQLite={sqlite3.sqlite_version}', flush=True)
print(f'PHASE {args.phase}', flush=True)


class Server:
    def __init__(self, db, serial):
        self.log = open(ROOT / f'{args.phase}-server-{serial}.log', 'w', encoding='utf-8')
        self.process = subprocess.Popen([sys.executable, '-u', str(ROOT / 'app.py'), '--db', str(db), '--port', '0'], stdout=subprocess.PIPE, stderr=self.log, text=True)
        line = self.process.stdout.readline().strip()
        assert line.startswith('LISTENING http://127.0.0.1:'), line
        self.port = int(line.rsplit(':', 1)[1])
        print(f'START pid={self.process.pid} {line}', flush=True)

    def request(self, method, path, fields=None):
        connection = http.client.HTTPConnection('127.0.0.1', self.port, timeout=5)
        data = urlencode(fields) if fields is not None else None
        connection.request(method, path, data, {'Content-Type': 'application/x-www-form-urlencoded'} if data is not None else {})
        response = connection.getresponse()
        status, location, body = response.status, response.getheader('Location'), response.read().decode('utf-8')
        connection.close()
        print(f'HTTP {method} {path} fields={fields!r} -> {status} Location={location!r} bytes={len(body.encode())}', flush=True)
        return status, location, body

    def stop(self):
        self.process.terminate()
        self.process.wait(timeout=10)
        self.process.stdout.close()
        self.log.close()
        print(f'STOP pid={self.process.pid} exit={self.process.returncode}', flush=True)


def check(condition, label):
    assert condition, label
    print(f'PASS {label}', flush=True)


with tempfile.TemporaryDirectory(prefix='notes-check-', dir=ROOT) as folder:
    db = Path(folder) / 'test.sqlite3'
    server = Server(db, 1)
    try:
        status, _, html = server.request('GET', '/')
        check(status == 200 and 'No notes yet.' in html and 'method="post" action="/notes"' in html, 'empty page and add form')
        for fields in ({'title': ' ', 'body': 'valid'}, {'title': 'valid', 'body': '\t'}, {}):
            status, _, html = server.request('POST', '/notes', fields)
            check(status == 400 and 'must both contain nonblank text' in html, 'blank fields visible 400')
        title, body = '<script>alert("title")</script>', '<img src=x onerror="alert(1)"> & body'
        status, location, _ = server.request('POST', '/notes', {'title': title, 'body': body})
        check(status == 303 and location == '/', 'creation redirects')
        server.request('POST', '/notes', {'title': 'Independent second', 'body': 'Survives first deletion'})
        status, _, html = server.request('GET', '/')
        ids = re.findall(r'action="/notes/(\d+)/delete"', html)
        check(len(ids) == 2 and ids[0] != ids[1], 'two independent identities and delete forms')
        check(escape(title) in html and escape(body) in html and title not in html and body not in html, 'stored HTML escaped')
        status, _, html = server.request('POST', '/notes/999999/delete', {})
        check(status == 404 and 'Note not found.' in html, 'absent deletion visible 404')
        status, location, _ = server.request('POST', f'/notes/{ids[0]}/delete', {})
        check(status == 303 and location == '/', 'deletion redirects')
        _, _, html = server.request('GET', '/')
        check(escape(title) not in html and 'Independent second' in html, 'delete affects only selected note')
        status, _, html = server.request('POST', f'/notes/{ids[0]}/delete', {})
        check(status == 404 and 'Note not found.' in html, 'repeated delete visible 404')
        if args.phase == 'initial':
            status, _, _ = server.request('POST', '/notes', {'title': 'L' * 81, 'body': 'Initially allowed'})
            check(status == 303, 'initial policy accepts long title')
        else:
            for size, expected in ((80, 303), (81, 400)):
                status, _, html = server.request('POST', '/notes', {'title': 'T' * size, 'body': 'Length boundary'})
                check(status == expected and (size == 80 or 'at most 80 characters' in html), f'title length {size}')
            _, _, html = server.request('GET', '/')
            check('T' * 81 not in html, 'rejected title never persisted')
    finally:
        server.stop()
    if args.phase == 'followup':
        # Explicit legacy fixture: old valid data, not a substitute for HTTP creation tests.
        connection = sqlite3.connect(db)
        with connection:
            legacy = connection.execute('INSERT INTO notes(title, body) VALUES (?, ?)', ('Legacy-' + 'L' * 81, 'Existing body')).lastrowid
        connection.close()
        print(f'FIXTURE existing pre-policy title inserted id={legacy}', flush=True)
    server = Server(db, 2)
    try:
        status, _, html = server.request('GET', '/')
        check(status == 200 and 'Independent second' in html and escape(title) not in html, 'create and delete persist after real process restart')
        if args.phase == 'followup':
            check('Legacy-' + 'L' * 81 in html, 'legacy long title displays after restart')
            status, location, _ = server.request('POST', f'/notes/{legacy}/delete', {})
            check(status == 303 and location == '/', 'legacy long title remains deletable')
            _, _, html = server.request('GET', '/')
            check('Legacy-' not in html and 'Independent second' in html, 'legacy deletion localized to selected identity')
    finally:
        server.stop()
print('ALL CHECKS PASSED; browser interaction UNEXECUTED (no browser tool exposed).', flush=True)
