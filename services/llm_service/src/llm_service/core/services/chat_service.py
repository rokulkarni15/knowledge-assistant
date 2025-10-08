from llm_service.clients import OllamaClient
from llm_service.core import (
    build_chat_messages, 
    build_extraction_prompt, 
    build_task_extraction_prompt,
    build_summarization_prompt,
    build_analysis_prompt,
)
from typing import List, Optional, Dict, Any
import logging
import json

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "phi3:mini", embedding_model: str = "mxbai-embed-large"):
        self.ollama = OllamaClient(ollama_url)
        self.model = model
        self.embedding_model = embedding_model
        
    async def chat(self, message: str, context: List[str] = None) -> str:
        """Chat with optional context"""
        try:
            messages = build_chat_messages(message, context)
            response = await self.ollama.chat(self.model, messages)
            return response.strip()
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return f"I'm having trouble processing that request. Error: {str(e)}"
    
    async def extract_entities(self, text: str) -> dict:
        """Extract entities from text"""
        try:
            prompt = build_extraction_prompt(text)
            response = await self.ollama.generate(self.model, prompt)
            
            # Try to parse JSON from response
            try:
                start = response.find('{')
                end = response.rfind('}') + 1
                if start >= 0 and end > start:
                    json_str = response[start:end]
                    return json.loads(json_str)
            except:
                pass
            
            # Fallback
            return {
                "people": [],
                "organizations": [],
                "concepts": [text[:100] + "..." if len(text) > 100 else text],
                "summary": "Content processed successfully"
            }
            
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
        try:
            embeddings = await self.ollama.generate_embeddings(self.embedding_model, text)
            return embeddings
        except Exception as e:
            logger.error(f"Ollama embeddings error: {e}")
            # Return zero vector
            return [0.0] * 384
        
    async def extract_tasks(self, text: str) -> Dict[str, Any]:
        try:
            prompt = build_task_extraction_prompt(text)
            response = await self.ollama.generate(self.model, prompt)

            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
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
            response = await self.ollama.generate(self.model, prompt)
            
            # Try to extract JSON
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
            
            raise ValueError("No valid JSON found in response")
            
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
