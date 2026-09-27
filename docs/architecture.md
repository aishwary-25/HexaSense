# HexaSense architecture

## Overview

HexaSense is a local-first document intelligence system for Windows PCs powered by Snapdragon X Elite. It ingests privileged files, extracts text, redacts sensitive data, embeds content locally, and answers questions with grounded responses.

## Architecture layers

### 1. Ingestion layer

Purpose: accept files from the user and prepare them for indexing.

Components:
- file upload UI
- local file parsing
- text extraction
- metadata tracking (file name, file id, path, timestamp)

### 2. Redaction layer

Purpose: identify and redact personally identifiable or secret values before indexing.

Examples:
- email addresses
- credit card numbers
- tokens
- IP addresses

This is critical because the app is privacy-first and should minimize leakage inside the local index.

### 3. Chunking + embedding layer

Purpose: convert documents into small chunks that can be retrieved semantically.

Implementation plan:
- split text into 400-600 token chunks
- preserve overlap for continuity
- embed chunks locally with a sentence-transformer model
- store vectors in a local vector database

### 4. Retrieval layer

Purpose: find the most relevant chunks for a query.

The retrieval system should support:
- keyword search
- semantic similarity search
- top-k results
- file-level filtering

### 5. Answer generation layer

Purpose: generate a grounded response using context retrieved from local memory.

Flow:
- user asks a natural-language question
- retrieve relevant chunks
- send them to a local LLM
- return answer + source snippets

### 6. Memory control layer

Purpose: support selective forgetting.

A user should be able to:
- remove a doc
- remove a chunk
- delete all doc metadata
- clear the local embedding index for that file

This is a major differentiator and should be emphasized in the hackathon pitch.

## Security posture

The system assumes the user owns the device and the data. This means:

- do not send questions to third-party APIs by default
- store embeddings locally
- provide a local-only mode
- allow file-level deletion
- mark redacted content explicitly in the pipeline

## Suggested implementation sequence

1. Build file ingestion and parsing
2. Add redaction and metadata tracking
3. Build chunking and local embeddings
4. Add retrieval and answer generation
5. Implement forget/delete document flow
6. Measure answer quality and latency

## Demo flow

1. user uploads a doc set
2. app scans and redacts sensitive fields
3. user asks a question
4. app retrieves relevant chunks
5. answer is returned with citation evidence
6. user deletes a file and asks again
7. file is gone from new responses

## Security-first future roadmap

- allow user-configured redaction policies
- support encrypted local index storage
- provide export/import of encrypted memory
- support OCR for scanned PDF docs
- benchmark CPU vs NPU performance
