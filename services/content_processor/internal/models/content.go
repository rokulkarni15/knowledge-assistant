package models

import (
	"time"
)

// ProcessingRequest represents a file processing request
type ProcessingRequest struct {
	DocumentID string            `json:"document_id"`
	Content    string            `json:"content"`
	FileType   string            `json:"file_type"`
	Metadata   map[string]string `json:"metadata,omitempty"`
}

// ProcessingResponse represents the response from processing
type ProcessingResponse struct {
	DocumentID   string                 `json:"document_id"`
	Status       string                 `json:"status"`
	ProcessedAt  time.Time              `json:"processed_at"`
	Analysis     map[string]interface{} `json:"analysis,omitempty"`
	Tasks        map[string]interface{} `json:"tasks,omitempty"`
	Embeddings   []float64              `json:"embeddings,omitempty"`
	Summary      string                 `json:"summary,omitempty"`
	ErrorMessage string                 `json:"error_message,omitempty"`
}

// LLMAnalysisResponse represents response from LLM service analysis
type LLMAnalysisResponse struct {
	Summary       string                            `json:"summary"`
	KeyConcepts   []string                          `json:"key_concepts"`
	Entities      map[string][]string              `json:"entities"`
	Tasks         []map[string]interface{}         `json:"tasks"`
	Themes        []string                          `json:"themes"`
	Difficulty    string                            `json:"difficulty_level"`
	Model         string                            `json:"model"`
}

// LLMEmbeddingResponse represents response from LLM service embeddings
type LLMEmbeddingResponse struct {
	Embeddings     []float64 `json:"embeddings"`
	Dimensions     int       `json:"dimensions"`
	Model          string    `json:"model"`
	EmbeddingModel string    `json:"embedding_model"`
}

// LLMTaskResponse represents response from LLM service tasks
type LLMTaskResponse struct {
	Tasks         []map[string]interface{} `json:"tasks"`
	EstimatedTime string                   `json:"estimated_time"`
	Model         string                   `json:"model"`
}

// ProcessedChunk represents a processed chunk of content
type ProcessedChunk struct {
	ChunkID    string                 `json:"chunk_id"`
	Content    string                 `json:"content"`
	Analysis   map[string]interface{} `json:"analysis"`
	Embeddings []float64              `json:"embeddings"`
	Tasks      []map[string]interface{} `json:"tasks"`
}