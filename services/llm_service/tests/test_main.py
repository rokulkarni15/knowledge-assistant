import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from llm_service.main import app

client = TestClient(app)

# Basic endpoint tests
def test_health_check():
    """Test LLM service health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "llm-service"

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "LLM Service" in data["message"]

def test_chat_health_endpoint():
    """Test chat health endpoint"""
    response = client.get("/chat/health")
    assert response.status_code == 200
    data = response.json()
    assert "ollama_available" in data
    assert "model" in data

# Chat endpoint tests
@patch('llm_service.core.services.chat_service.ChatService.chat')
def test_chat_endpoint_success(mock_chat):
    """Test successful chat request"""
    mock_chat.return_value = "This is a test response from Ollama"
    
    response = client.post("/chat/", json={"message": "Hello"})
    
    assert response.status_code == 200
    data = response.json()
    assert data["response"] == "This is a test response from Ollama"
    assert data["model"] == "phi3:mini"

@patch('llm_service.core.services.chat_service.ChatService.chat')
def test_chat_endpoint_with_context(mock_chat):
    """Test chat request with context"""
    mock_chat.return_value = "Response with context"
    
    response = client.post(
        "/chat/",
        json={
            "message": "What did I learn?",
            "context": ["Document about microservices", "Notes about Python"]
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["response"] == "Response with context"

def test_chat_endpoint_missing_message():
    """Test chat request with missing message field"""
    response = client.post("/chat/", json={})
    assert response.status_code == 422

# Extract endpoint tests
@patch('llm_service.core.services.chat_service.ChatService.extract_entities')
def test_extract_endpoint_success(mock_extract):
    """Test successful entity extraction"""
    mock_extract.return_value = {
        "people": ["John"],
        "organizations": ["Microsoft"],
        "concepts": ["AI projects"],
        "summary": "John works at Microsoft on AI projects"
    }
    
    response = client.post(
        "/chat/extract",
        json={"text": "John works at Microsoft on AI projects"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["entities"]["people"] == ["John"]
    assert data["entities"]["organizations"] == ["Microsoft"]
    assert data["model"] == "phi3:mini"

def test_extract_endpoint_missing_text():
    """Test extract request with missing text field"""
    response = client.post("/chat/extract", json={})
    assert response.status_code == 422

# Embeddings endpoint tests
@patch('llm_service.core.services.chat_service.ChatService.create_embeddings')
def test_embeddings_endpoint_success(mock_embeddings):
    """Test successful embeddings generation"""
    mock_embeddings.return_value = [0.1, -0.2, 0.3, 0.4] * 256  # 1024 dimensions
    
    response = client.post(
        "/chat/embeddings",
        json={"text": "Machine learning and AI"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["embeddings"]) == 1024
    assert data["dimensions"] == 1024
    assert data["model"] == "phi3:mini"

def test_embeddings_endpoint_missing_text():
    """Test embeddings request with missing text field"""
    response = client.post("/chat/embeddings", json={})
    assert response.status_code == 422

@patch('llm_service.core.services.chat_service.ChatService.create_embeddings')
def test_embeddings_endpoint_error_handling(mock_embeddings):
    """Test embeddings endpoint error handling"""
    mock_embeddings.side_effect = Exception("Ollama connection failed")
    
    response = client.post(
        "/chat/embeddings",
        json={"text": "test text"}
    )
    
    assert response.status_code == 500

# Document analysis endpoint tests
@patch('llm_service.core.services.chat_service.ChatService.analyze_document')
def test_analyze_endpoint_success(mock_analyze):
    """Test successful document analysis"""
    mock_analyze.return_value = {
        "summary": "A meeting about microservices project",
        "key_concepts": ["microservices", "architecture"],
        "entities": {
            "people": ["John", "Sarah"],
            "organizations": ["Company"],
            "technologies": ["Go", "Python"],
            "locations": []
        },
        "tasks": [{"task": "Implement authentication", "priority": "high"}],
        "themes": ["software development"],
        "difficulty_level": "intermediate"
    }
    
    response = client.post(
        "/chat/analyze",
        json={
            "text": "We discussed microservices. John will use Go, Sarah will use Python.",
            "analysis_type": "meeting_notes"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["summary"] == "A meeting about microservices project"
    assert data["key_concepts"] == ["microservices", "architecture"]
    assert data["entities"]["people"] == ["John", "Sarah"]
    assert len(data["tasks"]) == 1
    assert data["model"] == "phi3:mini"

def test_analyze_endpoint_missing_text():
    """Test analyze request with missing text field"""
    response = client.post("/chat/analyze", json={})
    assert response.status_code == 422

# Task extraction endpoint tests
@patch('llm_service.core.services.chat_service.ChatService.extract_tasks')
def test_tasks_endpoint_success(mock_tasks):
    """Test successful task extraction"""
    mock_tasks.return_value = {
        "tasks": [
            {
                "task": "Review architecture document",
                "priority": "high",
                "category": "documentation",
                "deadline": None,
                "estimated_hours": 2
            },
            {
                "task": "Schedule team meeting",
                "priority": "medium",
                "category": "coordination",
                "deadline": None,
                "estimated_hours": 1
            }
        ],
        "estimated_time": "3 hours"
    }
    
    response = client.post(
        "/chat/tasks",
        json={"text": "I need to review the architecture document and schedule a team meeting"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["tasks"]) == 2
    assert data["tasks"][0]["task"] == "Review architecture document"
    assert data["tasks"][0]["priority"] == "high"
    assert data["estimated_time"] == "3 hours"
    assert data["model"] == "phi3:mini"

def test_tasks_endpoint_missing_text():
    """Test tasks request with missing text field"""
    response = client.post("/chat/tasks", json={})
    assert response.status_code == 422

# Summarization endpoint tests
@patch('llm_service.core.services.chat_service.ChatService.summarize_text')
def test_summarize_endpoint_success(mock_summarize):
    """Test successful text summarization"""
    mock_summarize.return_value = {
        "summary": "Microservices offer scalability but add complexity."
    }
    
    long_text = "Microservices architecture is a design approach where applications are built as small services. " * 10
    
    response = client.post(
        "/chat/summarize",
        json={"text": long_text, "max_length": 100}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["summary"] == "Microservices offer scalability but add complexity."
    assert data["original_length"] == len(long_text)
    assert data["summary_length"] == len(data["summary"])
    assert data["compression_ratio"] < 1.0
    assert data["model"] == "phi3:mini"

def test_summarize_endpoint_missing_text():
    """Test summarize request with missing text field"""
    response = client.post("/chat/summarize", json={})
    assert response.status_code == 422

def test_summarize_endpoint_with_defaults():
    """Test summarize request with default parameters"""
    with patch('llm_service.core.services.chat_service.ChatService.summarize_text') as mock_summarize:
        mock_summarize.return_value = {"summary": "Short summary"}
        
        response = client.post(
            "/chat/summarize",
            json={"text": "Some long text here"}
        )
        
        assert response.status_code == 200
        # Verify default max_length was used (200)
        mock_summarize.assert_called_once()