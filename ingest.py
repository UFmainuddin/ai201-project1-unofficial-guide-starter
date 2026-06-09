"""
Milestone 3: Document ingestion pipeline.
Loads .txt files from documents/, cleans them, and splits into chunks.
"""

import os
import re


DOCUMENTS_FOLDER = "documents"
CHUNK_SIZE = 300
CHUNK_OVERLAP = 50


def load_documents(folder=DOCUMENTS_FOLDER):
    """
    Load all .txt files from the documents folder.
    Returns a list of dicts: {filename, content}
    """
    docs = []
    for filename in sorted(os.listdir(folder)):
        if not filename.endswith(".txt"):
            continue
        if filename == ".gitkeep":
            continue
        filepath = os.path.join(folder, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            docs.append({"filename": filename, "content": content})
        except Exception as e:
            print(f"  [WARN] Could not read {filename}: {e}")
    return docs


def clean_text(text):
    """
    Clean a document's text content:
    - Strip the metadata header (Source/Accessed/Description lines and the --- divider)
    - Collapse multiple whitespace and newlines into single spaces
    - Remove non-printable characters
    """
    # Remove the metadata header block (everything up to and including the first "---" line)
    if "---" in text:
        parts = text.split("---", 1)
        text = parts[1] if len(parts) > 1 else text

    # Replace newlines and tabs with spaces
    text = re.sub(r"[\r\n\t]+", " ", text)

    # Collapse multiple spaces into one
    text = re.sub(r" {2,}", " ", text)

    # Remove non-printable / non-ASCII characters (keep standard ASCII + common Unicode)
    text = text.encode("utf-8", errors="ignore").decode("utf-8")

    return text.strip()


def chunk_text(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """
    Split text into overlapping chunks using a sliding window.

    Args:
        text: cleaned text string
        size: chunk size in characters (default 300)
        overlap: overlap between consecutive chunks in characters (default 50)

    Returns:
        list of chunk strings
    """
    if not text:
        return []

    chunks = []
    step = size - overlap
    start = 0

    while start < len(text):
        end = min(start + size, len(text))

        # Snap end to nearest word boundary so we don't cut mid-word
        if end < len(text) and text[end] != " ":
            last_space = text.rfind(" ", start, end)
            if last_space > start:
                end = last_space

        chunk = text[start:end].strip()

        # Skip very short final fragments (less than 50 chars is not useful)
        if len(chunk) < 50 and chunks:
            break

        if chunk:
            chunks.append(chunk)

        # Advance to next start, snapping to the next word boundary
        next_start = start + step
        if next_start < len(text) and text[next_start] != " ":
            next_space = text.find(" ", next_start)
            next_start = next_space + 1 if next_space != -1 else len(text)

        if next_start <= start:
            break
        start = next_start

    return chunks


def ingest_all(folder=DOCUMENTS_FOLDER):
    """
    Full ingestion pipeline: load -> clean -> chunk all documents.

    Returns:
        list of dicts: {text, source, chunk_index}
    """
    docs = load_documents(folder)
    all_chunks = []

    for doc in docs:
        cleaned = clean_text(doc["content"])
        chunks = chunk_text(cleaned)
        for i, chunk_text_item in enumerate(chunks):
            all_chunks.append({
                "text": chunk_text_item,
                "source": doc["filename"],
                "chunk_index": i,
            })

    return all_chunks


if __name__ == "__main__":
    print("=== Milestone 3: Document Ingestion Pipeline ===\n")

    docs = load_documents()
    print(f"Documents loaded: {len(docs)}")
    for doc in docs:
        print(f"  {doc['filename']} ({len(doc['content']):,} chars raw)")

    print()
    chunks = ingest_all()
    print(f"Total chunks produced: {len(chunks)}")
    print(f"Chunk size: {CHUNK_SIZE} chars, overlap: {CHUNK_OVERLAP} chars\n")

    print("--- 5 Sample Chunks ---\n")
    # Show chunks from different documents for variety
    seen_sources = set()
    shown = 0
    for chunk in chunks:
        if chunk["source"] not in seen_sources and shown < 5:
            print(f"[Source: {chunk['source']}, chunk #{chunk['chunk_index']}]")
            print(f"Length: {len(chunk['text'])} chars")
            print(chunk["text"])
            print()
            seen_sources.add(chunk["source"])
            shown += 1
