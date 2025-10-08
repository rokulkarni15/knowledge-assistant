package clients

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"time"

	"content-processor/internal/models"
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

// call the LLM service analysis endpoint
func (c *LLMClient) AnalyzeContent(text string, analysisType string) (*models.LLMAnalysisResponse, error) {
	payload := map[string]interface{}{
		"text":          text,
		"analysis_type": analysisType,
	}

	var response models.LLMAnalysisResponse
	if err := c.makeRequest("POST", "/chat/analyze", payload, &response); err != nil {
		return nil, fmt.Errorf("failed to analyze content: %w", err)
	}

	return &response, nil
}

// call the LLM service embeddings endpoint
func (c *LLMClient) CreateEmbeddings(text string) (*models.LLMEmbeddingResponse, error) {
	payload := map[string]string{
		"text": text,
	}

	var response models.LLMEmbeddingResponse
	if err := c.makeRequest("POST", "/chat/embeddings", payload, &response); err != nil {
		return nil, fmt.Errorf("failed to create embeddings: %w", err)
	}

	return &response, nil
}

// call the LLM service task extraction endpoint
func (c *LLMClient) ExtractTasks(text string) (*models.LLMTaskResponse, error) {
	payload := map[string]string{
		"text": text,
	}

	var response models.LLMTaskResponse
	if err := c.makeRequest("POST", "/chat/tasks", payload, &response); err != nil {
		return nil, fmt.Errorf("failed to extract tasks: %w", err)
	}

	return &response, nil
}

// helper method to make HTTP requests to LLM service
func (c *LLMClient) makeRequest(method, endpoint string, payload interface{}, response interface{}) error {
	jsonData, err := json.Marshal(payload)
	if err != nil {
		return fmt.Errorf("failed to marshal payload: %w", err)
	}

	url := c.BaseURL + endpoint
	req, err := http.NewRequest(method, url, bytes.NewBuffer(jsonData))
	if err != nil {
		return fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")

	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return fmt.Errorf("failed to make request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("LLM service returned status %d", resp.StatusCode)
	}

	if err := json.NewDecoder(resp.Body).Decode(response); err != nil {
		return fmt.Errorf("failed to decode response: %w", err)
	}

	return nil
}

