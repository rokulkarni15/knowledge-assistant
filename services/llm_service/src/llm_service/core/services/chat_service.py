from llm_service.clients import OllamaClient
from llm_service.core import (
    build_chat_messages, 
    build_extraction_prompt, 
    build_task_extraction_prompt,
    build_summarization_prompt,
    build_analysis_prompt,
)
from infrastructure.redis_cache import RedisCache
from typing import List, Optional, Dict, Any
import logging
import json
from llm_service.core.models import EntityExtractionModel, TaskExtractionModel, DocumentAnalysisModel

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "phi3:mini", embedding_model: str = "mxbai-embed-large"):
        self.ollama = OllamaClient(ollama_url)
        self.model = model
        self.embedding_model = embedding_model
        self.cache = RedisCache()

    async def initialize(self):
        """Initialize cache connection"""
        await self.cache.connect()
        
    async def chat(self, message: str, context: List[str] = None) -> str:
        """Chat with optional context"""
        # Create cache key
        cache_key = self.cache.make_key("chat", message, str(context or []))
        
        # Check cache
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
        
        try:
            messages = build_chat_messages(message, context)
            response = await self.ollama.chat(self.model, messages)
            result = response.strip()
            await self.cache.set(cache_key, result, expire=3600)
            return result
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return f"I'm having trouble processing that request. Error: {str(e)}"
    
    async def extract_entities(self, text: str) -> dict:
        """Extract entities from text"""
        cache_key = self.cache.make_key("extract", text)
        
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
        
        try:
            prompt = build_extraction_prompt(text)
            response = await self.ollama.generate_structured(
                model=self.model,
                prompt=prompt,
                response_format=EntityExtractionModel
            )
            # convert pydantic model to dict
            result_dict = response.model_dump()
            await self.cache.set(cache_key, result_dict, expire=3600)
            return result_dict
        except Exception as e:
            logger.error(f"Entity extraction error: {e}")
            return {
                "people": [],
                "organizations": [],
                "concepts": ["Error processing"],
                "summary": f"Error: {str(e)}"
            }
        
    async def create_embeddings(self, text: str) -> List[float]:
        """Generates embeddings for vector search"""
        # Create cache key
        cache_key = self.cache.make_key("embeddings", text)
        
        # Check cache
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
        
        try:
            embeddings = await self.ollama.generate_embeddings(self.embedding_model, text)
            await self.cache.set(cache_key, embeddings, expire=86400)
            return embeddings
        except Exception as e:
            logger.error(f"Ollama embeddings error: {e}")
            # Return zero vector
            return [0.0] * 384
        
    async def extract_tasks(self, text: str) -> Dict[str, Any]:
        cache_key = self.cache.make_key("tasks", text)
        
        # Check cache
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
        
        try:
            prompt = build_task_extraction_prompt(text)
            response = await self.ollama.generate_structured(
                model=self.model,
                prompt=prompt,
                response_format=TaskExtractionModel,
            )
            result_dict = response.model_dump()
            await self.cache.set(cache_key, result_dict, expire=3600)
            return result_dict
        except Exception as e:
            logger.error(f"Task extraction error: {e}")
            return {
                "tasks": [],
                "estimated_time": f"Failed to extract tasks: {str(e)}"
            }
                
    async def summarize_text(self, text: str, max_length: int = 200) -> Dict[str, str]:
        """Generate text summary"""
        try:
            prompt = build_summarization_prompt(text, max_length)
            response = await self.ollama.generate(self.model, prompt)
            
            summary = response.strip()
            if len(summary) > max_length:
                summary = summary[:max_length] + "..."
            
            return {"summary": summary}
            
        except Exception as e:
            logger.error(f"Summarization error: {e}")
            return {"summary": f"Failed to generate summary: {str(e)}"}
    
    async def analyze_document(self, text: str, analysis_type: str = "general") -> Dict[str, Any]:
        """Comprehensive document analysis"""
        try:
            prompt = build_analysis_prompt(text, analysis_type)
            response = await self.ollama.generate_structured(
                model=self.model,
                prompt=prompt,
                response_format=DocumentAnalysisModel
            )
            
            return response.model_dump()
                    
        except Exception as e:
            logger.error(f"Document analysis error: {e}")
            return {
                "summary": f"Failed to analyze: {str(e)}",
                "key_concepts": [],
                "entities": {
                    "people": [],
                    "organizations": [],
                    "technologies": [],
                    "locations": []
                },
                "tasks": [],
                "themes": [],
                "difficulty_level": "unknown"
            }
        
    async def health_check(self) -> dict:
        """Check service health"""
        try:
            available = await self.ollama.is_available()
            return {
                "ollama_available": available,
                "model": self.model,
                "status": "healthy" if available else "ollama_unavailable"
            }
        except Exception as e:
            return {
                "ollama_available": False,
                "model": self.model,
                "status": f"error: {str(e)}"
            }
    
    async def close(self):
        await self.ollama.close()
        await self.cache.close()
