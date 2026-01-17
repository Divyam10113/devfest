# Integration Guide for Service 4 (RAG Intelligence)

Hey teammate! Here's how to integrate with the Ingestion & Knowledge Service 🚀

## 📍 Service Location

- **Local**: `http://localhost:8002`
- **Docker**: `http://ingestion-service:8002` (use service name in docker-compose)

## 🔌 Main Endpoint You'll Use

### POST /search

This is your primary endpoint. It searches the vector database and returns relevant chunks.

## 📋 Request Format

```python
import requests

def search_documents(query: str, top_k: int = 5):
    """
    Search the knowledge base for relevant context.
    
    Args:
        query: User's natural language question
        top_k: Number of results to return (default 5)
    
    Returns:
        List of relevant chunks with parent context
    """
    response = requests.post(
        "http://localhost:8002/search",
        json={
            "query": query,
            "top_k": top_k,
            "include_parent": True  # IMPORTANT: Get parent chunks for LLM
        }
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Search failed: {response.text}")
```

## 📦 Response Format

```json
{
  "results": [
    {
      "text": "Child chunk text (300 tokens)",
      "score": 0.89,  # Similarity score (0-1, higher is better)
      "page": 4,      # Page number for citations
      "source": "employee_handbook.pdf",
      "parent_text": "Full parent chunk with more context (1200 tokens)",
      "metadata": {
        "parent_id": "...",
        "token_count": 298
      }
    },
    // ... more results
  ],
  "query": "Can I work from home?",
  "num_results": 5
}
```

## 💡 How to Use the Results

### Option 1: Use Parent Text for LLM Context (RECOMMENDED)

```python
def build_llm_context(search_results):
    """Build context from parent chunks."""
    context_parts = []
    
    for result in search_results["results"]:
        # Use parent_text for richer context
        context_parts.append(
            f"[Source: {result['source']}, Page {result['page']}]\n"
            f"{result['parent_text']}\n"
        )
    
    return "\n\n---\n\n".join(context_parts)

# Use with your LLM
context = build_llm_context(search_results)
prompt = f"""
Based on the following context from our policy documents, answer the question.

Context:
{context}

Question: {user_question}

Answer:
"""
```

### Option 2: Use Child Text for Precise Snippets

```python
def get_quick_snippets(search_results):
    """Get concise snippets for quick answers."""
    snippets = []
    
    for result in search_results["results"]:
        snippets.append({
            "text": result["text"],  # Child chunk (precise)
            "source": result["source"],
            "page": result["page"],
            "relevance": result["score"]
        })
    
    return snippets
```

## 🎯 Complete Integration Example

```python
import requests
from openai import OpenAI

class RAGSystem:
    def __init__(self):
        self.search_url = "http://localhost:8002/search"
        self.openai = OpenAI()
    
    def answer_question(self, user_question: str) -> dict:
        """
        Answer user question using RAG.
        
        Returns:
            {
                "answer": str,
                "sources": list,
                "context_used": str
            }
        """
        # Step 1: Search for relevant context
        search_response = requests.post(
            self.search_url,
            json={
                "query": user_question,
                "top_k": 5,
                "include_parent": True
            }
        )
        
        results = search_response.json()["results"]
        
        # Step 2: Build context from parent chunks
        context = "\n\n".join([
            f"[Source: {r['source']}, Page {r['page']}]\n{r['parent_text']}"
            for r in results
        ])
        
        # Step 3: Query LLM with context
        llm_response = self.openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that answers questions based on provided policy documents. Always cite sources."
                },
                {
                    "role": "user",
                    "content": f"""
Context from policy documents:
{context}

Question: {user_question}

Please answer the question based on the context above. Include citations with [Source: filename, Page X] format.
"""
                }
            ]
        )
        
        answer = llm_response.choices[0].message.content
        
        # Step 4: Extract sources for UI
        sources = [
            {
                "document": r["source"],
                "page": r["page"],
                "relevance_score": r["score"]
            }
            for r in results
        ]
        
        return {
            "answer": answer,
            "sources": sources,
            "context_used": context
        }

# Usage
rag = RAGSystem()
result = rag.answer_question("Can I work from home?")

print(result["answer"])
print("\nSources:")
for src in result["sources"]:
    print(f"  - {src['document']} (Page {src['page']}) - Relevance: {src['relevance_score']:.2f}")
```

## 🔍 Advanced: Filters

You can filter results by metadata:

```python
response = requests.post(
    "http://localhost:8002/search",
    json={
        "query": "vacation policy",
        "top_k": 3,
        "filters": {
            "source": "employee_handbook.pdf"  # Only search this document
        }
    }
)
```

## 🩺 Health Check

Before making search requests, check if the service is ready:

```python
def is_service_ready():
    try:
        response = requests.get("http://localhost:8002/health")
        return response.status_code == 200
    except:
        return False

if not is_service_ready():
    print("⚠️ Ingestion service is not ready!")
```

## 📊 Get Service Stats

Monitor cache performance and loaded documents:

```python
stats = requests.get("http://localhost:8002/stats").json()

print(f"Cached queries: {stats['cache']['cached_queries']}")
print(f"Total chunks: {stats['collections']['num_chunks']}")
print(f"Documents loaded: {stats['preload']['processed']}")
```

## 🚨 Error Handling

```python
def safe_search(query: str):
    try:
        response = requests.post(
            "http://localhost:8002/search",
            json={"query": query, "top_k": 5},
            timeout=10  # 10 second timeout
        )
        response.raise_for_status()
        return response.json()
    
    except requests.Timeout:
        print("⏱️ Search timed out")
        return None
    
    except requests.ConnectionError:
        print("🔌 Cannot connect to ingestion service")
        return None
    
    except Exception as e:
        print(f"❌ Search error: {e}")
        return None
```

## 💬 Quick Test

Test the integration from your terminal:

```bash
# Test search
curl -X POST http://localhost:8002/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the vacation policy?",
    "top_k": 3
  }' | jq

# Check stats
curl http://localhost:8002/stats | jq
```

## 📝 Notes

- **Semantic Caching**: Similar queries are cached automatically - no action needed on your end!
- **Parent vs Child**: Always use `"include_parent": true` for better LLM context
- **Citations**: Use the `page` and `source` fields to show citations in your UI
- **Top-K**: Start with 5 results, adjust based on answer quality

## 🎓 Tips for Hackathon

1. **Show citations**: Display source documents and page numbers in your UI
2. **Show relevance scores**: Use the `score` field to show how relevant each source is
3. **Error handling**: Gracefully handle service downtime
4. **Cache benefits**: Monitor `/stats` to show cost savings to judges

Need help? Check:
- [README.md](file:///Users/divyansh/Desktop/devfest/services/pdf_chunking/README.md) - Full documentation
- [QUICKSTART.md](file:///Users/divyansh/Desktop/devfest/services/pdf_chunking/QUICKSTART.md) - Quick start guide

Happy integrating! 🚀
