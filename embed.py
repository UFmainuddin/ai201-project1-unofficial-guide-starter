"""
Milestone 4: Embed chunks and store in ChromaDB. Build retrieval function.
"""

import os
import chromadb
from sentence_transformers import SentenceTransformer

from ingest import ingest_all

CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "housing_guide"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
TOP_K = 5

# Module-level singletons — loaded once, reused by query.py
_model = None
_collection = None


def get_model():
    """Load and return the sentence-transformers embedding model (cached)."""
    global _model
    if _model is None:
        print(f"Loading embedding model: {EMBEDDING_MODEL}...")
        _model = SentenceTransformer(EMBEDDING_MODEL)
        print("Model loaded.")
    return _model


def get_collection():
    """Return the ChromaDB collection (cached after first call)."""
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        _collection = client.get_or_create_collection(name=COLLECTION_NAME)
    return _collection


def build_vector_store():
    """
    Ingest all documents, embed them, and load into ChromaDB.
    Deletes and recreates the collection to avoid stale duplicates on re-runs.
    """
    global _collection

    print("Running document ingestion pipeline...")
    chunks = ingest_all()
    print(f"Total chunks to embed: {len(chunks)}")

    model = get_model()

    # Recreate the collection to avoid duplicates
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    try:
        client.delete_collection(name=COLLECTION_NAME)
        print(f"Deleted existing collection '{COLLECTION_NAME}'")
    except Exception:
        pass
    collection = client.create_collection(name=COLLECTION_NAME)
    _collection = collection

    # Embed all chunks
    texts = [c["text"] for c in chunks]
    print("Embedding chunks...")
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=64)

    # Prepare IDs and metadata
    ids = [f"{c['source']}_chunk{c['chunk_index']}" for c in chunks]
    metadatas = [
        {"source": c["source"], "chunk_index": c["chunk_index"]}
        for c in chunks
    ]

    # Store in ChromaDB
    collection.add(
        ids=ids,
        embeddings=embeddings.tolist(),
        documents=texts,
        metadatas=metadatas,
    )

    count = collection.count()
    print(f"Stored {count} vectors in ChromaDB collection '{COLLECTION_NAME}'")
    return collection


def retrieve(query, top_k=TOP_K):
    """
    Retrieve the top-k most relevant chunks for a query string.

    Returns:
        list of dicts: {text, source, chunk_index, distance}
    """
    model = get_model()
    collection = get_collection()

    query_embedding = model.encode([query]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    output = []
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    dists = results["distances"][0]

    for doc, meta, dist in zip(docs, metas, dists):
        output.append({
            "text": doc,
            "source": meta["source"],
            "chunk_index": meta["chunk_index"],
            "distance": round(dist, 4),
        })

    return output


if __name__ == "__main__":
    print("=== Milestone 4: Embedding and Retrieval ===\n")

    # Build the vector store
    build_vector_store()

    # Test with 3 evaluation queries
    test_queries = [
        "How much does a one-bedroom apartment cost in Flushing?",
        "How do I get from Queens College to Flushing Main Street?",
        "What rights do I have if my landlord won't fix the heat?",
    ]

    print("\n--- Retrieval Tests ---\n")
    for query in test_queries:
        print(f"Query: {query}")
        results = retrieve(query)
        for i, r in enumerate(results, 1):
            print(f"  [{i}] (dist={r['distance']}) [{r['source']}] {r['text'][:120]}...")
        print()
