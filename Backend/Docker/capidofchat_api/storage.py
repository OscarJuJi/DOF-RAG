"""Persistent local accounts, sessions, and document vectors."""

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@contextmanager
def database():
    directory = Path(os.getenv("DATA_DIR", "./data"))
    directory.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(directory / "dof.sqlite3", timeout=30)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys=ON")
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def initialize_database():
    with database() as connection:
        connection.execute("PRAGMA journal_mode=WAL")
        connection.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                email TEXT PRIMARY KEY, password_hash TEXT NOT NULL,
                first_name TEXT NOT NULL, paternal_name TEXT NOT NULL DEFAULT '',
                maternal_name TEXT NOT NULL DEFAULT '', phone TEXT NOT NULL DEFAULT '',
                department TEXT NOT NULL DEFAULT '',
                notifications INTEGER NOT NULL DEFAULT 1,
                role TEXT NOT NULL DEFAULT 'user'
            );
            CREATE TABLE IF NOT EXISTS sessions (
                token_hash TEXT PRIMARY KEY,
                email TEXT NOT NULL REFERENCES users(email) ON DELETE CASCADE,
                expires_at REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS resets (
                email TEXT PRIMARY KEY REFERENCES users(email) ON DELETE CASCADE,
                code_hash TEXT NOT NULL, expires_at REAL NOT NULL,
                attempts INTEGER NOT NULL DEFAULT 0,
                token_hash TEXT
            );
            CREATE TABLE IF NOT EXISTS attempts (
                bucket TEXT NOT NULL, occurred_at REAL NOT NULL
            );
            CREATE INDEX IF NOT EXISTS attempts_bucket ON attempts(bucket, occurred_at);
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY, name TEXT NOT NULL, path TEXT NOT NULL,
                model TEXT NOT NULL, pages INTEGER NOT NULL, indexed_at TEXT NOT NULL,
                summary TEXT
            );
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY,
                document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                page INTEGER NOT NULL, content TEXT NOT NULL, vector BLOB NOT NULL
            );
        """)
