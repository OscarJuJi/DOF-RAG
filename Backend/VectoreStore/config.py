import os

from dotenv import load_dotenv


load_dotenv()


def get_required_setting(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def get_pinecone_index_name() -> str:
    return os.getenv("PINECONE_INDEX_NAME", "test")
