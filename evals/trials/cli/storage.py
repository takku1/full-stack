"""SQLite state authority and atomic batch writing."""
import sqlite3
from contextlib import closing


def initialize(connection):
    connection.execute('CREATE TABLE IF NOT EXISTS inventory (name TEXT PRIMARY KEY NOT NULL, quantity INTEGER NOT NULL CHECK(quantity >= 0))')


def apply_batch(path, rows):
    with closing(sqlite3.connect(path)) as connection:
        with connection:
            initialize(connection)
            connection.executemany('INSERT INTO inventory(name,quantity) VALUES (?,?) ON CONFLICT(name) DO UPDATE SET quantity=excluded.quantity', rows)


def list_items(path):
    with closing(sqlite3.connect(path)) as connection:
        with connection:
            initialize(connection)
            return connection.execute('SELECT name,quantity FROM inventory ORDER BY name').fetchall()
