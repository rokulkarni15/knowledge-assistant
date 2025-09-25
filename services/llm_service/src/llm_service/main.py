from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
from llm_service.api import chat

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("LLM Service starting up...")
    yield
    logger.info("LLM Service shutting down...")

app = FastAPI(
    title="LLM Service",
    description="Ollama-powered LLM service for Knowledge Assistant",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(chat.router, prefix="/chat", tags=["chat"])

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "llm-service",
        "version": "0.1.0"
    }

@app.get("/")
async def root():
    return {"message": "LLM Service", "docs": "/docs"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002, reload=True)