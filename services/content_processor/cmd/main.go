package main

import (
	"log"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
	"content-processor/internal/api"
	"content-processor/internal/service"
)

func main() {
	// Get service URLs from environment or use defaults
	llmServiceURL := os.Getenv("LLM_SERVICE_URL")
	if llmServiceURL == "" {
		llmServiceURL = "http://localhost:8002"
	}

	searchServiceURL := os.Getenv("SEARCH_SERVICE_URL")
	if searchServiceURL == "" {
		searchServiceURL = "http://localhost:8004"
	}

	// Initialize services with both URLs
	contentService := service.NewContentService(llmServiceURL, searchServiceURL)
	handlers := api.NewHandlers(contentService)

	// Setup Gin router
	router := gin.Default()
	router.MaxMultipartMemory = 10 << 20

	// Health check
	router.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status":  "healthy",
			"service": "content-processor",
			"version": "0.1.0",
		})
	})

	router.GET("/", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"message": "📄 Content Processor Service",
			"docs":    "/docs",
		})
	})

	// Register API routes
	api.RegisterRoutes(router, handlers)

	log.Println("Content Processor starting on :8003")
	if err := router.Run(":8003"); err != nil {
		log.Fatal("Failed to start server:", err)
	}
}