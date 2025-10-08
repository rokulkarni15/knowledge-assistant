package api

import (
	"fmt"
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"content-processor/internal/models"
	"content-processor/internal/processors"
	"content-processor/internal/service"
)

type Handlers struct {
	contentService *service.ContentService
	pdfProcessor   *processors.PDFProcessor
}

func NewHandlers(contentService *service.ContentService) *Handlers {
	return &Handlers{
		contentService: contentService,
		pdfProcessor:   processors.NewPDFProcessor(),
	}
}

// handle text processing requests
func (h *Handlers) ProcessText(c *gin.Context) {
	var request models.ProcessingRequest
	
	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	
	// Generate document ID if not provided
	if request.DocumentID == "" {
		request.DocumentID = uuid.New().String()
	}
	
	// Process the content
	response, err := h.contentService.ProcessContent(&request)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Failed to process content",
			"details": err.Error(),
		})
		return
	}
	
	c.JSON(http.StatusOK, response)
}

// handle PDF file upload and processing
func (h *Handlers) ProcessFile(c *gin.Context) {
	file, err := c.FormFile("file")
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "No file uploaded"})
		return
	}
	
	// Only accept PDFs
	if !strings.HasSuffix(strings.ToLower(file.Filename), ".pdf") {
		c.JSON(http.StatusBadRequest, gin.H{
			"error":           "Only PDF files are supported",
			"supported_types": []string{".pdf"},
		})
		return
	}
	
	// Create uploads directory
	uploadsDir := "uploads"
	if err := os.MkdirAll(uploadsDir, 0755); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create uploads directory"})
		return
	}
	
	// Save file
	documentID := uuid.New().String()
	savedPath := filepath.Join(uploadsDir, documentID+".pdf")
	
	if err := c.SaveUploadedFile(file, savedPath); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Failed to save file",
			"details": err.Error(),
		})
		return
	}
	
	// Extract text from PDF
	extractedText, err := h.pdfProcessor.ExtractText(savedPath)
	if err != nil {
		os.Remove(savedPath)
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Failed to extract PDF text",
			"details": err.Error(),
		})
		return
	}
	
	// Get PDF metadata
	metadata, _ := h.pdfProcessor.GetMetadata(savedPath)
	
	// Create processing request
	request := models.ProcessingRequest{
		DocumentID: documentID,
		Content:    extractedText,
		FileType:   "application/pdf",
		Metadata: map[string]string{
			"filename":       file.Filename,
			"size":           fmt.Sprintf("%d", file.Size),
			"saved_path":     savedPath,
			"pages":          metadata["pages"],
			"content_length": fmt.Sprintf("%d", len(extractedText)),
		},
	}
	
	// Process with LLM service
	response, err := h.contentService.ProcessContent(&request)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Failed to process file content",
			"details": err.Error(),
		})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{
		"message":              "PDF processed successfully",
		"filename":             file.Filename,
		"extracted_text_length": len(extractedText),
		"pages":                metadata["pages"],
		"result":               response,
	})
}

// register all API routes
func RegisterRoutes(router *gin.Engine, handlers *Handlers) {
	api := router.Group("/api/v1")
	{
		api.POST("/process/text", handlers.ProcessText)
		api.POST("/process/file", handlers.ProcessFile)
	}
}