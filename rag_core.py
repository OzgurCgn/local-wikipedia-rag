import json
import re
from pathlib import Path

import chromadb
import ollama

CHROMA_DATA_PATH = "./chroma_db"
EMBEDDING_MODEL = "nomic-embed-text"
LLM_MODEL = "llama3.2"

DATA_DIR = Path("data")
ENTITIES_FILE = DATA_DIR / "entities.json"

client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)
collection = client.get_or_create_collection(name="wiki_rag")


DEFAULT_PEOPLE = [
    "Albert Einstein", "Marie Curie", "Leonardo da Vinci", "William Shakespeare",
    "Ada Lovelace", "Nikola Tesla", "Lionel Messi", "Cristiano Ronaldo",
    "Taylor Swift", "Frida Kahlo", "Mahatma Gandhi", "Nelson Mandela",
    "Marilyn Monroe", "Elvis Presley", "Pablo Picasso", "Vincent van Gogh",
    "Stephen Hawking", "Isaac Newton", "Galileo Galilei", "Charles Darwin"
]

DEFAULT_PLACES = [
    "Eiffel Tower", "Great Wall of China", "Taj Mahal", "Grand Canyon",
    "Machu Picchu", "Colosseum", "Hagia Sophia", "Statue of Liberty",
    "Pyramids of Giza", "Mount Everest", "Stonehenge", "Petra",
    "Acropolis of Athens", "Sydney Opera House", "Angkor Wat", "Alhambra",
    "Mount Fuji", "Niagara Falls", "Yellowstone National Park", "Burj Khalifa"
]


def load_entity_lists():
    if ENTITIES_FILE.exists():
        try:
            with open(ENTITIES_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            people = data.get("people", DEFAULT_PEOPLE)
            places = data.get("places", DEFAULT_PLACES)

            return people, places

        except Exception:
            pass

    return DEFAULT_PEOPLE, DEFAULT_PLACES


PEOPLE, PLACES = load_entity_lists()
ALL_ENTITIES = PEOPLE + PLACES


COUNTRY_TO_ENTITY = {
    "turkey": "Hagia Sophia",
    "türkiye": "Hagia Sophia",
    "france": "Eiffel Tower",
    "china": "Great Wall of China",
    "india": "Taj Mahal",
    "italy": "Colosseum",
    "nepal": "Mount Everest",
    "egypt": "Pyramids of Giza",
    "peru": "Machu Picchu",
    "united states": "Statue of Liberty",
    "usa": "Statue of Liberty",
    "america": "Statue of Liberty",
    "japan": "Mount Fuji",
    "australia": "Sydney Opera House",
    "spain": "Alhambra",
    "greece": "Acropolis of Athens",
    "jordan": "Petra",
    "canada": "Niagara Falls",
    "united arab emirates": "Burj Khalifa",
    "uae": "Burj Khalifa"
}


CONCEPT_TO_ENTITY = {
    "electricity": "Nikola Tesla",
    "electrical": "Nikola Tesla",
    "alternating current": "Nikola Tesla",
    "ac current": "Nikola Tesla",
    "radioactivity": "Marie Curie",
    "radium": "Marie Curie",
    "polonium": "Marie Curie",
    "relativity": "Albert Einstein",
    "gravity": "Isaac Newton",
    "evolution": "Charles Darwin",
    "natural selection": "Charles Darwin",
    "football": "Lionel Messi",
    "soccer": "Lionel Messi"
}


ENTITY_ALIASES = {
    "great wall": "Great Wall of China",
    "pyramids": "Pyramids of Giza",
    "giza": "Pyramids of Giza",
    "everest": "Mount Everest",
    "liberty statue": "Statue of Liberty",
    "statue": "Statue of Liberty",
    "sophia": "Hagia Sophia",
    "eiffel": "Eiffel Tower",
    "colosseum": "Colosseum",
    "einstein": "Albert Einstein",
    "curie": "Marie Curie",
    "da vinci": "Leonardo da Vinci",
    "shakespeare": "William Shakespeare",
    "lovelace": "Ada Lovelace",
    "tesla": "Nikola Tesla",
    "messi": "Lionel Messi",
    "ronaldo": "Cristiano Ronaldo",
    "swift": "Taylor Swift",
    "kahlo": "Frida Kahlo",
    "gandhi": "Mahatma Gandhi",
    "mandela": "Nelson Mandela",
    "monroe": "Marilyn Monroe",
    "presley": "Elvis Presley",
    "picasso": "Pablo Picasso",
    "van gogh": "Vincent van Gogh",
    "hawking": "Stephen Hawking",
    "newton": "Isaac Newton",
    "galileo": "Galileo Galilei",
    "darwin": "Charles Darwin"
}


def unique_keep_order(items):
    seen = set()
    result = []

    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)

    return result


def get_entities_from_query(query):
    query_lower = query.lower()
    matches = []

    for entity in ALL_ENTITIES:
        if entity.lower() in query_lower:
            matches.append(entity)

    for alias, entity in ENTITY_ALIASES.items():
        if alias in query_lower:
            matches.append(entity)

    for country, entity in COUNTRY_TO_ENTITY.items():
        if country in query_lower:
            matches.append(entity)

    if not matches:
        for concept, entity in CONCEPT_TO_ENTITY.items():
            if concept in query_lower:
                matches.append(entity)

    return unique_keep_order(matches)


def get_intent(query):
    query_lower = query.lower()

    person_keywords = [
        "who", "person", "people", "discover", "discovered", "invent",
        "invented", "born", "scientist", "artist", "painter", "writer",
        "footballer", "singer", "composer", "physicist", "mathematician"
    ]

    place_keywords = [
        "where", "place", "located", "location", "country", "city",
        "building", "mountain", "tower", "wall", "landmark", "built",
        "used for", "visited", "monument", "structure", "turkey",
        "türkiye", "france", "china", "india", "italy", "nepal",
        "egypt", "peru", "japan", "australia", "spain", "greece",
        "jordan", "canada", "united states", "usa"
    ]

    person_score = sum(1 for keyword in person_keywords if keyword in query_lower)
    place_score = sum(1 for keyword in place_keywords if keyword in query_lower)

    if place_score > person_score:
        return "place"

    if person_score > place_score:
        return "person"

    return "both"


def is_comparison_query(query):
    query_lower = query.lower()

    comparison_words = [
        "compare",
        "comparison",
        "versus",
        "difference",
        "differences",
        "similarities",
        "similarity"
    ]

    if any(word in query_lower for word in comparison_words):
        return True

    if re.search(r"\bvs\.?\b", query_lower):
        return True

    return False


def create_embedding(text):
    response = ollama.embeddings(
        model=EMBEDDING_MODEL,
        prompt=text
    )

    return response["embedding"]


def query_collection(query_embedding, where_filter=None, n_results=5):
    if where_filter:
        return collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_filter
        )

    return collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )


def extract_documents(results):
    if not results:
        return []

    if "documents" not in results:
        return []

    if not results["documents"]:
        return []

    if not results["documents"][0]:
        return []

    return results["documents"][0]


def get_first_entity_chunks(entity, limit=2):
    try:
        results = collection.get(
            where={"entity": entity},
            include=["documents", "metadatas"]
        )

        documents = results.get("documents", [])
        ids = results.get("ids", [])

        if not documents:
            return []

        paired = list(zip(ids, documents))

        def chunk_number(item):
            chunk_id = item[0]
            match = re.search(r"_(\d+)$", chunk_id)

            if match:
                return int(match.group(1))

            return 999999

        paired.sort(key=chunk_number)

        return [doc for _, doc in paired[:limit]]

    except Exception:
        return []


def retrieve_context(query):
    intent = get_intent(query)
    target_entities = get_entities_from_query(query)
    comparison_mode = is_comparison_query(query)

    try:
        query_embedding = create_embedding(query)
    except Exception:
        return [], intent, target_entities, "Error creating embedding. Make sure Ollama is running."

    context_chunks = []

    try:
        if comparison_mode and len(target_entities) >= 2:
            for entity in target_entities:
                first_chunks = get_first_entity_chunks(entity, limit=2)

                if first_chunks:
                    for doc in first_chunks:
                        context_chunks.append(f"[Context for {entity}]\n{doc}")
                else:
                    entity_query = f"{entity} main field role known for achievement"
                    entity_embedding = create_embedding(entity_query)

                    results = query_collection(
                        query_embedding=entity_embedding,
                        where_filter={"entity": entity},
                        n_results=2
                    )

                    documents = extract_documents(results)

                    for doc in documents:
                        context_chunks.append(f"[Context for {entity}]\n{doc}")

        elif target_entities:
            for entity in target_entities:
                results = query_collection(
                    query_embedding=query_embedding,
                    where_filter={"entity": entity},
                    n_results=3
                )

                documents = extract_documents(results)

                for doc in documents:
                    context_chunks.append(f"[Context for {entity}]\n{doc}")

        else:
            where_filter = None

            if intent == "person":
                where_filter = {"type": "person"}
            elif intent == "place":
                where_filter = {"type": "place"}

            results = query_collection(
                query_embedding=query_embedding,
                where_filter=where_filter,
                n_results=5
            )

            context_chunks.extend(extract_documents(results))

    except Exception:
        return [], intent, target_entities, "Error querying database."

    context_chunks = unique_keep_order(context_chunks)

    if not context_chunks:
        return [], intent, target_entities, None

    return context_chunks, intent, target_entities, None


def build_prompt(query, context_chunks, intent, target_entities):
    context_text = "\n\n".join(context_chunks)
    detected_entities = ", ".join(target_entities) if target_entities else "None"

    if is_comparison_query(query) and len(target_entities) >= 2:
        return f"""You are a strict local Wikipedia RAG assistant.

Use only the retrieved context below to answer the comparison question.

CRITICAL RULES:
- Compare only the detected target entities.
- DO NOT merge their achievements into a single sentence. State what each person is known for individually.
- NEVER claim they worked on the same specific technology (e.g., electrical systems, relativity) unless the context explicitly says so for BOTH.
- Do not use outside knowledge.
- Do not include personal-life details, personality claims, opinions, or legacy.
- Write one short paragraph.
- Maximum 3 sentences.
- Do not use bullet points or headings.
- Do not write an introduction.
- If the retrieved context is not enough, output EXACTLY: I don't know.

Detected target entities:
{detected_entities}

Retrieved context:
{context_text}

Question:
{query}

Answer:"""

    return f"""You are a local Wikipedia RAG assistant.

Use only the retrieved context below to answer the question.

Rules:
- Do not use outside knowledge.
- Do not add examples that are not in the retrieved context.
- If the answer cannot be found in the retrieved context, output exactly: I don't know.
- Keep the answer concise.
- For simple factual questions, answer in one complete sentence.
- Do not use bullet points unless they are useful.
- Do not end with extra offers such as "Please let me know if I can help."

Detected query type:
{intent}

Detected target entities:
{detected_entities}

Retrieved context:
{context_text}

Question:
{query}

Answer:"""


def generate_answer(query):
    target_entities = get_entities_from_query(query)

    if not target_entities:
        return "I don't know.", []

    comparison_mode = is_comparison_query(query)

    context_chunks, intent, target_entities, error = retrieve_context(query)

    if error:
        return error, []

    if not context_chunks:
        return "I don't know.", []

    prompt = build_prompt(
        query=query,
        context_chunks=context_chunks,
        intent=intent,
        target_entities=target_entities
    )

    try:
        options = {
            "temperature": 0.0,
            "num_predict": 120 if comparison_mode else 90
        }

        response = ollama.chat(
            model=LLM_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a factual assistant. "
                        "Use only the provided retrieved context. "
                        "If the context is insufficient, say exactly: I don't know."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            options=options
        )

        answer = response["message"]["content"].strip()

        if not answer:
            return "I don't know.", context_chunks

        return answer, context_chunks

    except Exception:
        return "LLM error. Make sure Ollama is running and the model is installed.", []