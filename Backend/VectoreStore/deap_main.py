from collections.abc import Iterable

from langchain_community.embeddings import HuggingFaceEmbeddings
from pinecone import Pinecone
from torch import cuda

from config import get_pinecone_index_name, get_required_setting
from query_docs import fetch_note_ids, fetch_notes


DEFAULT_EMBEDDING_MODEL = "sentence-transformers/bert-base-nli-mean-tokens"


def create_embedding_model(model_id: str, batch_size: int) -> HuggingFaceEmbeddings:
    device = f"cuda:{cuda.current_device()}" if cuda.is_available() else "cpu"
    return HuggingFaceEmbeddings(
        model_name=model_id,
        model_kwargs={"device": device},
        encode_kwargs={"device": device, "batch_size": batch_size},
    )


def create_pinecone_index():
    client = Pinecone(api_key=get_required_setting("PINECONE_API_KEY"))
    return client.Index(get_pinecone_index_name())


def split_notes(notes: Iterable[dict], chunks_per_note: int) -> tuple[list[str], list[dict]]:
    chunk_ids = []
    metadata = []
    for note in notes:
        text = note["text"]
        chunk_length = max(1, len(text) // chunks_per_note)
        for chunk_index in range(chunks_per_note):
            start = chunk_index * chunk_length
            end = None if chunk_index == chunks_per_note - 1 else start + chunk_length
            chunk_text = text[start:end]
            if not chunk_text:
                continue
            chunk_ids.append(f"{note['id']}#chunk{chunk_index + 1}")
            metadata.append(
                {
                    "text": chunk_text,
                    "title": note["title"],
                    "organizations": note["organizations"],
                }
            )
    return chunk_ids, metadata


def upsert_notes(
    index,
    notes: Iterable[dict],
    embedding_model: HuggingFaceEmbeddings,
    batch_size: int,
    chunks_per_note: int,
) -> None:
    chunk_ids, metadata = split_notes(notes, chunks_per_note)
    embeddings = embedding_model.embed_documents([item["text"] for item in metadata])
    for start in range(0, len(chunk_ids), batch_size):
        end = start + batch_size
        vectors = zip(chunk_ids[start:end], embeddings[start:end], metadata[start:end])
        index.upsert(vectors=vectors)


def ingest_date(
    date_value: str,
    model_id: str = DEFAULT_EMBEDDING_MODEL,
    embedding_batch_size: int = 32,
    upsert_batch_size: int = 32,
    chunks_per_note: int = 32,
) -> tuple[int, list[str]]:
    note_ids = fetch_note_ids(date_value)
    notes, failed_note_ids = fetch_notes(note_ids)
    if not notes:
        return 0, failed_note_ids

    embedding_model = create_embedding_model(model_id, embedding_batch_size)
    upsert_notes(
        create_pinecone_index(),
        notes,
        embedding_model,
        upsert_batch_size,
        chunks_per_note,
    )
    return len(notes), failed_note_ids
