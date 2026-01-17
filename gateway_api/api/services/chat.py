import httpx
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from core.config import settings
from api.schemas import Citation, ChatResponse
import json

class ChatService:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            api_key=settings.OPENAI_API_KEY
        )
        self.vector_db_url = settings.VECTOR_DB_URL

    async def search_documents(self, query: str) -> list[dict]:
        """
        Calls the Ingestion Service (Microservice 3) to find relevant documents.
        """
        try:
            async with httpx.AsyncClient() as client:
                # Based on Connection C: Intelligence Service -> Knowledge Service
                # For this limited template, we assume the Ingestion Service accepts 'query_text'.
                # If strictly vectors are needed, embeddings generation should happen here.
                
                response = await client.post(
                    f"{self.vector_db_url}/search",
                    json={"query_text": query, "k": 3}, 
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"Error calling Ingestion Service: {e}")
            return []

    async def get_chat_history(self, user_id: int) -> str:
        """
        Fetches past conversations from the Auth Service (Connection A/B via History).
        For now, we'll mock this or try to call the service.
        """
        # In a real scenario, we'd call http://auth-service:8001/history
        # For this template/hackathon, we'll return a placeholder or implement a simple mimic if Auth isn't ready.
        # "History Retrieval: When a user logs in, this service provides the list of past conversations."
        # We can try to fetch it.
        try:
             async with httpx.AsyncClient() as client:
                # Assuming Auth service has an endpoint for history
                response = await client.get(f"http://auth-service:8001/history/{user_id}", timeout=2.0)
                if response.status_code == 200:
                    history = response.json()
                    # Format history to string
                    return "\n".join([f"Human: {msg['query']}\nAI: {msg['response']}" for msg in history[-5:]]) # Last 5
        except Exception:
            pass
        return ""

    # Simple in-memory storage for feedback for the hackathon "demo"
    # In production, this goes to DB.
    feedback_store = []

    async def save_feedback(self, user_id: int, query: str, corrected_answer: str):
        self.feedback_store.append({
            "user_id": user_id, 
            "query": query, 
            "correction": corrected_answer
        })

    async def generate_response(self, query: str, user_id: int) -> ChatResponse:
        # 0. Get Context & Corrections
        history_text = await self.get_chat_history(user_id)
        
        # Check for relevant corrections (Memory Agent)
        # Naive "Semantic" search: if words match. Ideally we use vectors here too.
        relevant_corrections = []
        for fb in self.feedback_store:
            # Simple keyword match
            if any(word in query.lower() for word in fb['query'].lower().split()):
                relevant_corrections.append(f"User Correction for '{fb['query']}': {fb['correction']}")
        
        correction_context = "\n".join(relevant_corrections)

        # 1. Retrieve Docs
        docs = await self.search_documents(query)
        
        # Format context
        doc_text = "\n\n".join([d.get("text", "") for d in docs])
        
        final_context = f"""
        Prior Chat History:
        {history_text}
        
        Relevant Past User Corrections (LEARN FROM THIS):
        {correction_context}
        
        Document Context:
        {doc_text}
        """
        
        # 2. RAG Prompt
        prompt = ChatPromptTemplate.from_template("""
        You are a Compliance Intelligence Assistant. Answer the user's question based ONLY on the following context.
        If the answer is not in the context, say "I don't have enough information to answer that."
        
        Context:
        {context}
        
        Question: 
        {question}
        
        Answer:
        """)
        
        # 3. Generate Answer
        chain = prompt | self.llm | StrOutputParser()
        full_response = await chain.ainvoke({"context": final_context, "question": query})
        
        # 4. Conflict Detection (Separate basic check)
        conflict_detected = False
        if len(docs) > 1:
             # Very basic heuristic
             if "conflict" in full_response.lower() or "contradict" in full_response.lower():
                 conflict_detected = True

        citations = []
        for d in docs:
            citations.append(Citation(text=d.get("text", "")[:100] + "...", page=d.get("metadata", {}).get("page")))

        return ChatResponse(
            answer=full_response,
            citations=citations,
            conflict_detected=conflict_detected
        )
