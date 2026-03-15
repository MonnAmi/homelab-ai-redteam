"""
ingest.py — Security Library Ingestion Pipeline
Reads PDFs/EPUBs from RAID, creates embeddings, stores in Qdrant
100% offline — no internet required
"""

import os
import time
import argparse
import hashlib
from pathlib import Path
from tqdm import tqdm

import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct
)

# ─── Config ───────────────────────────────────────────────────────────────────

QDRANT_HOST     = os.getenv("QDRANT_HOST", "192.168.1.12")
QDRANT_PORT     = int(os.getenv("QDRANT_PORT", 6333))
COLLECTION_NAME = "security-library"
EMBED_MODEL     = "all-MiniLM-L6-v2"   # fast, good quality, runs offline
CHUNK_SIZE      = 512                   # characters per chunk
CHUNK_OVERLAP   = 64
VECTOR_DIM      = 384                   # all-MiniLM-L6-v2 output size
SUPPORTED_EXTS  = {".pdf", ".txt", ".epub"}

# ─── Setup ────────────────────────────────────────────────────────────────────

print("[*] Loading embedding model (offline)...")
embedder = SentenceTransformer(EMBED_MODEL)

client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)


def ensure_collection():
    """Create Qdrant collection if it doesn't exist."""
    collections = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in collections:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_DIM,
                distance=Distance.COSINE
            )
        )
        print(f"[+] Created collection: {COLLECTION_NAME}")
    else:
        print(f"[*] Collection exists: {COLLECTION_NAME}")


# ─── Text Extraction ──────────────────────────────────────────────────────────

def extract_text_pdf(filepath: str) -> str:
    """Extract all text from a PDF file."""
    try:
        doc = fitz.open(filepath)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        print(f"[!] Failed to read {filepath}: {e}")
        return ""


def extract_text_txt(filepath: str) -> str:
    """Read plain text file."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        print(f"[!] Failed to read {filepath}: {e}")
        return ""


def extract_text(filepath: str) -> str:
    """Route to correct extractor by file type."""
    ext = Path(filepath).suffix.lower()
    if ext == ".pdf":
        return extract_text_pdf(filepath)
    elif ext in {".txt", ".epub"}:
        return extract_text_txt(filepath)
    return ""


# ─── Chunking ─────────────────────────────────────────────────────────────────

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP):
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if len(chunk) > 50:  # skip tiny chunks
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


# ─── Ingestion ────────────────────────────────────────────────────────────────

def file_id(filepath: str) -> str:
    """Generate stable ID from filepath."""
    return hashlib.md5(filepath.encode()).hexdigest()


def ingest_file(filepath: str):
    """Full pipeline: extract → chunk → embed → store."""
    filename = Path(filepath).name
    print(f"[~] Ingesting: {filename}")

    text = extract_text(filepath)
    if not text.strip():
        print(f"[!] No text found in {filename}, skipping")
        return 0

    chunks = chunk_text(text)
    if not chunks:
        return 0

    # Create embeddings
    embeddings = embedder.encode(chunks, show_progress_bar=False)

    # Build Qdrant points
    points = []
    base_id = abs(hash(filepath)) % (10 ** 9)
    for i, (chunk, vector) in enumerate(zip(chunks, embeddings)):
        points.append(PointStruct(
            id=base_id + i,
            vector=vector.tolist(),
            payload={
                "text":     chunk,
                "source":   filename,
                "filepath": filepath,
                "chunk_id": i,
            }
        ))

    # Upload to Qdrant in batches
    batch_size = 100
    for i in range(0, len(points), batch_size):
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points[i:i + batch_size]
        )

    print(f"[+] {filename} → {len(chunks)} chunks stored")
    return len(chunks)


def ingest_directory(books_path: str):
    """Ingest all supported files in a directory recursively."""
    books_dir = Path(books_path)
    files = [
        f for f in books_dir.rglob("*")
        if f.suffix.lower() in SUPPORTED_EXTS
    ]

    print(f"[*] Found {len(files)} files to ingest")
    total_chunks = 0

    for filepath in tqdm(files, desc="Ingesting books"):
        total_chunks += ingest_file(str(filepath))

    print(f"\n[✓] Done! Total chunks stored: {total_chunks}")
    print(f"[✓] Collection: {COLLECTION_NAME} on {QDRANT_HOST}:{QDRANT_PORT}")


def watch_directory(books_path: str, interval: int = 60):
    """Watch for new files and auto-ingest."""
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

    class BookHandler(FileSystemEventHandler):
        def on_created(self, event):
            if not event.is_directory:
                ext = Path(event.src_path).suffix.lower()
                if ext in SUPPORTED_EXTS:
                    print(f"\n[+] New file detected: {event.src_path}")
                    ingest_file(event.src_path)

    observer = Observer()
    observer.schedule(BookHandler(), books_path, recursive=True)
    observer.start()
    print(f"[*] Watching {books_path} for new files...")
    print("[*] Press Ctrl+C to stop")

    try:
        while True:
            time.sleep(interval)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


# ─── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest security books into AI")
    parser.add_argument("--books-path",  default="/mnt/books", help="Path to book library")
    parser.add_argument("--qdrant-host", default=QDRANT_HOST,  help="Qdrant server IP")
    parser.add_argument("--watch",       action="store_true",  help="Watch for new files")
    args = parser.parse_args()

    QDRANT_HOST = args.qdrant_host
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

    ensure_collection()

    if args.watch:
        watch_directory(args.books_path)
    else:
        ingest_directory(args.books_path)
