"""Prompts for tool/MCP selection"""

TOOL_SELECTION_PROMPT = """Analyze this user question and determine which GitHub data sources would help answer it.

User question: {question}

Available GitHub tools:
- github_repos: Search or list user's GitHub repositories
- github_code: Search for code examples in user's repositories  
- github_issues: Get issues/bugs from user's repositories
- github_commits: Get recent commits from repositories
- none: GitHub data not needed

Return ONLY a JSON list of needed tools. Examples:
- ["github_repos"] 
- ["github_code"]
- ["github_repos", "github_issues"]
- []

Consider the question needs GitHub data if it mentions:
- "my projects", "my repos", "my code", "my repositories"
- "what have I built", "what am I working on"
- "my issues", "my bugs", "my commits"
- "code examples", "show me code"

JSON list:"""

def build_tool_selection_prompt(question: str) -> str:
    """Build prompt for tool selection"""
    return TOOL_SELECTION_PROMPT.format(question=question)
