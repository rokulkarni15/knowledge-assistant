import asyncio
import logging
from contextlib import asynccontextmanager

from mcp.server import Server
from mcp.types import Resource, TextContent, Tool
import mcp.types as types

from clients.github_client import GithubClient
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

github_client = GithubClient(settings.github_token, settings.github_username)

mcp_server = Server("github-mcp")

@mcp_server.list_resources()
async def list_resources() -> list[Resource]:
    """List available GitHub repositories as MCP resources"""
    logger.info("Listing GitHub repositories")
    
    repos = await github_client.get_user_repos(limit=50)
    
    resources = [
        Resource(
            uri=f"github://repo/{repo['name']}",
            name=repo['name'],
            mimeType="text/plain",
            description=repo.get('description', 'No description')
        )
        for repo in repos
    ]
    
    logger.info(f"Found {len(resources)} repositories")
    return resources

@mcp_server.read_resource()
async def read_resource(uri: str) -> str:
    """Read a specific GitHub resource"""
    logger.info(f"Reading resource: {uri}")
    
    if uri.startswith("github://repo/"):
        repo_name = uri.replace("github://repo/", "")
        
        # Get README content
        readme = await github_client.get_repo_readme(repo_name)
        
        if readme:
            return readme
        else:
            return f"Repository: {repo_name}\nNo README available"
    
    return f"Unknown resource type: {uri}"

@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """List available GitHub tools"""
    return [
        Tool(
            name="search_repos",
            description="Search GitHub repositories by query",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for repositories"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="search_code",
            description="Search code across all repositories",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for code"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_issues",
            description="Get issues from a specific repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo": {
                        "type": "string",
                        "description": "Repository name"
                    },
                    "state": {
                        "type": "string",
                        "description": "Issue state: open, closed, or all",
                        "default": "open"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 30
                    }
                },
                "required": ["repo"]
            }
        ),
        Tool(
            name="get_commits",
            description="Get recent commits from a repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo": {
                        "type": "string",
                        "description": "Repository name"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of commits",
                        "default": 10
                    }
                },
                "required": ["repo"]
            }
        )
    ]

@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute GitHub tools"""
    logger.info(f"Calling tool: {name} with args: {arguments}")
    
    if name == "search_repos":
        query = arguments.get("query", "")
        limit = arguments.get("limit", 10)
        
        repos = await github_client.search_repositories(query, limit)
        
        result = "Found repositories:\n\n"
        for repo in repos:
            result += f"- {repo['name']}: {repo.get('description', 'No description')}\n"
            result += f"  Language: {repo.get('language', 'Unknown')}\n"
            result += f"  Stars: {repo.get('stargazers_count', 0)}\n"
            result += f"  URL: {repo.get('html_url')}\n\n"
        
        return [TextContent(type="text", text=result)]
    
    elif name == "search_code":
        query = arguments.get("query", "")
        limit = arguments.get("limit", 10)
        
        code_results = await github_client.search_code(query, limit)
        
        result = "Found code:\n\n"
        for item in code_results:
            result += f"- {item['name']} in {item['repository']['name']}\n"
            result += f"  Path: {item['path']}\n"
            result += f"  URL: {item['html_url']}\n\n"
        
        return [TextContent(type="text", text=result)]
    
    elif name == "get_issues":
        repo = arguments.get("repo", "")
        state = arguments.get("state", "open")
        limit = arguments.get("limit", 30)
        
        issues = await github_client.get_repo_issues(repo, state, limit)
        
        result = f"Issues in {repo} ({state}):\n\n"
        for issue in issues:
            result += f"- #{issue['number']}: {issue['title']}\n"
            result += f"  State: {issue['state']}\n"
            result += f"  Created: {issue['created_at']}\n"
            result += f"  URL: {issue['html_url']}\n\n"
        
        return [TextContent(type="text", text=result)]
    
    elif name == "get_commits":
        repo = arguments.get("repo", "")
        limit = arguments.get("limit", 10)
        
        commits = await github_client.get_recent_commits(repo, limit)
        
        result = f"Recent commits in {repo}:\n\n"
        for commit in commits:
            msg = commit['commit']['message'].split('\n')[0]  # First line
            result += f"- {commit['sha'][:7]}: {msg}\n"
            result += f"  Author: {commit['commit']['author']['name']}\n"
            result += f"  Date: {commit['commit']['author']['date']}\n\n"
        
        return [TextContent(type="text", text=result)]
    
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

# Run the MCP server
async def main():
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.run(
            read_stream,
            write_stream,
            mcp_server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())