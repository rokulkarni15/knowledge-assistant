import httpx
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class GithubClient:
    def __init__(self, token: str, username: str):
        self.token = token
        self.username = username
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.client = httpx.AsyncClient(timeout=30.0)

    async def get_user_repos(self, limit: str = 30):
        try:
            response = await self.client.get(
            url = f"{self.base_url}/users/{self.username}/repos",
            headers=self.headers,
            params = {"sort": "updated", "per_page": limit, "type": "owner"}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get repos: {e}")
            return []

    async def search_repositories(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search repositories"""
        try:
            url = f"{self.base_url}/search/repositories"
            params = {"q": f"{query} user:{self.username}", "per_page": limit, "sort": "updated"}
            
            response = await self.client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            return data.get("items", [])  
        except Exception as e:
            logger.error(f"Failed to search repos: {e}")
            return []
    
    async def search_code(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search code in user's repositories"""
        try:
            url = f"{self.base_url}/search/code"
            params = {"q": f"{query} user:{self.username}", "per_page": limit}
            
            response = await self.client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            return data.get("items", [])
            
        except Exception as e:
            logger.error(f"Failed to search code: {e}")
            return []
    
    async def get_repo_readme(self, repo_name: str) -> str:
        """Get repository README"""
        try:
            url = f"{self.base_url}/repos/{self.username}/{repo_name}/readme"
            
            response = await self.client.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            # README content is base64 encoded
            import base64
            content = base64.b64decode(data.get("content", "")).decode('utf-8')
            return content
            
        except Exception as e:
            logger.error(f"Failed to get README: {e}")
            return ""
    
    async def get_repo_issues(self, repo_name: str, state: str = "open", limit: int = 30) -> List[Dict[str, Any]]:
        """Get repository issues"""
        try:
            url = f"{self.base_url}/repos/{self.username}/{repo_name}/issues"
            params = {"state": state, "per_page": limit}
            
            response = await self.client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to get issues: {e}")
            return []
    
    async def get_recent_commits(self, repo_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent commits"""
        try:
            url = f"{self.base_url}/repos/{self.username}/{repo_name}/commits"
            params = {"per_page": limit}
            
            response = await self.client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to get commits: {e}")
            return []
    
    async def close(self):
        await self.client.aclose()