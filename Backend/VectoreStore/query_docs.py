from datetime import date, timedelta

import requests
from bs4 import BeautifulSoup


SIDOF_API_URL = "https://sidofqa.segob.gob.mx/dof/sidof"
NOTE_GROUPS = ("NotasVespertinas", "NotasExtraordinarias", "NotasMatutinas")


def fetch_note_ids(date_value: str) -> list[str]:
    response = requests.get(f"{SIDOF_API_URL}/notas/{date_value}", timeout=30)
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


def generate_dates_for_year(year: int) -> list[str]:
    current_date = date(year, 1, 1)
    next_year = date(year + 1, 1, 1)
    dates = []
    while current_date < next_year:
        dates.append(current_date.strftime("%d-%m-%Y"))
        current_date += timedelta(days=1)
    return dates


def fetch_notes_for_year(year: int) -> list[dict]:
    notes = []
    for date_value in generate_dates_for_year(year):
        note_ids = fetch_note_ids(date_value)
        daily_notes, _ = fetch_notes(note_ids)
        notes.extend(daily_notes)
    return notes
