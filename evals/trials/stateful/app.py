import argparse
from html import escape
from http.server import BaseHTTPRequestHandler, HTTPServer
import re
from urllib.parse import parse_qs

from notes import InvalidNote, MissingNote, Notes


def page(store, error='', title='', body=''):
    cards = ''.join(
        f'<article><h2>{escape(t)}</h2><pre>{escape(b)}</pre>'
        f'<form method="post" action="/notes/{i}/delete"><button>Delete note {i}</button></form></article>'
        for i, t, b in store.list()
    )
    return ('<!doctype html><html lang="en"><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width"><title>Local notes</title>'
            '<style>body{max-width:48rem;margin:2rem auto;padding:0 1rem;font:18px system-ui}'
            'label{display:block;margin:1rem 0}input,textarea{display:block;width:100%;box-sizing:border-box}'
            'pre{white-space:pre-wrap;overflow-wrap:anywhere}article{border-top:1px solid #aaa;margin-top:2rem}'
            '[role=alert]{color:#a00}</style><body><h1>Local notes</h1>'
            f'<p role="alert">{escape(error)}</p>'
            '<form method="post" action="/notes">'
            f'<label>Title<input name="title" required value="{escape(title, quote=True)}"></label>'
            f'<label>Body<textarea name="body" required>{escape(body)}</textarea></label>'
            '<button>Add note</button></form><section aria-label="Saved notes">'
            f'{cards or "<p>No notes yet.</p>"}</section></body></html>')


def handler_for(store):
    class Handler(BaseHTTPRequestHandler):
        def render(self, status=200, error='', title='', body=''):
            data = page(store, error, title, body).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            self.render() if self.path == '/' else self.render(404, 'Page not found.')

        def do_POST(self):
            if self.path == '/notes':
                try:
                    length = int(self.headers.get('Content-Length', '0'))
                    if length < 0:
                        raise ValueError()
                    fields = parse_qs(self.rfile.read(length).decode('utf-8'), keep_blank_values=True)
                except (ValueError, UnicodeDecodeError):
                    self.render(400, 'Invalid form data.')
                    return
                title = fields.get('title', [''])[0]
                body = fields.get('body', [''])[0]
                try:
                    store.create(title, body)
                except InvalidNote as error:
                    self.render(400, str(error), title, body)
                    return
            else:
                match = re.fullmatch(r'/notes/([1-9][0-9]*)/delete', self.path)
                if not match:
                    self.render(404, 'Page not found.')
                    return
                try:
                    store.delete(int(match[1]))
                except (MissingNote, OverflowError):
                    self.render(404, 'Note not found.')
                    return
            self.send_response(303)
            self.send_header('Location', '/')
            self.send_header('Content-Length', '0')
            self.end_headers()
    return Handler


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', default='notes.sqlite3')
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    server = HTTPServer(('127.0.0.1', args.port), handler_for(Notes(args.db)))
    print(f'LISTENING http://127.0.0.1:{server.server_port}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
