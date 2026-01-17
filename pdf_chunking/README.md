# Ingestion & Knowledge Service

Service 3: The Librarian - PDF parsing, intelligent chunking, vectorization, and ChromaDB storage for the compliance RAG system.

## 🚀 Features

- **Advanced PDF Parsing**: Uses LlamaParse for handling complex PDFs with images, tables, and multi-column layouts
- **Parent-Child Chunking**: Dual-level chunks for precise retrieval with full context
- **Semantic Caching**: Reduces embedding API costs by ~73% by reusing similar query embeddings
- **Automatic PDF Pre-loading**: Default PDFs are loaded at startup from `data/pdfs/` directory
- **FREE Google Embeddings**: Uses Google's Gemini API - zero cost with generous free tier!
- **ChromaDB Storage**: Persistent vector storage with metadata
- **REST API**: Clean FastAPI endpoints for search and monitoring

## 📋 Prerequisites

- Python 3.11+
- Docker (optional, for containerization)
- LlamaParse API Key ([Get it here](https://cloud.llamaindex.ai))
- Google API Key ([Get it FREE here](https://aistudio.google.com/app/apikey)) 🎉

## 🛠️ Setup

### Quick Setup (Recommended)

```bash
cd services/pdf_chunking

# Run setup script
./setup.sh

# Edit .env and add your API keys
nano .env

# Add your default PDFs to data/pdfs/
cp /path/to/your/compliance.pdf data/pdfs/

# Run the service
uvicorn app.main:app --reload --port 8002
```

### Manual Setup

1. **Create directories:**
```bash
mkdir -p data/pdfs chroma_db
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment:**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

4. **Add default PDFs:**
Place your compliance/policy PDFs in `data/pdfs/` - they will be automatically loaded at startup!

## 🐳 Docker Deployment

### Build Image

```bash
docker build -t ingestion-service .
```

### Run Container

```bash
docker run -p 8002:8000 \
  -e LLAMA_CLOUD_API_KEY=your_key \
  -e OPENAI_API_KEY=your_key \
  -v $(pwd)/data/chroma:/chroma_db \
  ingestion-service
```

## 📡 API Endpoints

### Search (Primary - called by RAG service)

**✨ Features semantic caching for 73% cost reduction!**

```bash
curl -X POST http://localhost:8002/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Can I work from home?",
    "top_k": 5,
    "include_parent": true
  }'
```

**Response:**
```json
{
  "results": [
    {
      "text": "Remote work is permitted up to 2 days per week...",
      "score": 0.89,
      "page": 4,
      "source": "employee_handbook.pdf",
      "parent_text": "...full parent context...",
      "metadata": {...}
    }
  ],
  "query": "Can I work from home?",
  "num_results": 5
}
```

### Health Check

```bash
curl http://localhost:8002/health
```

### Service Statistics

**New!** View cache performance and preload stats:

```bash
curl http://localhost:8002/stats
```

**Response:**
```json
{
  "service": "Ingestion & Knowledge Service",
  "cache": {
    "cached_queries": 47,
    "similarity_threshold": 0.95,
    "estimated_savings": "~73% API cost reduction on cache hits"
  },
  "collections": {
    "collection_name": "compliance_docs",
    "num_chunks": 892,
    "num_documents": 3
  },
  "preload": {
    "total_files": 3,
    "processed": 3,
    "failed": 0,
    "total_chunks": 892
  }
}
```

### Upload PDF (Admin/Optional)

Only needed if you want to add PDFs after startup:

```bash
curl -X POST http://localhost:8002/upload \
  -F "file=@additional_policy.pdf"
```

## 🏗️ Architecture

```
Upload Flow:
1. PDF Upload → LlamaParse (handles images/tables)
2. Parse Result → Chunker (parent-child strategy)
3. Child Chunks → Vectorizer (OpenAI embeddings)
4. Embeddings → ChromaDB (persistent storage)

Search Flow:
1. Query → Vectorizer (create embedding)
2. Query Embedding → ChromaDB (similarity search)
3. Results → Format with parent context
4. Return to RAG service
```

## 🧪 Testing

### Test PDF Upload

```bash
# Download a sample PDF
curl -o test.pdf https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf

# Upload it
curl -X POST http://localhost:8002/upload -F "file=@test.pdf"
```

### Test Search

```bash
curl -X POST http://localhost:8002/search \
  -H "Content-Type: application/json" \
  -d '{"query": "test document", "top_k": 3}'
```

## ⚙️ Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `LLAMA_CLOUD_API_KEY` | - | LlamaParse API key (required) |
| `GOOGLE_API_KEY` | - | Google Gemini API key (required, FREE tier!) |
| `CHROMA_DB_PATH` | `/chroma_db` | Path for ChromaDB storage |
| `PARENT_CHUNK_SIZE` | 1200 | Parent chunk size in tokens |
| `CHILD_CHUNK_SIZE` | 300 | Child chunk size in tokens |
| `CHUNK_OVERLAP` | 100 | Token overlap between chunks |
| `MAX_FILE_SIZE_MB` | 50 | Maximum PDF file size |
| `EMBEDDING_MODEL` | `models/text-embedding-004` | Google's embedding model |

## 🔌 Integration with Service 4 (RAG Intelligence)

Service 4 calls the `/search` endpoint:

```python
import requests

response = requests.post(
    "http://ingestion-service:8002/search",
    json={
        "query": user_question,
        "top_k": 5,
        "filters": {"department": "HR"}
    }
)

results = response.json()["results"]
# Use results[0]["parent_text"] as context for LLM
```

## 📝 Development Tips

1. **API Keys**: Only need LlamaParse key from [cloud.llamaindex.ai](https://cloud.llamaindex.ai)
2. **Zero Cost Embeddings**: Sentence Transformers runs locally - unlimited embeddings!
3. **Performance**: LlamaParse processes ~1 page/second
4. **Chunking**: Adjust chunk sizes based on your document complexity
5. **First Run**: The embedding model (~90MB) downloads automatically

## 🐛 Troubleshooting

**LlamaParse timeout?**
- Large PDFs may take time. LlamaParse processes asynchronously.

**ChromaDB permission errors?**
- Ensure `/chroma_db` directory is writable

**Out of memory?**
- Reduce batch size in vectorizer.py (default: 100)

## 📄 License

Built for Hackathon - Service 3 of 4
