from pathlib import Path

import requests
from bs4 import BeautifulSoup


SIDOF_API_URL = "https://sidofqa.segob.gob.mx/dof/sidof"
NOTE_GROUPS = ("NotasVespertinas", "NotasExtraordinarias", "NotasMatutinas")


def fetch_note_ids(date: str) -> list[str]:
    response = requests.get(f"{SIDOF_API_URL}/notas/{date}", timeout=30)
    response.raise_for_status()
    payload = response.json()
    return [
        str(note["codNota"])
        for group in NOTE_GROUPS
        for note in payload.get(group, [])
    ]


def fetch_notes(note_ids: list[str]) -> tuple[list[dict], list[str]]:
    notes = []
    failed_note_ids = []

    for note_id in note_ids:
        response = requests.get(f"{SIDOF_API_URL}/notas/nota/{note_id}", timeout=30)
        if not response.ok:
            failed_note_ids.append(note_id)
            continue

        note = response.json().get("Nota", {})
        html_content = note.get("cadenaContenido")
        text = (
            BeautifulSoup(html_content, "html.parser").get_text(" ", strip=True)
            if html_content
            else ""
        )
        title = note.get("titulo")
        if not title or not text:
            failed_note_ids.append(note_id)
            continue

        organizations = [
            note[organization_key]
            for organization_key in (
                "codOrgaUno",
                "codOrgaDos",
                "codOrgaTres",
                "codOrgaCuatro",
            )
            if note.get(organization_key) not in (None, "null")
        ]
        notes.append(
            {
                "id": note_id,
                "title": title,
                "text": text,
                "organizations": organizations,
            }
        )

    return notes, failed_note_ids


def fetch_issue_ids(date: str) -> list[str]:
    response = requests.get(f"{SIDOF_API_URL}/diarios/porFecha/{date}", timeout=30)
    response.raise_for_status()
    payload = response.json()
    return [
        issue[0]["codDiario"]
        for issue in (
            payload.get("Vespertina"),
            payload.get("Extraordinaria"),
            payload.get("Matutina"),
        )
        if issue
    ]


def download_issue_pdf(issue_id: str, output_directory: Path) -> Path:
    response = requests.get(
        f"{SIDOF_API_URL}/documentos/pdf/{issue_id}",
        timeout=60,
    )
    response.raise_for_status()
    output_directory.mkdir(parents=True, exist_ok=True)
    output_path = output_directory / f"diario_{issue_id}.pdf"
    output_path.write_bytes(response.content)
    return output_path
