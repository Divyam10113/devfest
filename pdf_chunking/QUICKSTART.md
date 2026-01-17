# 🚀 Quick Start Guide - Ingestion & Knowledge Service

Get your service running in 5 minutes!

## Step 1: Get Your API Keys

### 1. LlamaParse API Key
1. Go to [https://cloud.llamaindex.ai](https://cloud.llamaindex.ai)
2. Sign up/login
3. Create an API key
4. Copy it

### 2. Google API Key (FREE!)
1. Go to [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the key

**Both are FREE to get started!** 🎉

## Step 2: Setup Environment

```bash
cd services/pdf_chunking

# Copy environment template
cp .env.example .env

# Edit .env and paste your API keys
# LLAMA_CLOUD_API_KEY=llx-...
# GOOGLE_API_KEY=AIza...
```

## Step 3: Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 4: Run the Service

```bash
# Start the server
uvicorn app.main:app --reload --port 8002
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8002
INFO:     Initializing Ingestion & Knowledge Service...
INFO:     Service initialized successfully!
```

## Step 5: Test It!

Open a new terminal and run:

```bash
# Test health check
curl http://localhost:8002/health

# You should see:
# {"status":"healthy","service":"Ingestion & Knowledge Service","version":"1.0.0"}
```

## Step 6: Upload Your First PDF

```bash
curl -X POST http://localhost:8002/upload \
  -F "file=@your_document.pdf"
```

Success! 🎉 You should see:
```json
{
  "document_id": "doc_your_document",
  "filename": "your_document.pdf",
  "num_parent_chunks": 15,
  "num_child_chunks": 67,
  "status": "success",
  "message": "Processed 10 pages"
}
```

## Step 7: Search Your Document

```bash
curl -X POST http://localhost:8002/search \
  -H "Content-Type: application/json" \
  -d '{"query": "your question here", "top_k": 3}'
```

## 🐳 Docker Quick Start

If you prefer Docker:

```bash
# Build the image
docker build -t ingestion-service .

# Run with your API keys
docker run -p 8002:8000 \
  -e LLAMA_CLOUD_API_KEY=your_key \
  -e OPENAI_API_KEY=your_key \
  -v $(pwd)/chroma_db:/chroma_db \
  ingestion-service
```

## 🧪 Automated Testing

Use the test script:

```bash
# Test without upload
python test_service.py

# Test with upload
python test_service.py path/to/your.pdf

# Full test with search
python test_service.py path/to/your.pdf "your search query"
```

## ⚠️ Troubleshooting

**ModuleNotFoundError?**
```bash
# Make sure you're in the right directory
cd services/pdf_chunking

# Reinstall dependencies
pip install -r requirements.txt
```

**API Key errors?**
```bash
# Check your .env file exists
cat .env

# Make sure keys are set correctly (no quotes needed)
LLAMA_CLOUD_API_KEY=llx-your-key-here
OPENAI_API_KEY=sk-your-key-here
```

**Port already in use?**
```bash
# Change the port
uvicorn app.main:app --reload --port 8003
```

## 🎯 Next Steps

1. ✅ Upload some compliance PDFs to test
2. ✅ Check collection info: `curl http://localhost:8002/collections`
3. ✅ Test search with real queries
4. ✅ Integrate with Service 4 (RAG Intelligence)

## 📞 Integration Example (for Service 4)

```python
import requests

# From your RAG service, call:
response = requests.post(
    "http://localhost:8002/search",  # or "http://ingestion-service:8002" in Docker
    json={
        "query": "Can employees work from home?",
        "top_k": 5,
        "include_parent": True
    }
)

results = response.json()["results"]

# Use the parent_text as context for your LLM:
context = "\n\n".join([r["parent_text"] for r in results])
```

Happy hacking! 🏆
