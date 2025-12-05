import httpx
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class MCPClient:
    def __init__(self, github_mcp_url: str):
        self.github_mcp_url = github_mcp_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def call_github_tool(self, tool: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a GitHub MCP tool"""
        try:
            logger.info(f"🔧 Calling GitHub MCP tool: {tool}")
            
            response = await self.client.post(
                f"{self.github_mcp_url}/tools/call",
                json={"tool": tool, "arguments": arguments}
            )
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"GitHub MCP tool call failed: {e}")
            return {"error": str(e)}
    
    async def list_github_resources(self) -> List[Dict[str, Any]]:
        """List available GitHub resources"""
        try:
            response = await self.client.get(f"{self.github_mcp_url}/resources")
            response.raise_for_status()
            
            data = response.json()
            return data.get("resources", [])
            
        except Exception as e:
            logger.error(f"Failed to list GitHub resources: {e}")
            return []
    
    async def read_github_resource(self, repo_name: str) -> Dict[str, Any]:
        """Read a specific GitHub resource"""
        try:
            response = await self.client.get(f"{self.github_mcp_url}/resources/{repo_name}")
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to read GitHub resource: {e}")
            return {"error": str(e)}
    
    async def close(self):
        await self.client.aclose()