import argparse
import os
from pathlib import Path

from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv


load_dotenv()


def get_required_setting(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def upload_file(file_path: Path, container_name: str) -> None:
    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    service_client = BlobServiceClient.from_connection_string(
        get_required_setting("AZURE_STORAGE_CONNECTION_STRING")
    )
    blob_client = service_client.get_blob_client(
        container=container_name,
        blob=file_path.name,
    )
    with file_path.open("rb") as file_handle:
        blob_client.upload_blob(file_handle, overwrite=True)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Upload a file to Azure Blob Storage.")
    parser.add_argument("file", type=Path, help="File to upload.")
    parser.add_argument("--container", default="pdfs", help="Target container name.")
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_arguments()
    upload_file(arguments.file, arguments.container)
