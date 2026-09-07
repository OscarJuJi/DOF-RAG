from functools import lru_cache

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from .config import get_required_setting


SUMMARY_TEMPLATE = """Dado el siguiente documento, genera un resumen detallado y extenso del mismo en su idioma original.

{document}

Instrucciones para el resumen:
- Destaca los puntos clave del documento.
- Proporciona detalles relevantes que ayuden a entender mejor el contenido.
- Enfócate en la esencia del contenido para una comprensión rápida y efectiva.
- Mantén la objetividad y precisión en la información presentada, evitando sesgos o interpretaciones subjetivas.
- Estructura el resumen en párrafos separados por temas o secciones importantes.
- Incluye ejemplos específicos y citas textuales cuando sea relevante.
- Si hay varias secciones o capítulos, proporciona un resumen detallado de cada uno.

Resumen:"""

SUMMARY_PROMPT = PromptTemplate.from_template(SUMMARY_TEMPLATE)


class SummaryInput(BaseModel):
    document: str


@lru_cache(maxsize=1)
def get_summary_chain():
    chat_model = ChatOpenAI(
        api_key=get_required_setting("OPENAI_API_KEY"),
        temperature=0.3,
    )
    chain = SUMMARY_PROMPT | chat_model | StrOutputParser()
    return chain
