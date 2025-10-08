package processors

import (
	"fmt"
	"strings"

	"github.com/unidoc/unipdf/v3/extractor"
	"github.com/unidoc/unipdf/v3/model"
)

type PDFProcessor struct{}

func NewPDFProcessor() *PDFProcessor {
	return &PDFProcessor{}
}

// extract text from PDF file using unipdf library
func (p *PDFProcessor) ExtractText(filepath string) (string, error) {
	// Open PDF file - returns reader, file handle, and error
	pdfReader, fileHandle, err := model.NewPdfReaderFromFile(filepath, nil)
	if err != nil {
		return "", fmt.Errorf("failed to open PDF: %w", err)
	}
	defer fileHandle.Close()  // Close the file when done

	numPages, err := pdfReader.GetNumPages()
	if err != nil {
		return "", fmt.Errorf("failed to get page count: %w", err)
	}

	var textBuilder strings.Builder

	// Extract text from each page
	for i := 1; i <= numPages; i++ {
		page, err := pdfReader.GetPage(i)
		if err != nil {
			return "", fmt.Errorf("failed to get page %d: %w", i, err)
		}

		ex, err := extractor.New(page)
		if err != nil {
			return "", fmt.Errorf("failed to create extractor for page %d: %w", i, err)
		}

		text, err := ex.ExtractText()
		if err != nil {
			return "", fmt.Errorf("failed to extract text from page %d: %w", i, err)
		}

		textBuilder.WriteString(text)
		textBuilder.WriteString("\n\n")
	}

	return strings.TrimSpace(textBuilder.String()), nil
}

// extract metadata from PDF
func (p *PDFProcessor) GetMetadata(filepath string) (map[string]string, error) {
	pdfReader, fileHandle, err := model.NewPdfReaderFromFile(filepath, nil)
	if err != nil {
		return nil, err
	}
	defer fileHandle.Close()

	numPages, _ := pdfReader.GetNumPages()
	
	metadata := map[string]string{
		"pages": fmt.Sprintf("%d", numPages),
		"type":  "pdf",
	}

	// Get PDF info if available
	if pdfInfo, err := pdfReader.GetPdfInfo(); err == nil {
		if pdfInfo.Title != nil {
			metadata["title"] = pdfInfo.Title.String()
		}
		if pdfInfo.Author != nil {
			metadata["author"] = pdfInfo.Author.String()
		}
		if pdfInfo.Subject != nil {
			metadata["subject"] = pdfInfo.Subject.String()
		}
	}

	return metadata, nil
}