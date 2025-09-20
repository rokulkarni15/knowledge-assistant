# Knowledge Assistant

A personal knowledge management platform built with microservices architecture using Python AsyncIO and Go.

## Architecture

- **API Gateway** (Python FastAPI) - Request routing and authentication
- **LLM Service** (Python + Ollama) - AI-powered knowledge extraction and chat
- **Content Processor** (Go) - Document processing and text extraction  
- **Search Service** (Go) - High-performance vector search and indexing
- **WebSocket Hub** (Go) - Real-time communication and updates

## Features

- Document upload and processing
- AI-powered knowledge extraction using locally-hosted Ollama LLMs
- Semantic search across all content
- Real-time updates via WebSocket
- Distributed microservices with gRPC communication

## Tech Stack

- **Languages:** Python (AsyncIO), Go
- **Frameworks:** FastAPI, Gin
- **AI:** Ollama (local LLM deployment)
- **Databases:** PostgreSQL, Redis
- **Communication:** REST APIs, WebSocket, gRPC