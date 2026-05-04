# Product PRD: Local Wikipedia RAG Assistant

## 1. Product summary

The product is a local Wikipedia-based RAG assistant. It allows users to ask questions about famous people and famous places. The system retrieves relevant local Wikipedia chunks from a vector database and generates grounded answers using a local language model.

The project is designed for a course assignment and runs fully on localhost after ingestion.

## 2. Problem statement

Users need a simplified ChatGPT-style assistant that answers only from a controlled local dataset. The system should demonstrate ingestion, chunking, embedding, vector storage, retrieval, and local LLM generation.

## 3. Goals

- Ingest at least 20 famous people and 20 famous places from Wikipedia.
- Chunk large Wikipedia documents into manageable pieces.
- Generate embeddings locally without an external API.
- Store embeddings in a local vector database.
- Retrieve relevant chunks for a user query.
- Detect whether a query is about a person, place, concept, country, or comparison.
- Generate answers using a local LLM.
- Avoid hallucination when possible.
- Return `I don't know.` when the answer is not supported by the local data.
- Provide a simple chat interface.

## 4. Non-goals

- The system is not a full Wikipedia replacement.
- The system is not expected to answer questions about entities that were not ingested.
- The system does not use cloud LLM APIs.
- The system does not implement a complex production-grade entity linker.
- The system does not guarantee perfect answers for every comparison question.

## 5. Users

### Primary user

The instructor or teaching assistant who evaluates whether the system can run locally and demonstrate a complete RAG pipeline.

### Secondary user

A student or developer who wants to test a small local RAG architecture.

## 6. Functional requirements

### 6.1 Ingestion

The system ingests Wikipedia pages listed in `data/entities.json`. The file contains 20 famous people and 20 famous places.

### 6.2 Chunking

The system splits Wikipedia page content into overlapping word chunks. The current strategy uses:

- chunk size: 400 words
- overlap: 50 words

This keeps chunks small enough for retrieval and generation while preserving context across chunk boundaries.

### 6.3 Embedding

The system uses Ollama with `nomic-embed-text` to create embeddings locally. No external embedding API is used.

### 6.4 Vector storage

The system stores vectors in a local Chroma persistent database at `./chroma_db`.

Each vector has metadata:

- `type`: `person` or `place`
- `entity`: source entity name

### 6.5 Retrieval

The system retrieves context by:

1. Detecting matching entity names, aliases, countries, or concepts.
2. Applying metadata filtering when possible.
3. Querying the Chroma collection with the local query embedding.
4. Returning the most relevant chunks.

### 6.6 Generation

The system uses Ollama with `llama3.2` to generate answers from retrieved context.

The prompt instructs the model to:

- answer using only retrieved context
- avoid unsupported facts
- keep answers concise
- return `I don't know.` if the answer is not in the context

### 6.7 Chat interface

The system provides a Streamlit chat interface that supports:

- entering questions
- seeing generated answers
- viewing retrieved context
- clearing chat history

## 7. Architecture

```text
Wikipedia pages
    ↓
ingest.py
    ↓
chunk_text()
    ↓
Ollama nomic-embed-text
    ↓
Chroma vector database with metadata
    ↓
Streamlit query
    ↓
rag_core.py entity/intent routing
    ↓
Chroma retrieval
    ↓
Ollama llama3.2 generation
    ↓
Answer + optional retrieved context
```

## 8. Design choice

The system uses **one vector store with metadata** instead of two separate vector stores.

Reasons:

- It is simpler to run and maintain.
- Metadata filtering is enough for this dataset size.
- Entity-specific retrieval can be handled by `entity` metadata.
- Person/place filtering can be handled by `type` metadata.
- Mixed or comparison queries can retrieve from multiple entities.

Tradeoff:

- Rule-based routing must be maintained carefully.
- A larger production system may benefit from stronger entity linking or separate indexes.

## 9. Evaluation plan

Test cases:

- Person: `What elements did Marie Curie discover?`
- Person concept: `Which person is associated with electricity?`
- Place: `Where is the Eiffel Tower located?`
- Place country mapping: `Which famous place is located in Turkey?`
- Place details: `What was the Colosseum used for?`
- Comparison: `Compare the Eiffel Tower and the Statue of Liberty.`
- Failure: `Who is the president of Mars?`
- Failure: `Tell me about a random unknown person John Doe.`

## 10. Risks and mitigations

### Risk: hallucination

Mitigation:

- Use retrieved-context-only prompting.
- Return `I don't know.` for unknown entities.
- Keep the ingested dataset controlled.

### Risk: weak comparison answers

Mitigation:

- Retrieve context for each detected entity separately.
- Keep comparison prompts concise and grounded.
- Prefer demo questions with clean retrieved context.

### Risk: duplicate ingestion

Mitigation:

- Use `collection.upsert` in ingestion so repeated ingestion is safer.

### Risk: slow local embedding

Mitigation:

- Use a small embedding model.
- Persist Chroma data locally after ingestion.

## 11. Future improvements

- Add a stronger reranking step.
- Add automatic citation formatting.
- Add more entities and categories.
- Add automated evaluation queries.
- Add latency measurement.
- Add response caching.
- Improve entity linking with aliases from Wikipedia redirects.
- Compare multiple local LLMs such as `llama3.2`, `phi3`, and `mistral`.
