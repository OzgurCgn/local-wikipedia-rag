# Demo Script

## 0:00 - 0:30 Overview

This is a local Wikipedia RAG assistant. It answers questions about famous people and famous places using locally stored Wikipedia chunks and local Ollama models.

## 0:30 - 1:15 Architecture

Show the files:

- `ingest.py`: downloads Wikipedia pages, chunks them, embeds them, and stores vectors in Chroma.
- `rag_core.py`: detects entities, retrieves context, and calls the local LLM.
- `app.py`: Streamlit chat interface.
- `data/entities.json`: 20 people and 20 places.

Explain that the system uses one Chroma vector store with metadata.

## 1:15 - 2:00 Ingestion

Show or run:

```bash
python ingest.py
```

Explain that this creates the local `chroma_db/` folder.

## 2:00 - 2:30 Start app

Run:

```bash
streamlit run app.py
```

## 2:30 - 4:15 Demo questions

Ask:

```text
What elements did Marie Curie discover?
Which famous place is located in India?
Which famous place is located in Turkey?
Which person is associated with electricity?
What was the Colosseum used for?
Tell me about a random unknown person John Doe.
```

Open the retrieved context expander for at least one answer.

## 4:15 - 5:00 Tradeoffs and improvements

Mention:

- local models improve privacy but can be slower
- rule-based entity detection is simple but not perfect
- comparison questions are harder
- future improvements include reranking, citations, more entities, and evaluation scripts
