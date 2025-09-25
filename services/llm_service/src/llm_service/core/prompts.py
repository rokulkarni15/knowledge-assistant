"""Prompt templates for LLM operations"""

SYSTEM_PROMPT = """You are a helpful assistant for a personal knowledge management system. Be concise and helpful."""

CONTEXT_PROMPT_TEMPLATE = """Context from documents:
{context}"""

ENTITY_EXTRACTION_PROMPT = """Extract key information from this text and return ONLY a JSON object:

{{
  "people": ["list of people mentioned"],
  "organizations": ["list of companies/organizations"],
  "concepts": ["key topics or concepts"],
  "summary": "brief summary in one sentence"
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