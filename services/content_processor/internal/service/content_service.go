package service

import (
	"fmt"
	"log"
	"strings"
	"sync"
	"time"

	"github.com/google/uuid"
	"content-processor/internal/models"
	"content-processor/internal/clients"  
)


type ContentService struct {
	llmClient *clients.LLMClient 
	searchClient *clients.SearchClient
}

func NewContentService(llmServiceURL, searchServiceURL string) *ContentService {
	return &ContentService{
		llmClient:    clients.NewLLMClient(llmServiceURL),
		searchClient: clients.NewSearchClient(searchServiceURL),  // Add this
	}
}

func (s *ContentService) ProcessContent(req *models.ProcessingRequest) (*models.ProcessingResponse, error) {
	log.Printf("Processing content for document: %s", req.DocumentID)

	response := &models.ProcessingResponse{
		DocumentID: req.DocumentID,
		Status: "processing",
		ProcessedAt: time.Now(),
	}

	// chunk the document for better processing
	chunks := s.chunkContent(req.Content, 1000) // 1000 chars per chunk
	log.Printf("Split content into %d chunks", len(chunks))

	// Process chunks concurrently
	var wg sync.WaitGroup
	chunkResults := make([]models.ProcessedChunk, len(chunks))
	
	for i, chunk := range chunks {
		wg.Add(1)
		go func(index int, content string) {
			defer wg.Done()
			chunkResults[index] = s.processChunk(content, index)
		}(i, chunk)
	}
	
	wg.Wait()

	// Aggregate results from all chunks
	aggregatedResult := s.aggregateChunkResults(chunkResults)
	
	response.Analysis = aggregatedResult.Analysis
	response.Tasks = aggregatedResult.Tasks
	response.Embeddings = aggregatedResult.Embeddings
	response.Summary = aggregatedResult.Summary
	response.Status = "completed"
	if err := s.indexInSearchService(req.DocumentID, req.Content, aggregatedResult); err != nil {
		log.Printf("Failed to index in search service: %v", err)
	} else {
		log.Printf("Document indexed in search service: %s", req.DocumentID)
	}

	log.Printf("Completed processing document: %s", req.DocumentID)
	return response, nil
}

func (s *ContentService) chunkContent(content string, maxChunkSize int) []string {
	if len(content) < maxChunkSize {
		return []string{content}
	}
	var chunks []string
	words := strings.Fields(content)
	
	var currentChunk strings.Builder

	for _, word := range words {
		// Check if adding this word would exceed the limit
		if currentChunk.Len()+len(word)+1 > maxChunkSize && currentChunk.Len() > 0 {
			chunks = append(chunks, currentChunk.String())
			currentChunk.Reset()
		}
		
		if currentChunk.Len() > 0 {
			currentChunk.WriteString(" ")
		}
		currentChunk.WriteString(word)
	}
	// Add the last chunk
	if currentChunk.Len() > 0 {
		chunks = append(chunks, currentChunk.String())
	}
	
	return chunks
}

// process a single chunk of content
func (s *ContentService) processChunk(content string, chunkIndex int) models.ProcessedChunk {
	chunkID := fmt.Sprintf("chunk_%d_%s", chunkIndex, uuid.New().String()[:8])
	
	log.Printf("Processing chunk %d with LLM service", chunkIndex)
	
	result := models.ProcessedChunk{
		ChunkID: chunkID,
		Content: content,
	}

	// Create channels for concurrent LLM calls
	analysisChan := make(chan map[string]interface{})
	embeddingsChan := make(chan []float64)
	tasksChan := make(chan []map[string]interface{})
	
	// Make concurrent calls to LLM service
	go func() {
		if analysis, err := s.llmClient.AnalyzeContent(content, "general"); err == nil {
			analysisChan <- map[string]interface{}{
				"summary":         analysis.Summary,
				"key_concepts":    analysis.KeyConcepts,
				"entities":        analysis.Entities,
				"themes":          analysis.Themes,
				"difficulty":      analysis.Difficulty,
			}
		} else {
			log.Printf("Analysis failed for chunk %d: %v", chunkIndex, err)
			analysisChan <- map[string]interface{}{"error": err.Error()}
		}
	}()

	go func() {
		if embeddings, err := s.llmClient.CreateEmbeddings(content); err == nil {
			embeddingsChan <- embeddings.Embeddings
		} else {
			log.Printf("Embeddings failed for chunk %d: %v", chunkIndex, err)
			embeddingsChan <- []float64{}
		}
	}()

	go func() {
		if tasks, err := s.llmClient.ExtractTasks(content); err == nil {
			tasksChan <- tasks.Tasks
		} else {
			log.Printf("Task extraction failed for chunk %d: %v", chunkIndex, err)
			tasksChan <- []map[string]interface{}{}
		}
	}()

	// Collect results
	result.Analysis = <-analysisChan
	result.Embeddings = <-embeddingsChan
	result.Tasks = <-tasksChan

	return result
}

// remove duplicate strings from a slice
func (s *ContentService) removeDuplicateStrings(slice []string) []string {
	seen := make(map[string]bool)
	var result []string
	
	for _, item := range slice {
		if !seen[item] {
			seen[item] = true
			result = append(result, item)
		}
	}
	
	return result
}

// combine results from multiple chunks
func (s *ContentService) aggregateChunkResults(chunks []models.ProcessedChunk) *models.ProcessingResponse {
	var allConcepts []string
	var allTasks []map[string]interface{}
	var summaries []string
	
	// Collect all embeddings and average them
	var avgEmbeddings []float64
	embeddingCount := 0
	
	for _, chunk := range chunks {
		// type assert the Analysis field
		if keyConcepts, ok := chunk.Analysis["key_concepts"]; ok {
			// Try []string first
			if conceptsSlice, ok := keyConcepts.([]string); ok {
				allConcepts = append(allConcepts, conceptsSlice...)
			} else if conceptsInterface, ok := keyConcepts.([]interface{}); ok {
				// Fallback to []interface{} if needed
				for _, concept := range conceptsInterface {
					if conceptStr, ok := concept.(string); ok {
						allConcepts = append(allConcepts, conceptStr)
					}
				}
			}
		}
		
		// Get summary
		if summary, ok := chunk.Analysis["summary"]; ok {
			if summaryStr, ok := summary.(string); ok {
				summaries = append(summaries, summaryStr)
			}
		}
		
		// Collect tasks
		allTasks = append(allTasks, chunk.Tasks...)
		
		// Average embeddings
		if len(chunk.Embeddings) > 0 {
			if len(avgEmbeddings) == 0 {
				avgEmbeddings = make([]float64, len(chunk.Embeddings))
			}
			for i, val := range chunk.Embeddings {
				if i < len(avgEmbeddings) { 
					avgEmbeddings[i] += val
				}
			}
			embeddingCount++
		}
	}
	
	// Finalize average embeddings
	if embeddingCount > 0 {
		for i := range avgEmbeddings {
			avgEmbeddings[i] /= float64(embeddingCount)
		}
	}
	
	return &models.ProcessingResponse{
		Analysis: map[string]interface{}{
			"key_concepts": s.removeDuplicateStrings(allConcepts),
			"total_chunks": len(chunks),
		},
		Tasks: map[string]interface{}{
			"all_tasks": allTasks,
			"count":     len(allTasks),
		},
		Embeddings: avgEmbeddings,
		Summary:    strings.Join(summaries, " "),
	}
}

// indexInSearchService sends processed document to Search Service
func (s *ContentService) indexInSearchService(docID string, content string, result *models.ProcessingResponse) error {
	// Prepare metadata from analysis
	metadata := make(map[string]interface{})
	
	if result.Analysis != nil {
		for key, value := range result.Analysis {
			metadata[key] = value
		}
	}
	// Add tasks to metadata
	if result.Tasks != nil {
		for key, value := range result.Tasks {
			metadata[key] = value
		}
	}
	
	// Add summary
	metadata["summary"] = result.Summary

	indexReq := &clients.IndexDocumentRequest{
		DocumentID: docID,
		Content:    content,
		Embeddings: result.Embeddings,
		Metadata:   metadata,
	}

	return s.searchClient.IndexDocument(indexReq)
}