import os
from datetime import datetime

import requests
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv


load_dotenv()

DOF_SEARCH_URL = "https://sidof.segob.gob.mx/dof/sidof/buscarNotas/titulo/{area}"
DOF_DOCUMENT_URL = "https://www.dof.gob.mx/nota_to_doc.php?codnota={note_id}"
SEARCH_AREAS = (
    "juridico",
    "tesoreria",
    "contraloria",
    "contabilidad",
    "banco de mexico",
    "sistemas",
    "banca",
    "finanzas",
)


def get_required_setting(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def get_matching_note_ids(area: str, minimum_date: datetime) -> list[int]:
    response = requests.get(DOF_SEARCH_URL.format(area=area), timeout=30)
    response.raise_for_status()
    notes = response.json().get("Notas", [])
    return [
        note["codNota"]
        for note in notes
        if datetime.strptime(note["fecha"], "%d-%m-%Y") >= minimum_date
    ]


def get_blob_client(container_name: str, blob_name: str):
    service_client = BlobServiceClient.from_connection_string(
        get_required_setting("AZURE_STORAGE_CONNECTION_STRING")
    )
    return service_client.get_blob_client(container=container_name, blob=blob_name)


def download_note(note_id: int, blob_name: str, container_name: str) -> None:
    response = requests.get(DOF_DOCUMENT_URL.format(note_id=note_id), timeout=60)
    response.raise_for_status()
    get_blob_client(container_name, blob_name).upload_blob(response.content, overwrite=True)


def sync_notes(container_name: str = "docs") -> None:
    minimum_date = datetime(2022, 1, 1)
    note_ids = {
        note_id
        for area in SEARCH_AREAS
        for note_id in get_matching_note_ids(area, minimum_date)
    }
    manifest_client = get_blob_client(container_name, "downloaded_note_ids.txt")
    if manifest_client.exists():
        content = manifest_client.download_blob().readall().decode("utf-8")
        downloaded_ids = {int(value) for value in content.splitlines() if value}
    else:
        downloaded_ids = set()

    for note_id in sorted(note_ids - downloaded_ids):
        download_note(note_id, f"dof_{note_id}.doc", container_name)
        downloaded_ids.add(note_id)

    manifest_client.upload_blob(
        "\n".join(map(str, sorted(downloaded_ids))),
        overwrite=True,
    )


if __name__ == "__main__":
    sync_notes()
