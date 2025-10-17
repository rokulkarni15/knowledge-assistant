package api

import (
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
	"search-service/internal/service"
	"search-service/internal/storage"
)

type Handlers struct {
	searchService *service.SearchService
}

func NewHandlers(searchService *service.SearchService) *Handlers {
	return &Handlers{
		searchService: searchService,
	}
}

// handle document indexing
func (h *Handlers) IndexDocument(c *gin.Context) {
	var req storage.IndexRequest

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if err := h.searchService.IndexDocument(&req); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Failed to index document",
			"details": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"message":     "Document indexed successfully",
		"document_id": req.DocumentID,
	})
}

// handle search queries
func (h *Handlers) SearchDocuments(c *gin.Context) {
	query := c.Query("q")
	if query == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Query parameter 'q' is required"})
		return
	}

	limitStr := c.DefaultQuery("limit", "10")
	limit, err := strconv.Atoi(limitStr)
	if err != nil || limit < 1 {
		limit = 10
	}

	results, err := h.searchService.Search(query, limit)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Search failed",
			"details": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"query":   query,
		"results": results,
		"total":   len(results),
	})
}

// retrieve a specific document
func (h *Handlers) GetDocument(c *gin.Context) {
	docID := c.Param("id")

	doc, err := h.searchService.GetDocument(docID)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{
			"error":   "Document not found",
			"details": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, doc)
}

// remove a document
func (h *Handlers) DeleteDocument(c *gin.Context) {
	docID := c.Param("id")

	if err := h.searchService.DeleteDocument(docID); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Failed to delete document",
			"details": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"message":     "Document deleted successfully",
		"document_id": docID,
	})
}

// return index statistics
func (h *Handlers) GetStats(c *gin.Context) {
	stats := h.searchService.GetStats()
	c.JSON(http.StatusOK, stats)
}

// register all API routes
func RegisterRoutes(router *gin.Engine, handlers *Handlers) {
	api := router.Group("/api/v1")
	{
		api.POST("/index", handlers.IndexDocument)
		api.GET("/search", handlers.SearchDocuments)
		api.GET("/documents/:id", handlers.GetDocument)
		api.DELETE("/documents/:id", handlers.DeleteDocument)
		api.GET("/stats", handlers.GetStats)
	}
}