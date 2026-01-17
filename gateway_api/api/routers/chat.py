from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
import httpx
from ..oauth2 import get_current_user
from ..core.config import settings
import logging

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)

logger = logging.getLogger(__name__)

class ChatRequest(BaseModel):
    query: str
    user_id: Optional[int] = None
    token: Optional[str] = None

class Citation(BaseModel):
    page: int
    text: str
    source: str
    score: float

class ChatResponse(BaseModel):
    answer: str
    citations: List[Citation]
    conflict_detected: bool

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, current_user = Depends(get_current_user)):
    """
    Process a chat query using RAG.
    1. Retrieve relevant chunks from Ingestion Service.
    2. Generate answer using LLM.
    """
    
    # 1. Search for documents
    try:
        async with httpx.AsyncClient() as client:
            search_payload = {
                "query": request.query,
                "top_k": 5,
                "include_parent": True
            }
            
            logger.info(f"Calling Ingestion Service at {settings.INGESTION_SERVICE_URL}/search")
            response = await client.post(
                f"{settings.INGESTION_SERVICE_URL}/search",
                json=search_payload,
                timeout=10.0
            )
            
            if response.status_code != 200:
                logger.error(f"Ingestion service error: {response.text}")
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Failed to retrieve documents from knowledge base"
                )
            
            search_results = response.json()
            
    except httpx.RequestError as e:
        logger.error(f"Failed to connect to ingestion service: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Knowledge service unavailable: {str(e)}"
        )

    # 2. Build Context
    results = search_results.get("results", [])
    if not results:
        return ChatResponse(
            answer="I couldn't find any relevant policy documents to answer your question.",
            citations=[],
            conflict_detected=False
        )
    
    # Use parent text for better context if available, else child text
    context_parts = []
    citations = []
    
    for r in results:
        text = r.get("parent_text") or r.get("text", "")
        source = r.get("source", "Unknown")
        page = r.get("page", 0)
        score = r.get("score", 0.0)
        
        context_parts.append(f"[Source: {source}, Page: {page}]\n{text}")
        
        citations.append(Citation(
            page=page,
            text=r.get("text", "")[:200] + "...", # Snippet for UI
            source=source,
            score=score
        ))

    context = "\n\n---\n\n".join(context_parts)

    # 3. Generate Answer (if API Key available)
    if not settings.OPENAI_API_KEY:
        # Fallback if no key
        return ChatResponse(
            answer="I found relevant documents, but I cannot generate a natural language answer because the LLM is not configured (OPENAI_API_KEY missing). Please check the citations.",
            citations=citations,
            conflict_detected=False
        )

    try:
        async with httpx.AsyncClient() as client:
            llm_payload = {
                "model": "gpt-4o",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that answers internal policy questions based on the provided context. "
                                   "Always cite your sources using the format [Source, Page X]. "
                                   "If the context implies a conflict or ambiguity, mention it. "
                                   "If the answer is not in the context, say so."
                    },
                    {
                        "role": "user",
                        "content": f"Context:\n{context}\n\nQuestion: {request.query}"
                    }
                ],
                "temperature": 0.3
            }
            
            llm_response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
                json=llm_payload,
                timeout=30.0
            )
            
            if llm_response.status_code != 200:
                logger.error(f"LLM API error: {llm_response.text}")
                answer = "I encountered an error generating the detailed answer, but here are the relevant documents."
            else:
                data = llm_response.json()
                answer = data["choices"][0]["message"]["content"]
                
    except httpx.RequestError as e:
        logger.error(f"LLM Connection error: {e}")
        answer = "I encountered a connection error generating the answer. Please review the citations below."

    # 4. Return Response
    return ChatResponse(
        answer=answer,
        citations=citations,
        conflict_detected=False # Placeholder logic
    )
