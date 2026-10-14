"""Resumable edition downloads, page-aware extraction, and local full-text search."""

import hashlib
import json
import os
import re
import sqlite3
import subprocess
import tempfile
from contextlib import contextmanager
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

from .client import API_URL, DofClient, parse_date, validate_id


def now() -> str:
    return datetime.now(UTC).isoformat()


def today() -> date:
    return (datetime.now(UTC) - timedelta(hours=6)).date()


def atomic_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(text, encoding="utf-8", newline="\n")
    temporary.replace(path)


def extract_pdf(path: Path) -> tuple[list[str], list[int], list[int]]:
    info = subprocess.run(
        ["pdfinfo", str(path)], capture_output=True, text=True, check=True, timeout=120
    )
    match = re.search(r"^Pages:\s+(\d+)", info.stdout, re.MULTILINE)
    if not match:
        raise ValueError("Cannot determine PDF page count.")
    page_count = int(match[1])
    output = subprocess.run(
        ["pdftotext", "-layout", "-enc", "UTF-8", str(path), "-"],
        capture_output=True,
        check=True,
        timeout=300,
    ).stdout.decode("utf-8")
    pages = output.split("\f")
    if pages and not pages[-1].strip():
        pages.pop()
    if len(pages) != page_count:
        raise ValueError(f"Extracted {len(pages)} pages but PDF declares {page_count}.")
    ocr_pages = []
    low_text_pages = []
    for index, text in enumerate(pages):
        text = re.sub(r"[\x00-\x08\x0b\x0e-\x1f]", "", text).strip()
        if sum(character.isalnum() for character in text) < 80:
            with tempfile.TemporaryDirectory(prefix="dof-ocr-") as folder:
                image = str(Path(folder) / "page")
                subprocess.run(
                    [
                        "pdftoppm",
                        "-f",
                        str(index + 1),
                        "-l",
                        str(index + 1),
                        "-r",
                        "150",
                        "-singlefile",
                        "-png",
                        str(path),
                        image,
                    ],
                    capture_output=True,
                    check=True,
                    timeout=120,
                )
                recognized = (
                    subprocess.run(
                        ["tesseract", image + ".png", "stdout", "-l", "spa+eng"],
                        capture_output=True,
                        check=True,
                        timeout=180,
                    )
                    .stdout.decode("utf-8")
                    .strip()
                )
            ocr_pages.append(index + 1)
            if len(recognized) > len(text):
                text = recognized
            if sum(character.isalnum() for character in text) < 80:
                low_text_pages.append(index + 1)
        pages[index] = text
    return pages, ocr_pages, low_text_pages


class Archive:
    def __init__(self, root: Path | None = None):
        self.root = (root or Path(os.getenv("DOF_ARCHIVE_DIR", "/archive"))).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / "catalog.sqlite3"
        with self.connection() as db:
            db.executescript("""
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS days (
                    date TEXT PRIMARY KEY, status TEXT NOT NULL, error TEXT,
                    checked_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS editions (
                    id INTEGER PRIMARY KEY, date TEXT NOT NULL, edition TEXT NOT NULL,
                    expected_pages INTEGER NOT NULL DEFAULT 0,
                    status TEXT NOT NULL DEFAULT 'pending', source_url TEXT NOT NULL,
                    pdf_path TEXT, text_path TEXT, sha256 TEXT, text_sha256 TEXT,
                    bytes INTEGER DEFAULT 0, pages INTEGER DEFAULT 0,
                    characters INTEGER DEFAULT 0, ocr_pages TEXT DEFAULT '[]',
                    low_text_pages TEXT DEFAULT '[]', error TEXT, updated_at TEXT
                );
                CREATE INDEX IF NOT EXISTS editions_date ON editions(date);
                CREATE TABLE IF NOT EXISTS pages (
                    id INTEGER PRIMARY KEY, edition_id INTEGER NOT NULL,
                    page INTEGER NOT NULL, content TEXT NOT NULL,
                    UNIQUE(edition_id,page),
                    FOREIGN KEY(edition_id) REFERENCES editions(id)
                );
                CREATE VIRTUAL TABLE IF NOT EXISTS pages_fts USING fts5(
                    content, content='pages', content_rowid='id',
                    tokenize='unicode61 remove_diacritics 2'
                );
                CREATE TRIGGER IF NOT EXISTS pages_ai AFTER INSERT ON pages BEGIN
                    INSERT INTO pages_fts(rowid,content) VALUES(new.id,new.content);
                END;
                CREATE TRIGGER IF NOT EXISTS pages_ad AFTER DELETE ON pages BEGIN
                    INSERT INTO pages_fts(pages_fts,rowid,content)
                    VALUES('delete',old.id,old.content);
                END;
                CREATE TABLE IF NOT EXISTS runs (
                    id INTEGER PRIMARY KEY, start_date TEXT, end_date TEXT,
                    started_at TEXT, finished_at TEXT, status TEXT, error TEXT
                );
            """)

    @contextmanager
    def connection(self):
        db = sqlite3.connect(self.path, timeout=60)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        try:
            with db:
                yield db
        finally:
            db.close()

    def register_edition(self, item: dict):
        identifier = validate_id(int(item["id"]))
        parse_date(item["date"])
        if item["edition"] not in {"MAT", "VES", "EXT"}:
            raise ValueError("Unexpected edition type.")
        with self.connection() as db:
            db.execute(
                "INSERT INTO editions(id,date,edition,expected_pages,source_url) "
                "VALUES(?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET "
                "expected_pages=MAX(editions.expected_pages,excluded.expected_pages)",
                (
                    identifier,
                    item["date"],
                    item["edition"],
                    item.get("expected_pages", 0),
                    f"{API_URL}/documentos/pdf/{identifier}",
                ),
            )

    def save_response(self, name: str, payload: dict):
        atomic_text(
            self.root / "responses" / f"{name}.json",
            json.dumps(payload, ensure_ascii=False),
        )

    def discover_day(self, client: DofClient, day: date, refresh=False):
        value = day.isoformat()
        with self.connection() as db:
            previous = db.execute(
                "SELECT status FROM days WHERE date=?", (value,)
            ).fetchone()
        if previous and previous["status"] != "error" and not refresh and day < today():
            return
        try:
            editions, payload = client.editions(value)
            self.save_response(value + "-editions", payload)
            if not editions:
                notes, payload = client.notes(value)
                self.save_response(value + "-notes", payload)
                editions = list(
                    {
                        int(note["codDiario"]): {
                            "id": int(note["codDiario"]),
                            "date": value,
                            "edition": note["edition"],
                            "expected_pages": 0,
                        }
                        for note in notes
                    }.values()
                )
            for edition in editions:
                self.register_edition(edition)
            with self.connection() as db:
                # Annual results may reveal an edition missing from the daily response.
                found = db.execute(
                    "SELECT COUNT(*) FROM editions WHERE date=?", (value,)
                ).fetchone()[0]
                db.execute(
                    "INSERT OR REPLACE INTO days VALUES(?,?,NULL,?)",
                    (
                        value,
                        "editions_found" if found else "no_editions_reported",
                        now(),
                    ),
                )
        except Exception as error:
            with self.connection() as db:
                db.execute(
                    "INSERT OR REPLACE INTO days VALUES(?,?,?,?)",
                    (value, "error", str(error)[:2000], now()),
                )

    def edition(self, identifier: int) -> dict:
        with self.connection() as db:
            row = db.execute(
                "SELECT * FROM editions WHERE id=?", (validate_id(identifier),)
            ).fetchone()
        if row is None:
            raise ValueError("Edition not found in the local archive.")
        return dict(row)

    def import_edition(self, client: DofClient, identifier: int) -> str:
        item = self.edition(identifier)
        stem = f"{item['date']}_{item['edition']}_{identifier}"
        year = item["date"][:4]
        pdf = self.root / "pdf" / year / f"{stem}.pdf"
        text_file = self.root / "text" / year / f"{stem}.txt"
        if (
            item["status"] in {"complete", "needs_review"}
            and pdf.exists()
            and text_file.exists()
        ):
            return "unchanged"
        try:
            with self.connection() as db:
                db.execute(
                    "UPDATE editions SET status='downloading',error=NULL,updated_at=? WHERE id=?",
                    (now(), identifier),
                )
            if not pdf.exists():
                client.download_pdf(identifier, pdf)
            pages, ocr_pages, low_text_pages = extract_pdf(pdf)
            metadata = (
                "Diario Oficial de la Federación\n"
                f"Publication date: {item['date']}\nEdition: {item['edition']}\n"
                f"Edition ID: {identifier}\nSource: {item['source_url']}\n"
                f"Retrieved at: {now()}\n"
                "Plain-text derivative; consult the official PDF for images, tables and signatures.\n"
                f"OCR pages: {ocr_pages}\nLow-text pages requiring review: {low_text_pages}\n"
            )
            text = (
                metadata
                + "\n"
                + "\n\n".join(
                    f"=== PAGE {number} ===\n{content}"
                    for number, content in enumerate(pages, 1)
                )
                + "\n"
            )
            atomic_text(text_file, text)
            with pdf.open("rb") as source:
                digest = hashlib.file_digest(source, "sha256").hexdigest()
            warning = None
            if item["expected_pages"] and item["expected_pages"] != len(pages):
                warning = f"API expected {item['expected_pages']} pages; PDF has {len(pages)}."
            state = "needs_review" if low_text_pages or warning else "complete"
            with self.connection() as db:
                db.execute("DELETE FROM pages WHERE edition_id=?", (identifier,))
                db.executemany(
                    "INSERT INTO pages(edition_id,page,content) VALUES(?,?,?)",
                    [
                        (identifier, number, content)
                        for number, content in enumerate(pages, 1)
                    ],
                )
                db.execute(
                    "UPDATE editions SET status=?,pdf_path=?,text_path=?,sha256=?,text_sha256=?,"
                    "bytes=?,pages=?,characters=?,ocr_pages=?,low_text_pages=?,error=?,updated_at=? WHERE id=?",
                    (
                        state,
                        str(pdf.relative_to(self.root)),
                        str(text_file.relative_to(self.root)),
                        digest,
                        hashlib.sha256(text.encode()).hexdigest(),
                        pdf.stat().st_size,
                        len(pages),
                        sum(map(len, pages)),
                        json.dumps(ocr_pages),
                        json.dumps(low_text_pages),
                        warning,
                        now(),
                        identifier,
                    ),
                )
            return state
        except Exception as error:
            with self.connection() as db:
                db.execute(
                    "UPDATE editions SET status='error',error=?,updated_at=? WHERE id=?",
                    (str(error)[:2000], now(), identifier),
                )
            return "error"

    def list_editions(self, start_date: str, end_date: str, offset=0, limit=50) -> dict:
        start, end = parse_date(start_date), parse_date(end_date)
        if end < start or offset < 0 or not 1 <= limit <= 100:
            raise ValueError("Invalid date range or pagination.")
        with self.connection() as db:
            total = db.execute(
                "SELECT COUNT(*) FROM editions WHERE date BETWEEN ? AND ?",
                (str(start), str(end)),
            ).fetchone()[0]
            rows = db.execute(
                "SELECT id,date,edition,status,pages,text_path,source_url FROM editions "
                "WHERE date BETWEEN ? AND ? ORDER BY date,edition,id LIMIT ? OFFSET ?",
                (str(start), str(end), limit, offset),
            ).fetchall()
        return {
            "total": total,
            "items": [dict(row) for row in rows],
            "next_offset": offset + len(rows) if offset + len(rows) < total else None,
        }

    def read_pages(
        self, identifier: int, start_page=1, page_count=1, offset=0, max_chars=20000
    ) -> dict:
        item = self.edition(identifier)
        if (
            start_page < 1
            or not 1 <= page_count <= 10
            or offset < 0
            or not 1 <= max_chars <= 50000
        ):
            raise ValueError("Invalid page or character range.")
        with self.connection() as db:
            rows = db.execute(
                "SELECT page,content FROM pages WHERE edition_id=? AND page>=? AND page<? ORDER BY page",
                (identifier, start_page, start_page + page_count),
            ).fetchall()
        full = "\n\n".join(
            f"=== PAGE {row['page']} ===\n{row['content']}" for row in rows
        )
        return {
            "edition_id": identifier,
            "date": item["date"],
            "source_url": item["source_url"],
            "pages": [row["page"] for row in rows],
            "text": full[offset : offset + max_chars],
            "total_chars": len(full),
            "next_offset": offset + max_chars
            if offset + max_chars < len(full)
            else None,
            "next_page": start_page + page_count
            if start_page + page_count <= item["pages"]
            else None,
            "status": item["status"],
        }

    def search(
        self, query: str, start_date: str, end_date: str, limit=10
    ) -> list[dict]:
        start, end = parse_date(start_date), parse_date(end_date)
        words = re.findall(r"\w+", query, re.UNICODE)
        if not words or len(query) > 300 or not 1 <= limit <= 50 or start > end:
            raise ValueError("Supply a short search query and valid date range.")
        expression = " AND ".join('"' + word + '"' for word in words)
        with self.connection() as db:
            rows = db.execute(
                "SELECT editions.id AS edition_id,editions.date,editions.edition,pages.page,"
                "editions.source_url,snippet(pages_fts,0,'[',']',' … ',48) AS excerpt "
                "FROM pages_fts JOIN pages ON pages.id=pages_fts.rowid "
                "JOIN editions ON editions.id=pages.edition_id "
                "WHERE pages_fts MATCH ? AND editions.date BETWEEN ? AND ? "
                "ORDER BY rank LIMIT ?",
                (expression, str(start), str(end), limit),
            ).fetchall()
        return [dict(row) for row in rows]

    def status(self) -> dict:
        with self.connection() as db:
            days = {
                row[0]: row[1]
                for row in db.execute(
                    "SELECT status,COUNT(*) FROM days GROUP BY status"
                )
            }
            editions = {
                row[0]: row[1]
                for row in db.execute(
                    "SELECT status,COUNT(*) FROM editions GROUP BY status"
                )
            }
            totals = dict(
                db.execute(
                    "SELECT COUNT(*) AS editions,COALESCE(SUM(pages),0) AS pages,"
                    "COALESCE(SUM(characters),0) AS characters,COALESCE(SUM(bytes),0) AS pdf_bytes FROM editions"
                ).fetchone()
            )
            run = db.execute("SELECT * FROM runs ORDER BY id DESC LIMIT 1").fetchone()
        return {
            "days": days,
            "editions": editions,
            "totals": totals,
            "latest_run": dict(run) if run else None,
            "archive_directory": str(self.root),
            "coverage_basis": "SIDOF yearly catalog plus every daily endpoint; empty days cross-checked against notes.",
            "warning": "No-editions-reported is an API result, not proof of non-publication. Text is not a certified copy; graphics and external attachments are not transcribed.",
        }

    def export_manifest(self):
        with self.connection() as db:
            editions = [
                dict(row)
                for row in db.execute("SELECT * FROM editions ORDER BY date,edition,id")
            ]
            days = [dict(row) for row in db.execute("SELECT * FROM days ORDER BY date")]
        atomic_text(
            self.root / "manifest.json",
            json.dumps(
                {**self.status(), "calendar": days, "files": editions},
                ensure_ascii=False,
                indent=2,
            ),
        )
        atomic_text(
            self.root / "status.json",
            json.dumps(self.status(), ensure_ascii=False, indent=2),
        )
