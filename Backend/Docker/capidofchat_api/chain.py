from functools import lru_cache
from operator import itemgetter

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate, format_document
from langchain_core.runnables import RunnableMap, RunnablePassthrough
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from pydantic import BaseModel

from .config import get_pinecone_index_name, get_required_setting


EMBEDDING_MODEL_ID = "sentence-transformers/bert-base-nli-mean-tokens"
EMBEDDING_BATCH_SIZE = 32

CONDENSE_QUESTION_TEMPLATE = """Eres un asistente virtual llamado CapiDOFChat y ayudas a responder preguntas, acerca del Diario Oficial de la Federación (DOF) de México.

Dada la siguiente pregunta de seguimiento y el siguiente historial de chat, genera una pregunta independiente que tenga que ver con la pregunta de seguimiento y que tenga todo el contexto necesario para ser respondida por sí misma.

Toma en cuenta las siguientes reglas para escribir la pregunta independiente:
- Asegúrate de darle prioridad a la pregunta de seguimiento.
- Si la siguiente pregunta de seguimiento tiene que ver con el historial de la conversación, entonces, reformula la pregunta de seguimiento para que sea más específica, pero que tenga que ver con la pregunta de seguimiento.
- Si no tiene que ver en nada con el historial de la conversación, entonces, reescribe la pregunta tal cual es sin que le hagas ningún cambio.

Pregunta de seguimiento: {question}

Historial de la conversación:
{chat_history}

Pregunta independiente:"""

ANSWER_TEMPLATE = """Responde la pregunta basándote solo en el contexto proporcionado. Si no se encuentra en él, indica que el usuario debe ser más específico.

{context}

Pregunta: {question}

Responde en el mismo idioma en que se hace la pregunta.

Asegúrate de que la respuesta:
- Proporcione específicamente la información solicitada en la pregunta.
- Añada un pequeño contexto adicional si es relevante para mayor claridad.
- Esté estructurada de manera clara y concisa, añadiendo detalles según sea necesario.
- Evite cualquier información que no esté contenida en el contexto proporcionado.
- Sea amable y amigable.
- Añada la frase: "¿Hay algo más en lo que te pueda ayudar?" al final de la respuesta.
- Recuerde que su nombre es CapiDOFChat.
- Recuerde que es un asistente virtual que ayuda a responder preguntas legales acerca del Diario Oficial de la Federación (DOF) de México.
- Si la pregunta no tiene nada que ver con el contexto, el historial de chat, el DOF o el asistente, indique que no puede responderla.
- Si la pregunta es ofensiva, inapropiada o no tiene sentido, indique que no puede responderla.
"""

CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(CONDENSE_QUESTION_TEMPLATE)
ANSWER_PROMPT = ChatPromptTemplate.from_template(ANSWER_TEMPLATE)
DOCUMENT_PROMPT = PromptTemplate.from_template("{page_content}")


class ChatInput(BaseModel):
    chat_history: str
    question: str


def combine_documents(documents) -> str:
    return "\n\n".join(format_document(document, DOCUMENT_PROMPT) for document in documents)


def create_embedding_model() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_ID,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"device": "cpu", "batch_size": EMBEDDING_BATCH_SIZE},
    )


def create_retriever():
    vector_store = PineconeVectorStore(
        embedding=create_embedding_model(),
        index_name=get_pinecone_index_name(),
        pinecone_api_key=get_required_setting("PINECONE_API_KEY"),
    )
    return vector_store.as_retriever()


def create_chat_model(temperature: float) -> ChatOpenAI:
    return ChatOpenAI(
        api_key=get_required_setting("OPENAI_API_KEY"),
        temperature=temperature,
    )


@lru_cache(maxsize=1)
def get_chain():
    chat_model = create_chat_model(temperature=0.2)
    retriever = create_retriever()
    inputs = RunnableMap(
        standalone_question=RunnablePassthrough.assign(
            chat_history=lambda payload: payload["chat_history"]
        )
        | CONDENSE_QUESTION_PROMPT
        | chat_model
        | StrOutputParser(),
    )
    context = {
        "context": itemgetter("standalone_question") | retriever | combine_documents,
        "question": itemgetter("standalone_question"),
    }
    chain = inputs | context | ANSWER_PROMPT | chat_model | StrOutputParser()
    return chain
