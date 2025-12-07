package service

import (
	"encoding/json"
	"fmt"
	"log"
	"time"

	"search-service/internal/storage"
	"search-service/internal/clients"
)

type SearchService struct {
	vectorStore *storage.VectorStore
	llmClient   *clients.LLMClient
	redisClient *clients.RedisClient
}

func NewSearchService(llmServiceURL string, redisAddr string) *SearchService {
	return &SearchService{
		vectorStore: storage.NewVectorStore(),
		llmClient:   clients.NewLLMClient(llmServiceURL),
		redisClient: clients.NewRedisClient(redisAddr),
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

	// Check cache for search results
	cacheKey := s.redisClient.MakeKey("search", query, fmt.Sprintf("%d", limit))
	
	if cached, err := s.redisClient.Get(cacheKey); err == nil && cached != nil {
		var results []*storage.SearchResult
		if err := json.Unmarshal(cached, &results); err == nil {
			log.Printf("Cache HIT: Returning cached search results")
			return results, nil
		}
	}

	// Generate query embedding with caching
	queryEmbedding, err := s.getQueryEmbeddingCached(query)
	if err != nil {
		return nil, fmt.Errorf("failed to create query embedding: %w", err)
	}

	// Perform similarity search
	results := s.vectorStore.SimilaritySearch(queryEmbedding, limit)

	// Cache the search results (10 minutes)
	if err := s.redisClient.Set(cacheKey, results, 10*time.Minute); err != nil {
		log.Printf("Failed to cache search results: %v", err)
	}

	log.Printf("Found %d results", len(results))
	return results, nil
}

func (s *SearchService) getQueryEmbeddingCached(query string) ([]float64, error) {
	// Check cache for query embedding
	cacheKey := s.redisClient.MakeKey("query_emb", query)
	
	if cached, err := s.redisClient.Get(cacheKey); err == nil && cached != nil {
		var embedding []float64
		if err := json.Unmarshal(cached, &embedding); err == nil {
			log.Printf("Cache HIT: Using cached query embedding")
			return embedding, nil
		}
	}

	// Cache miss - generate embedding via LLM service
	log.Printf("Cache MISS: Generating query embedding via LLM")
	queryEmbedding, err := s.llmClient.CreateEmbeddings(query)
	if err != nil {
		return nil, err
	}

	// Cache the query embedding (1 hour)
	if err := s.redisClient.Set(cacheKey, queryEmbedding, 1*time.Hour); err != nil {
		log.Printf("Failed to cache query embedding: %v", err)
	}

	return queryEmbedding, nil
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