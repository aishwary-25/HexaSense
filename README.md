# HexaSense

HexaSense is a private, on-device AI knowledge assistant built for Windows PCs powered by Snapdragon X Elite. It lets users ingest personal or business documents, ask natural-language questions, and receive grounded answers without sending sensitive data to the cloud.

It is designed for privacy-first AI workflows: local retrieval, local inference, document redaction, and selective forgetting.

## Why this project matters

Most AI workflows today rely on cloud APIs. That creates privacy, compliance, and latency issues for users storing sensitive data in PDFs, emails, notes, and internal documents. HexaSense solves that with an offline-first pipeline that runs locally on the device.

## Core value proposition

- Private: files stay on-device
- Fast: low-latency local retrieval and inference
- Grounded: answers cite source snippets from documents
- Controllable: users can delete or forget specific files
- Security-aware: automatic PII detection and redaction

## Product pitch

"HexaSense is a private on-device AI knowledge assistant for Snapdragon PCs. Users can securely index personal or business files locally, ask natural-language questions, and retrieve answers with evidence from the documents on their device. It keeps sensitive data private, helps enforce forgetting, and is designed for HP PCs powered by Snapdragon X Elite."

## Key differentiators

1. Local-only architecture
2. Document forgetting / selective memory removal
3. PII redaction before indexing
4. On-device retrieval + answer grounding
5. Qualcomm story: works naturally with Snapdragon X Elite and NPU acceleration

## Demo concept

A user uploads a few internal docs, asks:

- "What did the client say about launch timing?"
- "Show me the payment terms in the contract."
- "Summarize the notes from the strategy doc."

Then the app retrieves relevant snippets and responds with citations.

Next, the user clicks "Forget file". The document disappears from all future answers and embedded chunks are removed from the vector store.

## Audience

- Enterprise knowledge workers
- Students and researchers with sensitive notes
- Privacy-conscious users
- Developers and teams handling confidential materials
- Snapdragon / Windows AI demos

## Project goals

- Build a working local document Q&A MVP
- Keep all processing on-device
- Add automatic redaction for sensitive fields
- Support selective forgetting of indexed content
- Deliver a 2-minute hackathon demo

## Non-goals for MVP

- Full cloud sync
- Multi-user collaboration
- Production-grade enterprise auth
- Heavy multi-tenant backend

## Hackathon angle

This is an ideal hackathon project because it is:

- practical
- privacy-first
- edge AI aligned with Snapdragon NPU
- easy to explain in 30 seconds
- highly demo-friendly

## Recommended stack

### Backend / app logic
- Python 3.11+
- FastAPI or Streamlit
- LangChain or custom RAG flow
- FAISS or Chroma for vector search
- sentence-transformers for embeddings

### Local model options
- Ollama
- llama.cpp
- Microsoft Phi / Qwen models via local runtime
- Qualcomm AI Hub optimized models if available

### Desktop UI options
- Streamlit for fastest delivery
- Electron for more polished desktop app
- Tauri for lightweight Windows app

### Document processing
- PyMuPDF / pdfplumber
- python-docx
- plain text parsing

## Detailed architecture

HexaSense follows a local RAG workflow:

1. File ingestion
2. Text extraction
3. Sensitive data detection / redaction
4. Chunking
5. Embedding generation
6. Vector storage
7. Retrieval on user query
8. LLM answer generation grounded in local context
9. Memory control for forgetting and removal

## High-level flow

```text
User uploads docs
      |
      v
Ingest + OCR + parse
      |
      v
Redaction layer (PII detection)
      |
      v
Chunk text + embed locally
      |
      v
Persist vectors in local store
      |
      v
User asks question
      |
      v
Retrieve matching chunks
      |
      v
Grounded answer generation
      |
      v
Return answer + source snippets
```

## Security and privacy model

HexaSense is privacy-first by design.

### Privacy policy for the MVP

- Everything runs on the same device
- No cloud API required
- The app can operate in completely offline mode
- Document embeddings live in a local vector store only
- User can delete a document and remove its memory
- PII redaction can help minimize leakage before indexing

## Core modules

- ingestion: file parsing and chunking
- redaction: PII detection and safe filtering
- vector_store: local embeddings and retrieval
- retriever: semantic search for relevant chunks
- llm_client: local model call for answers
- memory_manager: file deletion and selective forgetting
- ui: review UI and demo flow

## MVP feature set

### Must-have

- Document upload
- PDF / text / DOCX support
- Natural-language Q&A
- Answer with citations
- Delete/forget file
- Automatic sensitive-data redaction
- Offline operation

### Stretch

- Email import
- Markdown and JSON support
- OCR for scanned docs
- Conversation history
- Multimodal search
- NPU benchmark metrics
- Smart summarization

## Suggested product names and taglines

- HexaSense — Private AI memory for Snapdragon PCs
- HexaSense Secure — On-device knowledge that forgets
- HexaSense Recall — Local private memory for documents

## Suggested repo structure

```text
HexaSense/
├── README.md
├── AGENTS.md
├── requirements.txt
├── .gitignore
├── app/
│   ├── __init__.py
│   ├── main.py
│   └── ui.py
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── ingest.py
│   ├── redactor.py
│   ├── vector_store.py
│   ├── retriever.py
│   ├── llm_client.py
│   ├── memory_manager.py
│   └── demo_data.py
├── data/
│   └── sample_docs/
│       ├── notes.txt
│       ├── contract.md
│       └── research.txt
├── docs/
│   ├── architecture.md
│   ├── demo-script.md
│   └── roadmap.md
├── benchmarks/
│   └── latency.md
└── tests/
    └── test_redactor.py
```

## Implementation roadmap

### Phase 1: MVP
- file upload
- text extraction
- simple local chunking
- vector indexing
- prompt-answer generation
- delete/forget workflow

### Phase 2: privacy polish
- PII redaction
- redaction review UI
- memory deletion pipeline
- audit log of indexed docs

### Phase 3: Snapdragon optimization
- test low-latency local model paths
- benchmark CPU / NPU performance
- optimize chunk size and retrieval pipeline

### Phase 4: productization
- polished UI
- optional Windows app packaging
- richer document types
- export/import of private index

## Agent instructions

This repository is designed to be usable by agentic coding assistants. The main implementation goal is to build a strong MVP without architecture drift.

### Principles for agents

- Keep all data local by default
- Prefer local inference, not cloud APIs
- Make forgetting a first-class feature
- Keep the design simple and demo-friendly
- Prioritize correctness and grounded responses over fancy features

## Example prompt for future agents

```text
Build the next iteration of HexaSense as a local private document Q&A assistant. Keep all processing on-device. Implement ingestion, redaction, vector retrieval, and grounded answer generation using a local LLM. Add a memory manager that deletes a file and removes all associated chunks and embeddings. Keep the UI simple and demo-friendly for a Windows Snapdragon laptop demo.
```

## Suggested hackathon storyline

"HexaSense turns any Windows Snapdragon PC into a private AI knowledge assistant. It can parse your work documents, personal notes, and confidential files, answer grounded questions from them locally, and let the user forget a document at any time. That makes it ideal for privacy-sensitive workflows and positions it as a secure local AI companion for modern laptops."

## Recommended demo metrics

- answer latency
- source citation relevance
- redaction completeness
- delete/forget correctness
- local inference reliability

## First milestone checklist

- [ ] Document ingestion works
- [ ] Relevant retrieval works
- [ ] Local LLM answers grounded snippets
- [ ] Delete file removes embeddings and chunks
- [ ] PII redaction runs before indexing
- [ ] Demo script is ready

## Final recommendation

HexaSense is a strong Qualcomm hackathon project because it connects an explicit hardware story with a real product narrative: local AI, privacy, and on-device intelligence for modern Windows PCs.

It is differentiated from generic chatbots because it is built around memory, forgetting, and grounded access to private data.

## Getting started

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
python app/main.py
```

This repository is intentionally structured so that an agentic AI can extend the project module-by-module without needing to rewrite the whole system.

---

This project is intentionally designed to be a strong Qualcomm hackathon concept, easy to demo, and realistic to build in a short build window.
