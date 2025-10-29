package clients

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

type SearchClient struct {
	BaseURL    string
	HTTPClient *http.Client
}

func NewSearchClient(baseURL string) *SearchClient {
	return &SearchClient{
		BaseURL: baseURL,
		HTTPClient: &http.Client{
			Timeout: 30 * time.Second,
		},
	}
}

// match Search Service's IndexRequest
type IndexDocumentRequest struct {
	DocumentID string                 `json:"document_id"`
	Content    string                 `json:"content"`
	Embeddings []float64              `json:"embeddings"`
	Metadata   map[string]interface{} `json:"metadata"`
}

// sends processed document to Search Service for indexing
func (c *SearchClient) IndexDocument(req *IndexDocumentRequest) error {
	jsonData, err := json.Marshal(req)
	if err != nil {
		return fmt.Errorf("failed to marshal request: %w", err)
	}

	url := c.BaseURL + "/api/v1/index"
	httpReq, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonData))
	if err != nil {
		return fmt.Errorf("failed to create request: %w", err)
	}

	httpReq.Header.Set("Content-Type", "application/json")

	resp, err := c.HTTPClient.Do(httpReq)
	if err != nil {
		return fmt.Errorf("failed to call search service: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("search service returned status %d", resp.StatusCode)
	}

	return nil
}