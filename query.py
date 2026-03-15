"""
query.py — Query your private AI security knowledge base
Searches your book library via Qdrant + answers via local LLM
100% offline — your data never leaves your server
"""

import os
import sys
import httpx
import argparse
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

# ─── Config ───────────────────────────────────────────────────────────────────

QDRANT_HOST     = os.getenv("QDRANT_HOST", "192.168.1.12")
QDRANT_PORT     = int(os.getenv("QDRANT_PORT", 6333))
OLLAMA_HOST     = os.getenv("OLLAMA_HOST", "192.168.1.13")
OLLAMA_PORT     = int(os.getenv("OLLAMA_PORT", 11434))
COLLECTION_NAME = "security-library"
EMBED_MODEL     = "all-MiniLM-L6-v2"
OLLAMA_MODEL    = os.getenv("OLLAMA_MODEL", "deepseek-r1:14b")
TOP_K           = 5   # number of book passages to retrieve

# ─── Setup ────────────────────────────────────────────────────────────────────

embedder = SentenceTransformer(EMBED_MODEL)
qdrant   = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)


# ─── Search ───────────────────────────────────────────────────────────────────

def search_books(query: str, top_k: int = TOP_K) -> list[dict]:
    """Search vector DB for relevant book passages."""
    query_vector = embedder.encode(query).tolist()
    results = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=top_k,
        with_payload=True
    )
    return [
        {
            "text":   r.payload.get("text", ""),
            "source": r.payload.get("source", "unknown"),
            "score":  round(r.score, 3)
        }
        for r in results
    ]


# ─── LLM ──────────────────────────────────────────────────────────────────────

def ask_llm(question: str, context_passages: list[dict]) -> str:
    """Send question + book context to local LLM."""
    context = "\n\n".join([
        f"[From: {p['source']}]\n{p['text']}"
        for p in context_passages
    ])

    prompt = f"""You are a cybersecurity expert assistant.
Use the following excerpts from security books and research to answer the question.
If the context doesn't contain the answer, say so clearly.

CONTEXT FROM BOOKS:
{context}

QUESTION: {question}

ANSWER:"""

    response = httpx.post(
        f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/generate",
        json={
            "model":  OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
        },
        timeout=120.0
    )
    response.raise_for_status()
    return response.json().get("response", "No response from LLM")


# ─── Main ─────────────────────────────────────────────────────────────────────

def query(question: str, verbose: bool = False) -> str:
    """Full RAG pipeline: search books → ask LLM → return answer."""
    print(f"\n[*] Searching knowledge base for: {question}")
    passages = search_books(question)

    if not passages:
        print("[!] No relevant passages found in library")
        return ask_llm(question, [])

    if verbose:
        print(f"\n[*] Top {len(passages)} relevant passages found:")
        for i, p in enumerate(passages, 1):
            print(f"  {i}. [{p['score']}] {p['source']}")
            print(f"     {p['text'][:100]}...")

    print(f"[*] Querying {OLLAMA_MODEL} on {OLLAMA_HOST}...")
    answer = ask_llm(question, passages)
    return answer


def interactive_mode():
    """Run interactive CLI chat session."""
    print(f"""
╔══════════════════════════════════════════════╗
║       Private AI Security Assistant          ║
║  Model: {OLLAMA_MODEL:<36}║
║  Knowledge: Local security library           ║
║  Privacy: 100% offline                       ║
╚══════════════════════════════════════════════╝
Type 'exit' or Ctrl+C to quit
""")
    while True:
        try:
            question = input("You: ").strip()
            if not question:
                continue
            if question.lower() in {"exit", "quit", "bye"}:
                print("Goodbye.")
                break
            answer = query(question)
            print(f"\nAI: {answer}\n")
            print("─" * 60)
        except KeyboardInterrupt:
            print("\nGoodbye.")
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query your private AI")
    parser.add_argument("question",   nargs="?",       help="Question to ask")
    parser.add_argument("--verbose",  action="store_true", help="Show source passages")
    parser.add_argument("--model",    default=OLLAMA_MODEL, help="Ollama model to use")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    args = parser.parse_args()

    OLLAMA_MODEL = args.model

    if args.interactive or not args.question:
        interactive_mode()
    else:
        answer = query(args.question, verbose=args.verbose)
        print(f"\n{answer}\n")
