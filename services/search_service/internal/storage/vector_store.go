package storage

import (
	"fmt"
	"sort"
	"sync"
	"time"

	"search-service/pkg/vector"
)

// VectorStore manages document vectors and similarity search
type VectorStore struct {
	documents map[string]*Document
	mutex     sync.RWMutex
}

// creates a new vector store
func NewVectorStore() *VectorStore {
	return &VectorStore{
		documents: make(map[string]*Document),
	}
}

// stores a document with its embeddings
func (vs *VectorStore) Store(doc *Document) error {
	vs.mutex.Lock()
	defer vs.mutex.Unlock()

	doc.IndexedAt = time.Now()
	vs.documents[doc.ID] = doc

	return nil
}

// retrieves a document by ID
func (vs *VectorStore) Get(docID string) (*Document, error) {
	vs.mutex.RLock()
	defer vs.mutex.RUnlock()

	doc, exists := vs.documents[docID]
	if !exists {
		return nil, fmt.Errorf("document not found: %s", docID)
	}

	return doc, nil
}

// removes a document from the store
func (vs *VectorStore) Delete(docID string) error {
	vs.mutex.Lock()
	defer vs.mutex.Unlock()

	if _, exists := vs.documents[docID]; !exists {
		return fmt.Errorf("document not found: %s", docID)
	}

	delete(vs.documents, docID)
	return nil
}

// finds documents similar to the query vector
func (vs *VectorStore) SimilaritySearch(queryEmbedding []float64, limit int) []*SearchResult {
	vs.mutex.RLock()
	defer vs.mutex.RUnlock()

	var results []*SearchResult

	// Calculate similarity with each document
	for docID, doc := range vs.documents {
		if len(doc.Embeddings) == 0 {
			continue
		}

		score := vector.CosineSimilarity(queryEmbedding, doc.Embeddings)

		// Only include results above threshold
		if score > 0.1 {
			// Truncate content for preview
			content := doc.Content
			if len(content) > 200 {
				content = content[:200] + "..."
			}

			results = append(results, &SearchResult{
				DocumentID: docID,
				Content:    content,
				Score:      score,
				Metadata:   doc.Metadata,
			})
		}
	}

	// Sort by score descending
	sort.Slice(results, func(i, j int) bool {
		return results[i].Score > results[j].Score
	})

	// Limit results
	if len(results) > limit {
		results = results[:limit]
	}

	return results
}

// returns all documents
func (vs *VectorStore) GetAll() []*Document {
	vs.mutex.RLock()
	defer vs.mutex.RUnlock()

	docs := make([]*Document, 0, len(vs.documents))
	for _, doc := range vs.documents {
		docs = append(docs, doc)
	}

	return docs
}

// returns the number of indexed documents
func (vs *VectorStore) Count() int {
	vs.mutex.RLock()
	defer vs.mutex.RUnlock()

	return len(vs.documents)
}