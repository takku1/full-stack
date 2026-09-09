import sqlite3


class InvalidNote(ValueError):
    pass


class MissingNote(LookupError):
    pass


class Notes:
    def __init__(self, path):
        self.path = path
        self._execute('CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, body TEXT NOT NULL)')

    def _execute(self, sql, args=(), fetch=False):
        connection = sqlite3.connect(self.path)
        try:
            with connection:
                cursor = connection.execute(sql, args)
                return cursor.fetchall() if fetch else (cursor.lastrowid, cursor.rowcount)
        finally:
            connection.close()

    def create(self, title, body):
        title, body = title.strip(), body.strip()
        if not title or not body:
            raise InvalidNote('Title and body must both contain nonblank text.')
        if len(title) > 80:
            raise InvalidNote('Title must be at most 80 characters.')
        return self._execute('INSERT INTO notes(title, body) VALUES (?, ?)', (title, body))[0]

    def list(self):
        return self._execute('SELECT id, title, body FROM notes ORDER BY id', fetch=True)

    def delete(self, note_id):
        if self._execute('DELETE FROM notes WHERE id = ?', (note_id,))[1] == 0:
            raise MissingNote('Note not found.')
