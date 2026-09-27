from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.demo_data import seed_demo_docs

app = FastAPI(title="HexaSense", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok", "app": "HexaSense"}


@app.get("/")
def root():
    return {
        "name": "HexaSense",
        "message": "Private AI knowledge assistant for Snapdragon PCs",
        "offline_mode": settings.offline_mode,
    }


@app.on_event("startup")
def startup_event():
    # In a full app this would initialize local vector stores, config, and memory.
    seed_demo_docs()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
