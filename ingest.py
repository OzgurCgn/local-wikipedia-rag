import json
import wikipedia
import chromadb
import ollama
import time


wikipedia.set_user_agent("BLG483E_Project/1.0 (caganh23@itu.edu.tr)")

CHROMA_DATA_PATH = "./chroma_db"
EMBEDDING_MODEL = "nomic-embed-text"

def load_entities(filepath="data/entities.json"):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def chunk_text(text, chunk_size=400, overlap=50):
    words = text.split()
    chunks = []
    for i in range(0, len(words), max(1, chunk_size - overlap)):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

def process_entity(entity, entity_type, collection):
    try:
        print(f"[{entity_type.upper()}] Processing: {entity}...")
        page = wikipedia.page(entity, auto_suggest=False)
        chunks = chunk_text(page.content)
        
        for idx, chunk in enumerate(chunks):
            response = ollama.embeddings(model=EMBEDDING_MODEL, prompt=chunk)
            embedding = response["embedding"]
            
            collection.upsert(
                ids=[f"{entity_type}_{entity.replace(' ', '_')}_{idx}"],
                embeddings=[embedding],
                documents=[chunk],
                metadatas=[{"type": entity_type, "entity": entity}]
            )
        print(f" -> {entity} added successfully. ({len(chunks)} chunks)")
        
        # Wikipedia sunucularını yormamak için her kayıttan sonra 2 saniye bekle
        time.sleep(2)
        
    except Exception as e:
        print(f" -> ERROR: Could not process {entity}. Detail: {e}")

def main():
    print("Initializing vector database...")
    client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)
    collection = client.get_or_create_collection(name="wiki_rag")
    
    entities = load_entities()
    
    print("\n--- Processing People ---")
    for person in entities.get("people", []):
        process_entity(person, "person", collection)
        
    print("\n--- Processing Places ---")
    for place in entities.get("places", []):
        process_entity(place, "place", collection)
        
    print("\nAll data ingestion and vectorization processes completed!")

if __name__ == "__main__":
    main()