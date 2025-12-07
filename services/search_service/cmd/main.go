package main

import (
	"log"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
	"search-service/internal/api"
	"search-service/internal/service"
)

func main() {
	// Get LLM service URL from environment or use default
	llmServiceURL := os.Getenv("LLM_SERVICE_URL")
	if llmServiceURL == "" {
		llmServiceURL = "http://localhost:8002"
	}
	redisAddr := os.Getenv("REDIS_ADDR")
	if redisAddr == "" {
		redisAddr = "localhost:6379"
	}

	// Initialize services
	searchService := service.NewSearchService(llmServiceURL, redisAddr)
	handlers := api.NewHandlers(searchService)

	// Setup Gin router
	router := gin.Default()

	// Health check
	router.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status":  "healthy",
			"service": "search-service",
			"version": "0.1.0",
		})
	})

	router.GET("/", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"message": "Search Service",
			"docs":    "/docs",
		})
	})

	// Register API routes
	api.RegisterRoutes(router, handlers)

	log.Println("Search Service starting on :8004")
	if err := router.Run(":8004"); err != nil {
		log.Fatal("Failed to start server:", err)
	}
}