# Local Wikipedia RAG Assistant

Demo video link: **TODO: paste your Loom or unlisted YouTube link here before submission.**

## Project overview

This project is a local ChatGPT-style Retrieval Augmented Generation (RAG) assistant. It answers questions about famous people and famous places using Wikipedia data that is ingested, chunked, embedded, stored, retrieved, and passed to a local language model.

The system runs on localhost and does not use any external LLM API. Wikipedia is used as the data source during ingestion. After ingestion, question answering uses the local Chroma vector database and local Ollama models.

## Features

- Ingests Wikipedia pages for 20 famous people and 20 famous places.
- Splits Wikipedia pages into overlapping word chunks.
- Generates embeddings locally with Ollama using `nomic-embed-text`.
- Stores vectors locally in Chroma.
- Stores metadata for each chunk, including `type` and `entity`.
- Detects whether a query is about a person, place, concept, country, or comparison.
- Retrieves relevant chunks from the local vector database.
- Generates grounded answers with a local Ollama LLM.
- Returns `I don't know.` for out-of-scope questions.
- Provides a Streamlit chat interface with optional retrieved context display.

## Design choice: one vector store with metadata

This implementation uses **Option B: one vector store with metadata**.

All chunks are stored in a single Chroma collection named `wiki_rag`. Each chunk has metadata:

- `type`: `person` or `place`
- `entity`: entity name such as `Marie Curie` or `Hagia Sophia`

This design was chosen because it keeps the system simple while still allowing filtered retrieval. For example, person questions can filter by `type = person`, place questions can filter by `type = place`, and entity-specific questions can filter by the exact `entity` name. Mixed or comparison questions can retrieve chunks for multiple detected entities.

## Tech stack

- Python
- Streamlit for the chat interface
- Wikipedia Python package for ingestion
- Ollama for local embeddings and local generation
- `nomic-embed-text` for embeddings
- `llama3.2` for answer generation
- Chroma for local vector storage

## Folder structure

```text
LOCAL_WIKIPEDIA_RAG/
├── app.py
├── ingest.py
├── rag_core.py
├── requirements.txt
├── README.md
├── product_prd.md
├── recommendation.md
├── demo_script.md
├── .gitignore
└── data/
    └── entities.json
```

Generated after ingestion:

```text
chroma_db/
```

`chroma_db/` is ignored by Git because it is generated locally by running `python ingest.py`.

## Setup instructions

### 1. Install Ollama

Install Ollama from:

```text
https://ollama.com
```

Make sure Ollama is running.

### 2. Pull local models

```bash
ollama pull llama3.2
ollama pull nomic-embed-text
```

### 3. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Ingest Wikipedia data

```bash
python ingest.py
```

This downloads Wikipedia content, chunks it, creates local embeddings, and stores vectors in Chroma.

### 6. Run the app

```bash
streamlit run app.py
```

Open the local Streamlit URL shown in the terminal.

## Example questions

People:

```text
What elements did Marie Curie discover?
What is Charles Darwin known for?
Why is Nikola Tesla famous?
```

Places:

```text
Where is the Eiffel Tower located?
What was the Colosseum used for?
Which famous place is located in India?
Which famous place is located in Turkey?
```

Concept or mixed questions:

```text
Which person is associated with electricity?
Which person is associated with radioactivity?
Compare the Eiffel Tower and the Statue of Liberty.
Compare Albert Einstein and Nikola Tesla.
```

Failure cases:

```text
Who is the president of Mars?
Tell me about a random unknown person John Doe.
What is the capital city of Atlantis?
```

Expected failure-case behavior:

```text
I don't know.
```

## Demo video checklist

The 5-minute demo should show:

1. Project folder and file structure.
2. Ollama models installed locally.
3. Running `python ingest.py` or showing that ingestion has populated Chroma.
4. Running `streamlit run app.py`.
5. Asking a person question.
6. Asking a place question.
7. Asking a country/entity mapping question.
8. Asking a concept question.
9. Asking a failure-case question that returns `I don't know.`
10. Opening the retrieved context expander.
11. Explaining design choice: one vector store with metadata.
12. Explaining limitations and possible improvements.

## Known limitations

- The system uses simple rule-based entity and intent detection.
- Comparison answers depend on the quality of retrieved context and the local model.
- The dataset is limited to the configured 20 people and 20 places.
- The system does not support arbitrary Wikipedia questions outside the ingested entities.
- The first ingestion run can take time because embeddings are generated locally.

## Repository contents

The repository includes the main application code, ingestion script, RAG logic, dependency list, documentation files, and the entity configuration file.

Included files:

```text
app.py
ingest.py
rag_core.py
requirements.txt
README.md
product_prd.md
recommendation.md
demo_script.md
.gitignore
data/entities.json