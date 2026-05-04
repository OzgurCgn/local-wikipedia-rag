# Local Wikipedia RAG Assistant

Demo video link: **TODO: paste Loom or unlisted YouTube link here before submission.**

## Project Overview

This project is a local chat-style Retrieval Augmented Generation (RAG) assistant. It answers questions about famous people and famous places using Wikipedia data.

The system runs on localhost. It uses local embeddings, a local vector database, and a local language model. No external LLM API is used.

The application follows a simple RAG pipeline:

1. Ingest Wikipedia pages.
2. Split documents into chunks.
3. Generate local embeddings.
4. Store chunks and metadata in Chroma.
5. Retrieve relevant chunks for a user query.
6. Generate an answer using a local Ollama model.

## Features

- Ingests Wikipedia pages for 20 famous people and 20 famous places.
- Splits long Wikipedia pages into smaller chunks.
- Generates embeddings locally with Ollama using `nomic-embed-text`.
- Stores vectors locally in Chroma.
- Stores metadata for each chunk, including entity name and entity type.
- Retrieves relevant chunks based on entity, country, concept, or query intent.
- Generates answers using a local Ollama language model.
- Returns `I don't know.` for out-of-scope questions.
- Provides a Streamlit chat interface.
- Allows users to view retrieved context chunks.

## Design Choice

This project uses **Option B: one vector store with metadata**.

All chunks are stored in a single Chroma collection named `wiki_rag`. Each chunk includes metadata such as:

```text
type: person or place
entity: entity name
```

This design keeps the system simple while still allowing filtered retrieval. For example:

- Person questions can retrieve chunks related to people.
- Place questions can retrieve chunks related to places.
- Entity-specific questions can retrieve chunks for a specific entity.
- Mixed or comparison questions can retrieve chunks for multiple detected entities.

This corresponds to the metadata-based vector store option.

## Tech Stack

- Python
- Streamlit
- Wikipedia Python package
- Ollama
- `nomic-embed-text` for embeddings
- `llama3.2` for local answer generation
- Chroma for local vector storage

## Project Structure

```text
LOCAL_WIKIPEDIA_RAG/
├── app.py
├── ingest.py
├── rag_core.py
├── requirements.txt
├── README.md
├── product_prd.md
├── recommendation.md
├── .gitignore
└── data/
    └── entities.json
```

After ingestion, Chroma creates the following local folder:

```text
chroma_db/
```

This folder is generated locally and is not committed to GitHub.

## Installation

### 1. Install Ollama

Install Ollama from:

```text
https://ollama.com
```

Make sure Ollama is running before using the application.

### 2. Pull Local Models

```bash
ollama pull llama3.2
ollama pull nomic-embed-text
```

### 3. Create a Virtual Environment

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

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

## Ingest Wikipedia Data

Run the ingestion script before starting the app:

```bash
python ingest.py
```

This script:

- reads entities from `data/entities.json`,
- downloads Wikipedia content,
- chunks the text,
- generates local embeddings with Ollama,
- stores vectors and metadata in Chroma.

The generated Chroma database is stored in:

```text
chroma_db/
```

## Run the Application

Start the Streamlit app:

```bash
streamlit run app.py
```

Then open the local URL shown in the terminal.

## Example Questions

### People

```text
What elements did Marie Curie discover?
What is Charles Darwin known for?
Why is Nikola Tesla famous?
```

### Places

```text
Where is the Eiffel Tower located?
What was the Colosseum used for?
Which famous place is located in India?
Which famous place is located in Turkey?
```

### Concept and Mixed Questions

```text
Which person is associated with electricity?
Which person is associated with radioactivity?
Compare the Eiffel Tower and the Statue of Liberty.
Compare Albert Einstein and Nikola Tesla.
```

### Failure Cases

```text
Who is the president of Mars?
Tell me about a random unknown person John Doe.
What is the capital city of Atlantis?
```

Expected behavior for unsupported questions:

```text
I don't know.
```

## Known Limitations

- The system uses simple rule-based entity and intent detection.
- Comparison answers depend on the retrieved Wikipedia chunks and the local model.
- The dataset is limited to the configured 20 people and 20 places.
- Questions outside the ingested entities are handled conservatively with `I don't know.`
- The first ingestion run can take time because embeddings are generated locally.

## Notes

Generated local files such as the virtual environment, Python cache files, and Chroma database are excluded from the repository through `.gitignore`.

```text
.venv/
__pycache__/
chroma_db/
```
