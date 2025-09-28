import httpx
import json
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()

    async def chat(self, model: str, messages: List[dict]) -> str:
        """Chat with the ollama model"""
        url = f"{self.base_url}/api/chat"

        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
        }

        try:
            logger.info(f"Calling Ollama chat using {model}")
            response = await self.client.post(url, json=payload)
            response.raise_for_status()

            result = response.json()
            return result["message"]["content"]
        except Exception as e:
            logger.error(f"Ollama chat error: {e}")
            raise Exception(f"Ollama chat failed: {e}")

    async def generate(self, model: str, prompt: str) -> str:
        """Generate text using the ollama model"""
        url = f"{self.base_url}/api/generate"

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }

        try:
            logger.info(f"Calling Ollama generate using {model}")
            response = await self.client.post(url, json=payload)
            response.raise_for_status()

            result = response.json()
            return result["response"]
        except Exception as e:
            logger.error(f"Ollama generate error: {e}")
            raise Exception(f"Ollama generate failed: {e}")
        
    async def generate_embeddings(self, model: str, input: str) -> List[float]:
        """Generate embeddings using the ollama model"""
        url = f"{self.base_url}/api/embed"
        
        payload = {
            "model": model,
            "input": input,
            "stream": False
        }

        try:
            logger.info(f"Calling Ollama embed endpoint using {model}")
            response = self.client.post(url, json=payload)
            response.raise_for_status()

            result = response.json()
            return result["embeddings"][0]
        except Exception as e:
            raise Exception(f"Ollama embeddings failed: {e}")
        
    async def is_available(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except Exception as e:
            return False
        
    async def close(self):
       await self.client.aclose()
