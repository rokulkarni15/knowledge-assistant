from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
import json

from clients.github_client import GithubClient
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="GitHub MCP Server (HTTP)",
    description="HTTP wrapper for GitHub MCP server - for testing",
    version="0.1.0"
)

# Initialize GitHub client
github_client = GithubClient(settings.github_token, settings.github_username)

class ToolCallRequest(BaseModel):
    tool: str
    arguments: Dict[str, Any]

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "github-mcp-server",
        "github_user": settings.github_username
    }

@app.get("/")
async def root():
    return {
        "message": "GitHub MCP Server",
        "docs": "/docs",
        "github_user": settings.github_username
    }

@app.get("/resources")
async def list_resources():
    """List available GitHub repositories"""
    repos = await github_client.get_user_repos(limit=50)
    
    resources = [
        {
            "uri": f"github://repo/{repo['name']}",
            "name": repo['name'],
            "description": repo.get('description', 'No description'),
            "metadata": {
                "language": repo.get('language'),
                "stars": repo.get('stargazers_count', 0),
                "updated_at": repo.get('updated_at'),
                "url": repo.get('html_url')
            }
        }
        for repo in repos
    ]
    
    return {"resources": resources, "total": len(resources)}

@app.get("/resources/{repo_name}")
async def read_resource(repo_name: str):
    """Read a specific repository's README"""
    readme = await github_client.get_repo_readme(repo_name)
    
    if not readme:
        return {"error": "README not found"}
    
    return {
        "uri": f"github://repo/{repo_name}",
        "name": repo_name,
        "content": readme,
        "mimeType": "text/markdown"
    }

@app.post("/tools/call")
async def call_tool(request: ToolCallRequest):
    """Call a GitHub tool"""
    logger.info(f"🔧 Tool call: {request.tool}")
    
    if request.tool == "search_repos":
        query = request.arguments.get("query", "")
        limit = request.arguments.get("limit", 10)
        
        repos = await github_client.search_repositories(query, limit)
        
        return {
            "tool": "search_repos",
            "result": [
                {
                    "name": repo['name'],
                    "description": repo.get('description', ''),
                    "language": repo.get('language'),
                    "stars": repo.get('stargazers_count', 0),
                    "url": repo.get('html_url')
                }
                for repo in repos
            ]
        }
    
    elif request.tool == "search_code":
        query = request.arguments.get("query", "")
        limit = request.arguments.get("limit", 10)
        
        code_results = await github_client.search_code(query, limit)
        
        return {
            "tool": "search_code",
            "result": [
                {
                    "file": item['name'],
                    "path": item['path'],
                    "repository": item['repository']['name'],
                    "url": item['html_url']
                }
                for item in code_results
            ]
        }
    
    elif request.tool == "get_issues":
        repo = request.arguments.get("repo", "")
        state = request.arguments.get("state", "open")
        limit = request.arguments.get("limit", 30)
        
        issues = await github_client.get_repo_issues(repo, state, limit)
        
        return {
            "tool": "get_issues",
            "result": [
                {
                    "number": issue['number'],
                    "title": issue['title'],
                    "state": issue['state'],
                    "created_at": issue['created_at'],
                    "url": issue['html_url'],
                    "body": issue.get('body', '')[:200] + "..." if issue.get('body') else ""
                }
                for issue in issues
            ]
        }
    
    elif request.tool == "get_commits":
        repo = request.arguments.get("repo", "")
        limit = request.arguments.get("limit", 10)
        
        commits = await github_client.get_recent_commits(repo, limit)
        
        return {
            "tool": "get_commits",
            "result": [
                {
                    "sha": commit['sha'][:7],
                    "message": commit['commit']['message'].split('\n')[0],
                    "author": commit['commit']['author']['name'],
                    "date": commit['commit']['author']['date'],
                    "url": commit['html_url']
                }
                for commit in commits
            ]
        }
    
    else:
        return {"error": f"Unknown tool: {request.tool}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)