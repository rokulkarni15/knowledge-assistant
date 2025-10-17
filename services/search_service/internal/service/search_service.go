package service

import (
	"fmt"
	"log"

	"search-service/internal/storage"
	"search-service/internal/clients"
)

type SearchService struct {
	vectorStore *storage.VectorStore
	llmClient   *clients.LLMClient
}

func NewSearchService(llmServiceURL string) *SearchService {
	return &SearchService{
		vectorStore: storage.NewVectorStore(),
		llmClient:   clients.NewLLMClient(llmServiceURL),
	}
}

// indexes a document with its embeddings
func (s *SearchService) IndexDocument(req *storage.IndexRequest) error {
	log.Printf("Indexing document: %s", req.DocumentID)

	doc := &storage.Document{
		ID:         req.DocumentID,
		Content:    req.Content,
		Embeddings: req.Embeddings,
		Metadata:   req.Metadata,
	}

	if err := s.vectorStore.Store(doc); err != nil {
		return fmt.Errorf("failed to store document: %w", err)
	}

	log.Printf("Document indexed: %s", req.DocumentID)
	return nil
}

// performs semantic search
func (s *SearchService) Search(query string, limit int) ([]*storage.SearchResult, error) {
	log.Printf("Searching for: %s (limit: %d)", query, limit)

	// Generate query embedding
	queryEmbedding, err := s.llmClient.CreateEmbeddings(query)
	if err != nil {
		return nil, fmt.Errorf("failed to create query embedding: %w", err)
	}

	// Perform similarity search
	results := s.vectorStore.SimilaritySearch(queryEmbedding, limit)

	log.Printf("Found %d results", len(results))
	return results, nil
}

// retrieves a specific document
func (s *SearchService) GetDocument(docID string) (*storage.Document, error) {
	return s.vectorStore.Get(docID)
}

// removes a document from the index
func (s *SearchService) DeleteDocument(docID string) error {
	return s.vectorStore.Delete(docID)
}

// returns index statistics
func (s *SearchService) GetStats() map[string]interface{} {
	return map[string]interface{}{
		"total_documents": s.vectorStore.Count(),
		"indexed_at":      "in-memory",
	}
}