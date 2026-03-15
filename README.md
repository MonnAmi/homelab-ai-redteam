# 🤖 AI Security Pipeline

> Private RAG (Retrieval Augmented Generation) pipeline.
> Feed security books, CVEs, and research papers into my local AI.
> 100% offline. Zero cloud. My knowledge stays my.

---

## 📋 Overview

```
What this does:

1. Reads my PDF/EPUB security library (10TB)
2. Chunks text into searchable paragraphs
3. Creates vector embeddings
4. Stores in Qdrant (local NVMe)
5. AI answers questions FROM MY BOOKS
   not just from its training data
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│  RAID 5 HDD (28TB)                          │
│  /mnt/books  ← my PDF/EPUB library        │
└──────────────────┬──────────────────────────┘
                   │ read once
                   ▼
┌─────────────────────────────────────────────┐
│  VM1 — Ingestor (192.168.1.11)              │
│  PyMuPDF → chunk → sentence-transformers    │
│  Creates embeddings from my books         │
└──────────────────┬──────────────────────────┘
                   │ store vectors
                   ▼
┌─────────────────────────────────────────────┐
│  VM2 — VectorDB (192.168.1.12)              │
│  Qdrant on NVMe                             │
│  Fast semantic search                       │
└──────────────────┬──────────────────────────┘
                   │ retrieve context
                   ▼
┌─────────────────────────────────────────────┐
│  VM3 — LLM Brain (192.168.1.13)             │
│  DeepSeek R1 14B via Ollama                 │
│  RTX 3060 12GB GPU                          │
│  Answers using MY book context            │
└──────────────────┬──────────────────────────┘
                   │ serve answer
                   ▼
┌─────────────────────────────────────────────┐
│  VM4 — Agent/UI (192.168.1.14)              │
│  Open WebUI — browser chat interface        │
│  FastAPI — programmatic access              │
└─────────────────────────────────────────────┘
```

---

## 📦 Requirements

```bash
# VM1 — Ingestor
pip install pymupdf \
            sentence-transformers \
            qdrant-client \
            llama-index \
            celery \
            watchdog \
            tqdm

# VM2 — VectorDB
docker pull qdrant/qdrant

# VM3 — LLM (already done)
# Ollama + DeepSeek R1 14B ✅

# VM4 — Agent UI
docker pull ghcr.io/open-webui/open-webui:main
```

---

## 🚀 Quick Start

### 1. Start VectorDB (VM2)
```bash
docker run -d \
  --name qdrant \
  --restart always \
  -p 6333:6333 \
  -v /mnt/nvme/qdrant:/qdrant/storage \
  qdrant/qdrant
```

### 2. Run Ingestor (VM1)
```bash
# Single run — ingest all books
python3 ingest.py --books-path /mnt/books --qdrant-host 192.168.1.12

# Watch mode — auto-ingest new books as added
python3 ingest.py --watch --books-path /mnt/books --qdrant-host 192.168.1.12
```

### 3. Query My AI (VM4 or direct)
```bash
python3 query.py "What is Kerberoasting and how is it detected?"
```

---

## 📁 Files

| File | Purpose |
|---|---|
| `ingest.py` | PDF → chunks → embeddings → Qdrant |
| `query.py` | CLI interface to query my AI |
| `api.py` | FastAPI server for programmatic access |
| `config.py` | All configuration in one place |

---

## ⚙️ Configuration

Edit `config.py`:
```python
BOOKS_PATH      = "/mnt/books"          # my RAID mount
QDRANT_HOST     = "192.168.1.12"        # VM2
QDRANT_PORT     = 6333
OLLAMA_HOST     = "192.168.1.13"        # VM3
OLLAMA_PORT     = 11434
OLLAMA_MODEL    = "deepseek-r1:14b"     # my primary model
COLLECTION_NAME = "security-library"
CHUNK_SIZE      = 512                   # tokens per chunk
CHUNK_OVERLAP   = 64
```

---

## 📊 Performance

```
Ingestion speed (VM1):
├── PDF parsing:     ~50 pages/second
├── Embedding:       ~200 chunks/second (CPU)
└── Storage to Qdrant: ~1000 vectors/second

Query speed (full RAG pipeline):
├── Vector search:   < 50ms (NVMe)
├── LLM generation:  ~40-45 tok/s (RTX 3060)
└── Total response:  3-8 seconds

Storage estimate:
├── 1 book (300 pages) → ~3000 vectors
├── 10TB library       → ~200,000 books
└── Vector storage:    ~500GB on NVMe
```

---

## 🔐 Privacy

```
✅ All processing happens on my hardware
✅ No book content ever leaves my network
✅ No API calls to OpenAI/Anthropic/etc
✅ Qdrant runs locally on my NVMe
✅ Ollama runs locally with GPU
✅ Zero internet required after initial setup
```

---

## 🗺️ Roadmap

- [x] GPU passthrough for LLM VM
- [x] DeepSeek R1 14B running on RTX 3060
- [ ] VM2 Qdrant setup
- [ ] VM1 Ingestor pipeline
- [ ] VM4 Open WebUI
- [ ] Auto-watch for new books
- [ ] FastAPI endpoint
- [ ] Web dashboard for ingestion status

---

*Stack: Python 3.11 | Ollama | Qdrant | sentence-transformers | FastAPI | Docker | Ubuntu 22.04*
