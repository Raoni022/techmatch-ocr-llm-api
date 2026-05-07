# AI Document Intelligence API

A portfolio-grade FastAPI system for extracting, analyzing, and ranking documents using OCR and lightweight NLP techniques.

This repository demonstrates document intelligence pipeline design for workflows such as document screening, classification, knowledge extraction, and query-based ranking.

## Evaluator Quick Scan

| Area | Current implementation |
|---|---|
| API | FastAPI REST API |
| OCR | Tesseract-based document/image text extraction |
| NLP | Lightweight/local NLP service for summarization, keywords, sentiment, and categories |
| Ranking | Query-to-document relevance scoring |
| Batch processing | Multi-file processing with per-document success/failure isolation |
| Auditability | Audit log abstraction with local/mock implementation |
| Docs | Swagger/OpenAPI via FastAPI |
| Status | Applied AI backend prototype |

## Why this project exists

Most OCR demos stop at raw text extraction. Real document workflows usually need more:

- extract text from files
- summarize or classify content
- compare documents against a query
- rank results by relevance
- isolate failures during batch processing
- keep audit logs for operational review

This project shows how those concerns can be organized into a backend API.

## Core Flow

```text
Document Input
  -> OCR Extraction
  -> Text Cleaning
  -> NLP Analysis
  -> Query-Based Ranking
  -> Structured API Response
  -> Audit Log
```

## Current capabilities

- health endpoint
- supported language endpoint
- text analysis endpoint
- structured information extraction from raw text
- batch document processing
- optional query-based ranking
- summary-only mode when no query is provided
- audit log endpoint
- usage statistics endpoint
- global exception handler

## What is implemented vs. intentionally simplified

Implemented:

- FastAPI application structure
- upload/batch processing route
- OCR service boundary
- lightweight NLP service boundary
- ranking logic for query-based processing
- audit log abstraction
- structured response models
- health and stats endpoints

Simplified for local reproducibility:

- NLP layer uses a lightweight/local implementation rather than a paid LLM provider
- audit logging uses a local/mock implementation instead of a managed database by default
- no persistent document storage layer yet
- no vector database or embedding cache yet
- authentication and rate limiting are not included in this prototype

This is best read as a document intelligence backend prototype, not a fully deployed enterprise document platform.

## Architecture Overview

```text
Client
  -> FastAPI API
      -> File Upload / Batch Route
      -> OCR Service
      -> NLP Service
      -> Ranking Logic
      -> Audit Log
      -> Structured Response
```

## Engineering decisions

- Keep OCR, NLP, ranking, and API concerns separated.
- Support batch processing with per-document success/failure handling.
- Return relevance scores only when a query is provided.
- Keep local NLP lightweight so the project can be reviewed without paid API keys.
- Make audit logging optional so pipeline execution does not fail when logging is unavailable.

## Trade-offs

- Tesseract is lower cost and locally runnable, but less accurate than managed OCR for noisy scans.
- Lightweight NLP is faster and easier to review, but less capable than LLM-based semantic extraction.
- Query ranking is intentionally simple and can be upgraded to embeddings + vector search.
- The current project focuses on pipeline design rather than production security.

## Future improvements

- add persistent document storage
- integrate vector search using pgvector, FAISS, or Chroma
- add embedding cache
- add LLM-based extraction and classification
- add authentication and rate limiting
- add Docker Compose with persistence services
- add evaluation data for OCR/ranking quality
- add CI workflow for tests and linting

## Suggested evaluator talking points

- how the system separates extraction, analysis, ranking, and audit logging
- why OCR-only systems are not enough for document workflows
- how to upgrade the ranking layer to embeddings/RAG
- how to add retries and dead-letter handling for failed documents
- how to add persistent storage and authentication for production use

## Status

Applied AI pipeline / backend system prototype.
