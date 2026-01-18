import httpx
import os
import logging
import google.generativeai as genai
from .models import Citation
from dotenv import load_dotenv

load_dotenv()

# Configuration
INGESTION_SERVICE_URL = os.getenv("INGESTION_SERVICE_URL", "http://localhost:8002")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

logger = logging.getLogger("rag_engine")

if not GOOGLE_API_KEY:
    logger.warning("GOOGLE_API_KEY is not set. LLM features will fail.")
else:
    genai.configure(api_key=GOOGLE_API_KEY)

async def retrieve_documents(query: str, top_k: int = 5):
    """Call Service 3 to get relevant chunks."""
    async with httpx.AsyncClient() as http_client:
        try:
            logger.info(f"Searching knowledge base: {INGESTION_SERVICE_URL}/search")
            response = await http_client.post(
                f"{INGESTION_SERVICE_URL}/search",
                json={
                    "query": query,
                    "top_k": top_k,
                    "include_parent": True
                },
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to retrieve documents: {e}")
            # Fallback to empty results to prevent crash, but log error
            return {"results": []}

async def generate_compliance_response(query: str, search_results: dict, history: list[str] = []):
    """
    Generate an answer using Google Gemini with clear compliance guardrails.
    """
    results = search_results.get("results", [])
    
    # Process Citations for the UI
    citations = []
    context_parts = []
    
    for r in results:
        # Prefer parent text for context window, fall back to child text
        context_text = r.get("parent_text") or r.get("text", "")
        source_doc = r.get("source", "Unknown Policy")
        page_num = r.get("page", 0)
        
        context_parts.append(f"[Source: {source_doc}, Page: {page_num}]\n{context_text}")
        
        # Add to citations list
        citations.append(Citation(
            page=page_num,
            text=r.get("text", "")[:200], # Snippet
            source=source_doc,
            score=r.get("score", 0.0)
        ))

    if not context_parts:
        return "I could not find any specific policy documents related to your query. Please consult HR directly.", citations, False

    full_context = "\n\n---\n\n".join(context_parts)
    
    # Format History
    history_text = "\n".join(history)

    # Compliance-focused System Prompt
    system_prompt = """
    You are a Compliance Assistant for an internal company policy system.
    Your goal is to answer employee questions accurately based strictly on the provided policy documents.
    
    GUIDELINES:
    1. RELY ON CONTEXT: Only answer based on the provided context chunks. If the answer is not there, admit it.
    2. CITE SOURCES: When making a claim, reference the source document (e.g., "Scanning Policy, Page 4").
    3. DETECT CONFLICTS: If two policies seem to contradict, explicitly point this out (Conflict Detected).
    4. BE CAUTIOUS: For sensitive topics (harassment, termination, security), use guidance-oriented language, not definitive legal advice.
    5. UNCERSATINTY: If a policy is ambiguous, state "The policy implies X but does not explicitly state Y."
    
    Format your response clearly using Markdown.
    """

    user_prompt = f"""
    Context from Knowledge Base:
    {full_context}

    Prior Chat History:
    {history_text}
    
    Employee Question: {query}
    
    Please provide a helpful, accurate, and context-aware response.
    """

    try:
        # Initialize Gemini Model
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        
        # Combine prompts for simple generation
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        response = await model.generate_content_async(full_prompt)
        
        answer = response.text
        return answer, citations, False # TODO: Implement actual conflict detection logic if needed

    except Exception as e:
        logger.error(f"LLM Generation failed: {e}")
        return "I'm having trouble generating an answer right now, but I found these relevant documents.", citations, False
