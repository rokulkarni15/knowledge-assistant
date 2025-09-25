from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from llm_service.core import ChatService
import os

router = APIRouter()


chat_service = ChatService(
    ollama_url=os.getenv("OLLAMA_URL", "http://localhost:11434"),
    model=os.getenv("OLLAMA_MODEL", "phi3:mini")
)

class ChatRequest(BaseModel):
    message: str
    context: Optional[List[str]] = None

class ChatResponse(BaseModel):
    response: str
    model: str

class ExtractRequest(BaseModel):
    text: str

class ExtractResponse(BaseModel):
    entities: dict
    model: str

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with optional context"""
    try:
        response = await chat_service.chat(
            message=request.message, 
            context=request.context or []
        )
        
        return ChatResponse(
            response=response,
            model=chat_service.model
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/extract", response_model=ExtractResponse) 
async def extract_entities(request: ExtractRequest):
    """Extract entities from text"""
    try:
        entities = await chat_service.extract_entities(request.text)
        
        return ExtractResponse(
            entities=entities,
            model=chat_service.model
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health():
    """Health check with Ollama status"""
    return await chat_service.health_check()