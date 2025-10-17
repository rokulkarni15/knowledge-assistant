package clients

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

type LLMClient struct {
	BaseURL    string
	HTTPClient *http.Client
}

func NewLLMClient(baseURL string) *LLMClient {
	return &LLMClient{
		BaseURL: baseURL,
		HTTPClient: &http.Client{
			Timeout: 30 * time.Second,
		},
	}
}

// EmbeddingResponse matches LLM service response
type EmbeddingResponse struct {
	Embeddings     []float64 `json:"embeddings"`
	Dimensions     int       `json:"dimensions"`
	Model          string    `json:"model"`
	EmbeddingModel string    `json:"embedding_model"`
}

// calls LLM service to generate embeddings
func (c *LLMClient) CreateEmbeddings(text string) ([]float64, error) {
	payload := map[string]string{
		"text": text,
	}

	jsonData, err := json.Marshal(payload)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal payload: %w", err)
	}

	url := c.BaseURL + "/chat/embeddings"
	req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")

	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to make request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("LLM service returned status %d", resp.StatusCode)
	}

	var embeddingResp EmbeddingResponse
	if err := json.NewDecoder(resp.Body).Decode(&embeddingResp); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}

	return embeddingResp.Embeddings, nil
}