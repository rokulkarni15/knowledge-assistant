from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class EntityExtractionModel(BaseModel):
    """Structured model for entity extraction"""
    people: List[str] = Field(default_factory=list, description="List of people mentioned")
    organizations: List[str] = Field(default_factory=list, description="List of organizations")
    concepts: List[str] = Field(default_factory=list, description="Key topics or concepts")
    summary: str = Field(description="Brief summary in one sentence")

class TaskModel(BaseModel):
    """Single task model"""
    task: str = Field(description="Specific action to take")
    priority: str = Field(description="high, medium, or low")
    category: str = Field(default="general", description="Task category")
    deadline: Optional[str] = Field(default=None, description="Deadline if mentioned")
    estimated_hours: int = Field(default=1, description="Estimated hours to complete")

class TaskExtractionModel(BaseModel):
    """Structured model for task extraction"""
    tasks: List[TaskModel] = Field(default_factory=list, description="List of actionable tasks")
    estimated_time: str = Field(description="Total estimated time")

class EntityDict(BaseModel):
    """Nested entity structure"""
    people: List[str] = Field(default_factory=list)
    organizations: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
    locations: List[str] = Field(default_factory=list)

class DocumentAnalysisModel(BaseModel):
    """Structured model for document analysis"""
    summary: str = Field(description="Brief summary in 1-2 sentences")
    key_concepts: List[str] = Field(default_factory=list, description="Main concepts")
    entities: EntityDict = Field(default_factory=EntityDict, description="Extracted entities")
    tasks: List[TaskModel] = Field(default_factory=list, description="Actionable tasks")
    themes: List[str] = Field(default_factory=list, description="Main themes")
    difficulty_level: str = Field(default="intermediate", description="beginner, intermediate, or advanced")