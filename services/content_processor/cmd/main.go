package main

import (
	"log"
	"net/http"

	"github.com/gin-gonic/gin"
	"content-processor/internal/api"
	"content-processor/internal/service"
)

func main() {
	// Initialize services
	contentService := service.NewContentService()
	handlers := api.NewHandlers(contentService)

	// Setup Gin router
	router := gin.Default()
	
	// Set max file size (10MB)
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