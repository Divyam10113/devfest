from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import logging
import os

from .models import ChatRequest, ChatResponse
from .rag import retrieve_documents, generate_compliance_response

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("compliance_service")

app = FastAPI(
    title="Compliance Intelligence Service (Task 4)",
    description="The Brain: Orchestrates RAG, Reasoning, and Generation.",
    version="1.0.0"
)

# CORS (Allow Frontend to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "Compliance Intelligence"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Main Chat Endpoint (Connection B in Architecture).
    Receives query -> Calls Ingestion Service -> Calls LLM -> Returns Answer.
    """
    logger.info(f"Received query: {request.query}")
    
    # 1. Retrieve Context (Internal call to Service 3)
    search_data = await retrieve_documents(request.query)
    
    # 2. Generate Answer (Reasoning & Generation)
    answer, citations, conflict = await generate_compliance_response(request.query, search_data, request.history)
    
    # 3. Return formatted response
    return ChatResponse(
        answer=answer,
        citations=citations,
        conflict_detected=conflict
    )

if __name__ == "__main__":
    import uvicorn
    # Run on Port 8003 as specified in architecture
    uvicorn.run("app.main:app", host="0.0.0.0", port=8003, reload=True)
