import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, List, Optional, Dict
from enum import Enum
from llm_service.core import ChatService
import os
import logging

logger = logging.getLogger(__name__)


router = APIRouter()


chat_service = ChatService(
    ollama_url=os.getenv("OLLAMA_URL", "http://localhost:11434"),
    model=os.getenv("OLLAMA_MODEL", "phi3:mini")
)

class ChatRequest(BaseModel):
    message: str
    context: Optional[List[str]] = None
    search_limit: int = 3

class ChatResponse(BaseModel):
    response: str
    model: str
    sources: List[dict]

class ExtractRequest(BaseModel):
    text: str

class ExtractResponse(BaseModel):
    entities: dict
    model: str

class EmbeddingRequest(BaseModel):
    text: str

class EmbeddingResponse(BaseModel):
    embeddings: List[float]
    dimensions: int
    model: str

class TaskExtractionRequest(BaseModel):
    text: str

class TaskExtractionResponse(BaseModel):
    tasks: List[Dict[str, Any]]
    estimated_time: Optional[str]
    model: str

class SummarizeRequest(BaseModel):
    text: str
    max_length: int = 200

class SummarizeResponse(BaseModel):
    summary: str
    original_length: int
    summary_length: int
    compression_ratio: float
    model: str

class AnalysisType(str, Enum):
    general = "general"
    research_paper = "research_paper"
    meeting_notes = "meeting_notes"
    technical_doc = "technical_doc"
    
class DocAnalysisRequest(BaseModel):
    text: str
    analysis_type: AnalysisType = AnalysisType.general

class DocAnalysisResponse(BaseModel):
    summary: str
    key_concepts: List[str]
    entities: Dict[str, List[str]]
    tasks: List[Dict[str, Any]]
    themes: List[str]
    difficulty_level: str
    model: str


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with optional context"""
    context = request.context or []
    sources = []
    search_service_url = os.getenv("SEARCH_SERVICE_URL", "http://localhost:8004")

    try:
        async with httpx.AsyncClient() as client:
            search_response = await client.get(
                f"{search_service_url}/api/v1/search",
                params={"q": request.message, "limit": request.search_limit},
                timeout=5.0,
            )

            if search_response.status_code == 200:
                search_data = search_response.json()
                results = search_data.get("results", [])
                # Add retrieved documents to context
                rag_context = [result["content"] for result in results]
                context.extend(rag_context)
                # Prepare sources
                sources = [
                    {
                        "document_id": result["document_id"],
                        "score": result["score"],
                        "preview": result["content"][:150] + "..." if len(result["content"]) > 150 else result["content"]
                    }
                    for result in results
                ]
    except Exception as e:
        logger.warning("RAG search failed, using general knowledge: {e}")
    
    try:
        response = await chat_service.chat(
            message=request.message, 
            context= context if context else None
        )
        return ChatResponse(
            response=response,
            model=chat_service.model,
            sources=sources
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

@router.post("/embeddings", response_model=EmbeddingResponse)
async def create_embeddings(request: EmbeddingRequest):
    try:
        embeddings = await chat_service.create_embeddings(request.text)

        return EmbeddingResponse(
            embeddings=embeddings,
            dimensions=len(embeddings),
            model=chat_service.model
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tasks", response_model=TaskExtractionResponse)
async def extract_tasks(request: TaskExtractionRequest):
    try: 
        task_data = await chat_service.extract_tasks(request.text)

        return TaskExtractionResponse(
            tasks=task_data["tasks"],
            estimated_time=task_data.get("estimated_time"),
            model=chat_service.model
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/summarize", response_model=SummarizeResponse)
async def summarize_text(request: SummarizeRequest):
    """Generate different types of summaries"""
    try:
        summary_data = await chat_service.summarize_text(
            text=request.text,
            max_length=request.max_length
        )
        
        return SummarizeResponse(
            summary=summary_data["summary"],
            original_length=len(request.text),
            summary_length=len(summary_data["summary"]),
            compression_ratio=len(summary_data["summary"]) / len(request.text),
            model=chat_service.model
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze", response_model=DocAnalysisResponse)
async def analyze_document(request: DocAnalysisRequest):
    """Comprehensive document analysis"""
    try:
        analysis = await chat_service.analyze_document(
            text=request.text,
            analysis_type=request.analysis_type
        )
        
        return DocAnalysisResponse(
            summary=analysis["summary"],
            key_concepts=analysis["key_concepts"],
            entities=analysis["entities"],
            tasks=analysis["tasks"],
            themes=analysis["themes"],
            difficulty_level=analysis["difficulty_level"],
            model=chat_service.model
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health():
    """Health check with Ollama status"""
    return await chat_service.health_check()