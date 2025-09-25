from llm_service.clients import OllamaClient
from llm_service.core import build_chat_messages, build_extraction_prompt
from typing import List, Optional
import logging
import json

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "phi3:mini"):
        self.ollama = OllamaClient(ollama_url)
        self.model = model
        
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
