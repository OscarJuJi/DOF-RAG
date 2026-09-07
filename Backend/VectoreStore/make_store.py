import argparse
from pathlib import Path

from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_parse import LlamaParse
from qdrant_client import QdrantClient

from config import get_required_setting


DEFAULT_COLLECTION_NAME = "demo"


def create_vector_index(document_path: Path, collection_name: str) -> None:
    if not document_path.is_file():
        raise FileNotFoundError(f"Document not found: {document_path}")

    document_parser = LlamaParse(
        api_key=get_required_setting("LLAMA_CLOUD_API_KEY"),
        result_type="markdown",
    )
    documents = document_parser.load_data([str(document_path)])
    client = QdrantClient(
        url=get_required_setting("QDRANT_URL"),
        api_key=get_required_setting("QDRANT_API_KEY"),
    )
    vector_store = QdrantVectorStore(
        client=client,
        collection_name=collection_name,
        enable_hybrid=True,
        batch_size=20,
    )
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    VectorStoreIndex.from_documents(documents, storage_context=storage_context)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest a DOF PDF into Qdrant.")
    parser.add_argument("document", type=Path, help="Path to the DOF PDF.")
    parser.add_argument(
        "--collection",
        default=DEFAULT_COLLECTION_NAME,
        help="Target Qdrant collection name.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_arguments()
    create_vector_index(arguments.document, arguments.collection)
