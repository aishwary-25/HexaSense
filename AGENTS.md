# AGENTS.md

This repository is for HexaSense, a private on-device AI knowledge assistant for Windows Snapdragon PCs.

## Mission

Build a local-first document Q&A system with:

- document ingestion
- text extraction
- PII redaction
- local vector indexing
- retrieval-augmented answering
- selective forgetting / memory removal

## Critical design principles

1. Keep everything local by default.
2. No cloud dependency for the MVP.
3. User should be able to forget a file completely.
4. Every answer must be grounded in a source snippet.
5. Safeguard sensitive content before indexing.
6. Favor a clear demo over broad feature scope.

## Recommended implementation order

1. Ingestion and file parsing
2. Chunking and indexing
3. Retrieval pipeline
4. Local answer generation
5. Redaction layer
6. Forget/delete feature
7. UX polish for demo

## Important architecture constraints

- The app should support a few document types: PDF, TXT, MD, DOCX
- Local embeddings should be stored on-device
- The vector database should support deletion by file ID
- The redaction phase should detect and mask sensitive text before indexing
- A file deletion flow should remove chunks, vectors, and metadata

## Deliverables for an agent

When implementing new features, prefer:

- small modules
- strong typed configuration
- failure-safe local operations
- explicit metadata on each document
- complete cleanup of memory when documents are removed

## Suggested demo scenario

- Upload contracts and notes
- Ask a question about a specific term
- Show answer with citations
- Redact sensitive content before indexing
- Delete one file
- Confirm it disappears from future answers

## Quality bar

The product should feel like a demo-ready local AI assistant, not a janky prototype. It must clearly demonstrate:

- on-device privacy
- grounded answers
- memory control
- security-conscious design

## Output expectations

Agents working in this repo should keep code clean and make the project easy to extend. Avoid unnecessary backend complexity. Focus on the MVP and the hackathon demo flow.
