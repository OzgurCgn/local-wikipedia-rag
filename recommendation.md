# Recommendation: Production Deployment and Improvements

## 1. Current prototype

The current system is a local course-project prototype. It demonstrates the main RAG pipeline:

- Wikipedia ingestion
- chunking
- local embeddings
- vector database storage
- metadata-based retrieval
- local LLM generation
- Streamlit chat interface

It is appropriate for a localhost demo and for explaining the architecture of a simplified RAG system.

## 2. Recommended production architecture

For a production version, the system should be separated into services:

```text
Frontend
    ↓
Backend API
    ↓
Retrieval service
    ↓
Vector database
    ↓
Document database
    ↓
Model service
```

Recommended stack:

- Frontend: React, Next.js, or Streamlit for internal tools
- Backend: FastAPI
- Worker queue: Celery, RQ, or another background job processor
- Document database: PostgreSQL
- Vector database: Qdrant, Milvus, Weaviate, or Chroma for smaller deployments
- Model serving: Ollama for local use, vLLM or llama.cpp server for optimized production inference
- Observability: logs, latency metrics, retrieval metrics, and error tracking

## 3. Ingestion improvements

The current ingestion process is manual and fixed to a small entity list. A production system should add:

- scheduled ingestion
- retry logic
- source versioning
- duplicate detection
- ingestion status tracking
- chunk provenance
- source update timestamps
- admin tools for adding or removing entities

## 4. Retrieval improvements

The current retrieval uses vector similarity with metadata filtering. Improvements:

- hybrid retrieval using keyword search plus vector search
- reranking using a local cross-encoder
- better query rewriting
- stronger entity linking
- alias expansion from Wikipedia redirects
- dynamic top-k retrieval
- context compression before generation

## 5. Generation improvements

The current generation prompt is intentionally simple. Improvements:

- sentence-level citations
- source highlighting in answers
- stricter refusal behavior for unsupported questions
- confidence indicators
- streaming responses
- model comparison mode
- response caching

## 6. Comparison question improvements

Comparison questions are harder because they require balanced context for multiple entities. A stronger system should:

- retrieve a short profile chunk for each entity
- retrieve achievement-specific chunks for each entity
- summarize each entity separately
- generate the comparison from those summaries
- cite each side of the comparison

## 7. Security and reliability

Even with public Wikipedia data, production deployment should include:

- input validation
- rate limiting
- logging and monitoring
- safe error handling
- dependency pinning
- database backups
- prompt-injection mitigation

## 8. Local model tradeoffs

Advantages:

- no external LLM API dependency
- better privacy
- predictable local demo environment
- lower cost for small workloads

Limitations:

- slower on weak hardware
- quality depends on the local model
- local setup can be harder for users
- small models may hallucinate or follow prompts imperfectly

## 9. Recommended next steps for this project

1. Add automated tests for the example questions.
2. Add a small evaluation script that checks whether failure cases return `I don't know.`
3. Add better citations in answers.
4. Add latency measurement for ingestion, retrieval, and generation.
5. Add optional model selection in the Streamlit sidebar.
6. Add response caching for repeated questions.
7. Improve comparison answers with a summarize-then-compare pipeline.

## 10. Final recommendation

For the course submission, the current architecture is suitable because it is simple, local, and explainable. It demonstrates the required RAG components clearly. For production, the system should evolve toward a service-based architecture with stronger retrieval, evaluation, monitoring, and citation support.
