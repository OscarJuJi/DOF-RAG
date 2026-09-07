from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .chain import ChatInput, get_chain
from .notification_chain import NewDocumentInput, get_notification_chain
from .specific_chain import SpecificQuestionInput, get_specific_chain
from .summary_chain import SummaryInput, get_summary_chain


app = FastAPI(
    title="CapiDOFChat API",
    version="1.0.0",
    description="RAG API for Diario Oficial de la Federación content.",
)

class InvokeRequest(BaseModel):
    input: ChatInput | NewDocumentInput | SpecificQuestionInput | SummaryInput


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


async def invoke_chain(chain_factory, payload: BaseModel) -> dict[str, str]:
    try:
        output = await chain_factory().ainvoke(payload.model_dump())
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    return {"output": output}


@app.post("/query/invoke")
async def invoke_query(request: InvokeRequest) -> dict[str, str]:
    if not isinstance(request.input, ChatInput):
        raise HTTPException(status_code=422, detail="Expected chat input.")
    return await invoke_chain(get_chain, request.input)


@app.post("/notification/invoke")
async def invoke_notification(request: InvokeRequest) -> dict[str, str]:
    if not isinstance(request.input, NewDocumentInput):
        raise HTTPException(status_code=422, detail="Expected new document input.")
    return await invoke_chain(get_notification_chain, request.input)


@app.post("/summary/invoke")
async def invoke_summary(request: InvokeRequest) -> dict[str, str]:
    if not isinstance(request.input, SummaryInput):
        raise HTTPException(status_code=422, detail="Expected document input.")
    return await invoke_chain(get_summary_chain, request.input)


@app.post("/specific/invoke")
async def invoke_specific(request: InvokeRequest) -> dict[str, str]:
    if not isinstance(request.input, SpecificQuestionInput):
        raise HTTPException(status_code=422, detail="Expected document question input.")
    return await invoke_chain(get_specific_chain, request.input)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
