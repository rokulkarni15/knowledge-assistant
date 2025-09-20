from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from api_gateway.config import settings, SERVICE_REGISTRY
from api_gateway.routes import router as proxy_router, service_proxy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("API Gateway starting up...")
    logger.info(f"Available services: {list(SERVICE_REGISTRY.keys())}")
    yield
    await service_proxy.close()
    logger.info("API Gateway shutting down...")

app = FastAPI(
    title="Knowledge Assistant API Gateway",
    description="Central API gateway for routing requests",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "api-gateway",
        "version": "0.1.0",
        "services": list(SERVICE_REGISTRY.keys())
    }

@app.get("/")
async def root():
    return {"message": "Knowledge Assistant API Gateway", "docs": "/docs"}

@app.get("/api/v1/services")
async def list_services():
    return {"services": SERVICE_REGISTRY}

app.include_router(proxy_router, prefix="/api/v1")