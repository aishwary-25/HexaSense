from contextlib import asynccontextmanager

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.config import settings
from src.demo_data import seed_demo_docs
from src.pipeline import HexaSensePipeline, PipelineError

pipeline = HexaSensePipeline(settings)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    seed_demo_docs(settings.sample_docs_dir)
    yield


app = FastAPI(title="HexaSense", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    health_method = getattr(pipeline.llm_client, "health_check", None)
    local_ai = (
        health_method()
        if health_method is not None
        else {
            "ready": False,
            "model": pipeline.config.model_name,
            "message": "The configured local model client does not expose a health check.",
        }
    )
    return {
        "status": "ok",
        "app": "HexaSense",
        "indexed_documents": len(pipeline.list_documents()),
        "indexed_chunks": pipeline.vector_store.count(),
        "local_ai": local_ai,
    }


@app.get("/")
def root():
    return {
        "name": "HexaSense",
        "message": "Private AI knowledge assistant for Snapdragon PCs",
        "offline_mode": settings.offline_mode,
    }


class QueryRequest(BaseModel):
    question: str = Field(min_length=1)
    top_k: int | None = Field(default=None, ge=1, le=50)


@app.get("/documents")
def list_documents():
    return {"documents": pipeline.list_documents()}


@app.post("/documents")
async def upload_document(
    file: UploadFile = File(...),
    redact: bool = Form(default=True),
):
    try:
        content = await file.read()
        if not content:
            raise PipelineError(f"'{file.filename or 'upload'}' is empty.")
        return pipeline.index_bytes(
            content, file.filename or "upload.txt", redact=redact
        )
    except PipelineError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.delete("/documents/{doc_id}")
def forget_document(doc_id: str):
    try:
        return pipeline.forget_document(doc_id)
    except PipelineError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/query")
def query_documents(request: QueryRequest):
    try:
        result = pipeline.query(request.question, top_k=request.top_k)
        return {"answer": result.answer, "sources": result.sources}
    except PipelineError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
