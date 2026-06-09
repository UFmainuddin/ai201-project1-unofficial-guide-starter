"""
Milestone 5: Query pipeline — retrieval + Groq LLM generation.
"""

import os
from dotenv import load_dotenv
from groq import Groq

from embed import retrieve, get_model, get_collection

# Load API key from .env
load_dotenv()

GROQ_MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = (
    "You are a helpful assistant for Queens College students looking for "
    "off-campus housing near Flushing, Queens, New York. "
    "Answer the user's question using ONLY the information in the provided "
    "documents. Do not use any outside knowledge. "
    "If the documents do not contain enough information to answer the "
    "question, say exactly: 'I don't have enough information on that.' "
    "For every fact you state, mention which source document it came from "
    "(use the filename in brackets, e.g., [flushing_rent_prices.txt]). "
    "If source data may be outdated, say so."
)


def _get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment. Check your .env file.")
    return Groq(api_key=api_key)


def ask(question):
    """
    Full RAG pipeline: retrieve relevant chunks then generate a grounded answer.

    Args:
        question: user's question string

    Returns:
        dict with keys:
            "answer"  — the LLM's grounded response
            "sources" — list of source filenames used
    """
    # 1. Retrieve top-5 relevant chunks
    chunks = retrieve(question, top_k=5)

    if not chunks:
        return {
            "answer": "I don't have enough information on that.",
            "sources": [],
        }

    # 2. Build context block from retrieved chunks
    context_parts = []
    for chunk in chunks:
        context_parts.append(f"[{chunk['source']}]\n{chunk['text']}")
    context = "\n\n".join(context_parts)

    # 3. Build user message
    user_message = f"Context documents:\n\n{context}\n\nQuestion: {question}"

    # 4. Call Groq LLM
    client = _get_groq_client()
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.3,
        max_tokens=1024,
    )

    answer = response.choices[0].message.content

    # 5. Extract unique source filenames for attribution
    sources = list(dict.fromkeys(c["source"] for c in chunks))

    return {"answer": answer, "sources": sources}


if __name__ == "__main__":
    print("=== Milestone 5: Query Pipeline Test ===\n")

    # Pre-load model and collection (avoids slow cold start in the UI)
    print("Loading embedding model and vector store...")
    get_model()
    get_collection()
    print("Ready.\n")

    test_questions = [
        "How much does a one-bedroom apartment cost in Flushing?",
        "How do I get from Queens College to Flushing Main Street by bus?",
        "What is the best time to visit the US Open at Flushing Meadows?",  # out-of-scope test
    ]

    for question in test_questions:
        print(f"Q: {question}")
        result = ask(question)
        print(f"A: {result['answer']}")
        print(f"Sources: {', '.join(result['sources'])}")
        print()
