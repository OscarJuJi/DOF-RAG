from functools import lru_cache
from operator import itemgetter

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate, format_document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from pydantic import BaseModel

from .config import get_pinecone_index_name, get_required_setting


EMBEDDING_MODEL_ID = "sentence-transformers/bert-base-nli-mean-tokens"
EMBEDDING_BATCH_SIZE = 32
ANSWER_TEMPLATE = """Dado el siguiente contexto, describe los cambios, actualizaciones y mejoras que se han hecho en el nuevo documento en comparación con el contexto.

Contexto: {context}

Nuevo documento: {new_document}

Responde en el mismo idioma en que se hace la pregunta.

Asegúrate de que la respuesta:
- Proporcione específicamente la información sobre los cambios, actualizaciones y mejoras.
- Añada un pequeño contexto adicional si es relevante para mayor claridad.
- Esté estructurada de manera clara y concisa, añadiendo detalles según sea necesario.
- Destaque claramente los cambios importantes.
- Evite cualquier información que no esté contenida en el contexto o el nuevo documento proporcionados.

Actualizaciones:"""

ANSWER_PROMPT = PromptTemplate.from_template(ANSWER_TEMPLATE)
DOCUMENT_PROMPT = PromptTemplate.from_template("{page_content}")


class NewDocumentInput(BaseModel):
    new_document: str


def combine_documents(documents) -> str:
    return "\n\n".join(format_document(document, DOCUMENT_PROMPT) for document in documents)


def create_retriever():
    embedding_model = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_ID,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"device": "cpu", "batch_size": EMBEDDING_BATCH_SIZE},
    )
    vector_store = PineconeVectorStore(
        embedding=embedding_model,
        index_name=get_pinecone_index_name(),
        pinecone_api_key=get_required_setting("PINECONE_API_KEY"),
    )
    return vector_store.as_retriever()


@lru_cache(maxsize=1)
def get_notification_chain():
    context = {
        "context": itemgetter("new_document") | create_retriever() | combine_documents,
        "new_document": itemgetter("new_document"),
    }
    chat_model = ChatOpenAI(
        api_key=get_required_setting("OPENAI_API_KEY"),
        temperature=0.2,
    )
    chain = context | ANSWER_PROMPT | chat_model | StrOutputParser()
    return chain
