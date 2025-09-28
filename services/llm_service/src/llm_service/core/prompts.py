"""Prompt templates for LLM operations"""

SYSTEM_PROMPT = """You are a helpful assistant for a personal knowledge management system. Be concise and helpful."""

CONTEXT_PROMPT_TEMPLATE = """Context from documents:
{context}"""

# Entity extraction prompt
ENTITY_EXTRACTION_PROMPT = """Extract key information from this text and return ONLY a JSON object:

{{
  "people": ["list of people mentioned"],
  "organizations": ["list of companies/organizations"],
  "concepts": ["key topics or concepts"],
  "summary": "brief summary in one sentence"
}}

Text: {text}

JSON:"""

# Task extraction prompt
TASK_EXTRACTION_PROMPT = """Extract actionable tasks and TODOs from this text.
Return ONLY a JSON object with this structure:

{{
  "tasks": [
    {{
      "task": "specific action to take",
      "priority": "high/medium/low",
      "category": "category name",
      "deadline": null,
      "estimated_hours": 1
    }}
  ],
  "estimated_time": "total estimated time"
}}

Text: {text}

JSON:"""

# Summarization prompt
SUMMARIZATION_PROMPT = """Summarize this text in about {max_length} characters. Be concise and capture the main points:

Text: {text}

Summary:"""

# Document analysis prompt
DOCUMENT_ANALYSIS_PROMPT = """Analyze this {analysis_type} text and extract key information.
Return ONLY a JSON object with this exact structure:

{{
  "summary": "brief summary in 1-2 sentences",
  "key_concepts": ["list of main concepts"],
  "entities": {{
    "people": ["list of people"],
    "organizations": ["list of organizations"],
    "technologies": ["list of technologies/tools"],
    "locations": ["list of places"]
  }},
  "tasks": [
    {{"task": "action item", "priority": "high/medium/low", "deadline": null}}
  ],
  "themes": ["list of main themes"],
  "difficulty_level": "beginner/intermediate/advanced"
}}

Text: {text}

JSON:"""


def build_chat_messages(message: str, context: list = None) -> list:
    """Build messages array for chat completion"""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    if context:
        context_text = "\n".join(context[:3])
        messages.append({
            "role": "system",
            "content": CONTEXT_PROMPT_TEMPLATE.format(context=context_text)
        })
    
    messages.append({"role": "user", "content": message})
    return messages

def build_extraction_prompt(text: str) -> str:
    """Build prompt for entity extraction"""
    return ENTITY_EXTRACTION_PROMPT.format(text=text)

def build_task_extraction_prompt(text: str) -> str:
    """Build prompt for task extraction"""
    return TASK_EXTRACTION_PROMPT.format(text=text)

def build_summarization_prompt(text: str, max_length: int) -> str:
    """Build prompt for summarization"""
    return SUMMARIZATION_PROMPT.format(text=text, max_length=max_length)

def build_analysis_prompt(text: str, analysis_type: str) -> str:
    """Build prompt for document analysis"""
    return DOCUMENT_ANALYSIS_PROMPT.format(text=text, analysis_type=analysis_type)
