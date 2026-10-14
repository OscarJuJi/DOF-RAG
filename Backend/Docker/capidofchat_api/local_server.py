"""Local production API, backed by SQLite and Ollama."""

import os
from contextlib import asynccontextmanager
from typing import Generic, TypeVar

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException as StarletteHTTPException

from . import local_rag
from .accounts import bootstrap_admin, current_user, router
from .storage import database, initialize_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    bootstrap_admin()
    yield


app = FastAPI(title="CapiDOFChat Local API", version="2.0.0", lifespan=lifespan)
app.include_router(router)


@app.exception_handler(StarletteHTTPException)
async def http_error(request: Request, error: StarletteHTTPException):
    return JSONResponse(
        {"detail": error.detail, "message": error.detail}, status_code=error.status_code
    )


@app.exception_handler(httpx.HTTPError)
async def provider_error(request: Request, error: httpx.HTTPError):
    return JSONResponse(
        {
            "message": "Ollama no está disponible o falta un modelo. "
            "Revisa el estado local."
        },
        status_code=503,
    )


@app.exception_handler(RuntimeError)
async def runtime_error(request: Request, error: RuntimeError):
    return JSONResponse({"message": str(error)}, status_code=503)


class ChatInput(BaseModel):
    question: str = Field(min_length=1, max_length=2500)
    chat_history: str = Field(default="", max_length=16000)


class DocumentInput(BaseModel):
    document: str = Field(min_length=1, max_length=24000)


class SpecificInput(DocumentInput):
    question: str = Field(min_length=1, max_length=2500)


class NotificationInput(BaseModel):
    new_document: str = Field(min_length=1, max_length=12000)


Payload = TypeVar("Payload")


class InvokeRequest(BaseModel, Generic[Payload]):
    input: Payload


@app.get("/health")
def health():
    with database() as connection:
        connection.execute("SELECT 1")
    return {"status": "ok"}


@app.get("/api/status")
def status(user=Depends(current_user)):
    with database() as connection:
        documents = connection.execute(
            "SELECT COUNT(*) FROM documents WHERE model=?", (local_rag.EMBEDDING_MODEL,)
        ).fetchone()[0]
        chunks = connection.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
    try:
        response = httpx.get(
            f"{local_rag.OLLAMA_URL}/api/tags", timeout=10, trust_env=False
        )
        response.raise_for_status()
        models = {model["name"] for model in response.json()["models"]}
        ready = all(
            model in models
            for model in (local_rag.CHAT_MODEL, local_rag.EMBEDDING_MODEL)
        )
    except httpx.HTTPError:
        ready = False
    return {
        "ready": ready and documents > 0,
        "models_ready": ready,
        "documents": documents,
        "chunks": chunks,
        "model": local_rag.CHAT_MODEL,
        "mode": "local",
    }


@app.get("/api/documents")
def list_documents(user=Depends(current_user)):
    with database() as connection:
        rows = connection.execute(
            "SELECT id, name, pages, indexed_at FROM documents "
            "WHERE model=? ORDER BY indexed_at DESC",
            (local_rag.EMBEDDING_MODEL,),
        ).fetchall()
    return [dict(row) for row in rows]


@app.get("/api/documents/{identifier}/file")
def document_file(identifier: str, user=Depends(current_user)):
    with database() as connection:
        row = connection.execute(
            "SELECT path, name FROM documents WHERE id=?", (identifier,)
        ).fetchone()
    if row is None or not os.path.isfile(row["path"]):
        raise HTTPException(404, "Documento no disponible.")
    return FileResponse(row["path"], filename=row["name"])


@app.post("/api/documents/{identifier}/summary")
def summarize_document(identifier: str, user=Depends(current_user)):
    try:
        return {"output": local_rag.document_summary(identifier)}
    except KeyError as error:
        raise HTTPException(404, "Documento no encontrado.") from error


@app.post("/query/invoke")
def query(request: InvokeRequest[ChatInput], user=Depends(current_user)):
    return local_rag.answer_query(request.input.question, request.input.chat_history)


@app.post("/summary/invoke")
def summary(request: InvokeRequest[DocumentInput], user=Depends(current_user)):
    with local_rag.MODEL_LOCK:
        return {
            "output": local_rag.generate(
                f"Resume el documento proporcionado:\n{request.input.document}"
            )
        }


@app.post("/specific/invoke")
def specific(request: InvokeRequest[SpecificInput], user=Depends(current_user)):
    with local_rag.MODEL_LOCK:
        return {
            "output": local_rag.generate(
                f"Documento:\n{request.input.document}\n"
                f"Pregunta: {request.input.question}"
            )
        }


@app.post("/notification/invoke")
def notification(request: InvokeRequest[NotificationInput], user=Depends(current_user)):
    with local_rag.MODEL_LOCK:
        sources = local_rag.retrieve(request.input.new_document[:2000])
        context = "\n".join(source["content"] for source in sources)
        return {
            "output": local_rag.generate(
                "Compara el nuevo documento con los fragmentos del archivo. "
                "Solo describe cambios respaldados por ambos.\n"
                f"Archivo:\n{context}\nNuevo documento:\n{request.input.new_document}"
            )
        }
