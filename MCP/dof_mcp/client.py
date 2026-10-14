"""Read-only client for the production SIDOF open-data service."""

import re
import threading
import time
from datetime import date, datetime
from email.utils import parsedate_to_datetime
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

API_URL = "https://sidof.segob.gob.mx/dof/sidof"
EDITION_GROUPS = {"Matutina": "MAT", "Vespertina": "VES", "Extraordinaria": "EXT"}
NOTE_GROUPS = {
    "NotasMatutinas": "MAT",
    "NotasVespertinas": "VES",
    "NotasExtraordinarias": "EXT",
}


def parse_date(value: str) -> date:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError("Use an ISO date: YYYY-MM-DD.")
    return date.fromisoformat(value)


def validate_id(value: int) -> int:
    if isinstance(value, bool) or not 1 <= value <= 99_999_999:
        raise ValueError("Invalid DOF identifier.")
    return value


def html_to_text(value: str) -> str:
    soup = BeautifulSoup(value, "html.parser")
    for element in soup(["script", "style", "head", "noscript"]):
        element.decompose()
    for element in soup.find_all("br"):
        element.replace_with("\n")
    for element in soup.find_all(["p", "div", "tr", "li", "h1", "h2", "h3"]):
        element.append("\n")
    text = soup.get_text(" ").replace("\xa0", " ")
    return "\n".join(
        line
        for raw in text.splitlines()
        if (line := re.sub(r"[ \t]+", " ", raw).strip())
    )


class DofClient:
    def __init__(self, interval: float = 0.5, transport=None):
        self.interval = max(0.25, interval)
        self._lock = threading.Lock()
        self._next_request = 0.0
        self.http = httpx.Client(
            timeout=httpx.Timeout(120, connect=20),
            follow_redirects=False,
            trust_env=False,
            transport=transport,
            headers={"User-Agent": "DOF-RAG/1.0 (local public-document archive)"},
        )

    def close(self):
        self.http.close()

    def _throttle(self):
        with self._lock:
            delay = self._next_request - time.monotonic()
            if delay > 0:
                time.sleep(delay)
            self._next_request = time.monotonic() + self.interval

    def _cooldown(self, value: str | None, attempt: int):
        seconds = 2 ** (attempt + 1)
        if value:
            try:
                seconds = max(seconds, float(value))
            except ValueError:
                try:
                    seconds = max(
                        seconds, parsedate_to_datetime(value).timestamp() - time.time()
                    )
                except (ValueError, TypeError):
                    pass
        with self._lock:
            self._next_request = max(self._next_request, time.monotonic() + seconds)

    def json(self, path: str, *, allow_missing=False) -> dict:
        for attempt in range(5):
            self._throttle()
            try:
                response = self.http.get(API_URL + path)
                if response.status_code == 429 or response.status_code >= 500:
                    response.raise_for_status()
                payload = response.json()
                if not isinstance(payload, dict):
                    raise ValueError("SIDOF returned an unexpected JSON schema.")
                code = payload.get("messageCode")
                if allow_missing and code == 404 and response.status_code in (200, 404):
                    return payload
                response.raise_for_status()
                if code != 200:
                    raise ValueError(f"SIDOF returned messageCode={code!r}.")
                return payload
            except (httpx.TransportError, httpx.HTTPStatusError) as error:
                response = (
                    error.response if isinstance(error, httpx.HTTPStatusError) else None
                )
                if (
                    response is not None
                    and response.status_code not in (408, 429)
                    and response.status_code < 500
                ):
                    raise
                if attempt == 4:
                    raise
                self._cooldown(
                    response.headers.get("Retry-After")
                    if response is not None
                    else None,
                    attempt,
                )
        raise RuntimeError("Unreachable retry state.")

    def editions(self, publication_date: str) -> tuple[list[dict], dict]:
        day = parse_date(publication_date)
        payload = self.json(f"/diarios/porFecha/{day:%d-%m-%Y}", allow_missing=True)
        if payload.get("messageCode") == 200 and not any(
            key in payload for key in EDITION_GROUPS
        ):
            raise ValueError("SIDOF edition groups are missing; date not marked empty.")
        editions = {}
        for group, edition in EDITION_GROUPS.items():
            for item in payload.get(group) or []:
                identifier = validate_id(int(item["codDiario"]))
                existing = editions.setdefault(
                    identifier,
                    {
                        "id": identifier,
                        "date": publication_date,
                        "edition": edition,
                        "expected_pages": 0,
                    },
                )
                existing["expected_pages"] = max(
                    existing["expected_pages"], int(item.get("paginaMax") or 0)
                )
        return list(editions.values()), payload

    def notes(self, publication_date: str) -> tuple[list[dict], dict]:
        day = parse_date(publication_date)
        payload = self.json(f"/notas/{day:%d-%m-%Y}", allow_missing=True)
        if payload.get("messageCode") == 200 and not any(
            key in payload for key in NOTE_GROUPS
        ):
            raise ValueError("SIDOF note groups are missing; date not marked empty.")
        notes = []
        for group, edition in NOTE_GROUPS.items():
            for item in payload.get(group) or []:
                notes.append({**item, "edition": edition})
        return notes, payload

    def note(self, note_id: int) -> dict:
        identifier = validate_id(note_id)
        payload = self.json(f"/notas/nota/{identifier}")
        note = payload.get("Nota") or payload.get("nota")
        if not isinstance(note, dict) or int(note.get("codNota", 0)) != identifier:
            raise ValueError("SIDOF returned an invalid note.")
        text = html_to_text(note.get("cadenaContenido") or "")
        return {
            "id": identifier,
            "title": note.get("titulo"),
            "date": note.get("fecha"),
            "edition_id": note.get("codDiario"),
            "page": note.get("pagina"),
            "text": text,
            "has_text": bool(text),
            "source_url": f"{API_URL}/notas/nota/{identifier}",
            "warning": "Text excludes images and external attachments. Consult the original PDF.",
            "upstream_content_too_large": bool(payload.get("tamanioExcesivo")),
        }

    def download_pdf(self, identifier: int, destination: Path) -> None:
        identifier = validate_id(identifier)
        destination.parent.mkdir(parents=True, exist_ok=True)
        partial = destination.with_suffix(".pdf.part")
        for attempt in range(5):
            self._throttle()
            try:
                with self.http.stream(
                    "GET", f"{API_URL}/documentos/pdf/{identifier}"
                ) as response:
                    response.raise_for_status()
                    size = 0
                    with partial.open("wb") as output:
                        for chunk in response.iter_bytes():
                            size += len(chunk)
                            if size > 512 * 1024 * 1024:
                                raise ValueError(
                                    "PDF exceeds the 512 MiB safety limit."
                                )
                            output.write(chunk)
                with partial.open("rb") as source:
                    if source.read(5) != b"%PDF-":
                        raise ValueError("SIDOF did not return a PDF.")
                partial.replace(destination)
                return
            except (httpx.TransportError, httpx.HTTPStatusError) as error:
                response = (
                    error.response if isinstance(error, httpx.HTTPStatusError) else None
                )
                if (
                    response is not None
                    and response.status_code not in (408, 429)
                    and response.status_code < 500
                ):
                    raise
                if attempt == 4:
                    raise
                self._cooldown(
                    response.headers.get("Retry-After")
                    if response is not None
                    else None,
                    attempt,
                )


def api_date(value: str) -> str:
    return datetime.strptime(value, "%d-%m-%Y").date().isoformat()
