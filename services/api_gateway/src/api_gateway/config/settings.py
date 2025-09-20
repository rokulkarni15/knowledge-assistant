from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Service URLs
    llm_service_url: str = "http://localhost:8002"
    content_processor_url: str = "http://localhost:8003"
    search_service_url: str = "http://localhost:8004"
    websocket_hub_url: str = "http://localhost:8005"
    
    # API Gateway settings
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # CORS settings
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    class Config:
        env_file = ".env"

settings = Settings()

SERVICE_REGISTRY = {
    "llm": settings.llm_service_url,
    "content": settings.content_processor_url,
    "search": settings.search_service_url,
    "ws": settings.websocket_hub_url,
}