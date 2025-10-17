package storage

import (
	"time"
)

// represents a stored document with embeddings
type Document struct {
	ID         string                 `json:"id"`
	Content    string                 `json:"content"`
	Embeddings []float64              `json:"embeddings"`
	Metadata   map[string]interface{} `json:"metadata"`
	IndexedAt  time.Time              `json:"indexed_at"`
}

// represents a search result with similarity score
type SearchResult struct {
	DocumentID string                 `json:"document_id"`
	Content    string                 `json:"content"`
	Score      float64                `json:"score"`
	Metadata   map[string]interface{} `json:"metadata"`
}

// represents a document indexing request
type IndexRequest struct {
	DocumentID string                 `json:"document_id"`
	Content    string                 `json:"content"`
	Embeddings []float64              `json:"embeddings"`
	Metadata   map[string]interface{} `json:"metadata"`
}

// represents a search query
type SearchQuery struct {
	Query string `json:"query"`
	Limit int    `json:"limit"`
}