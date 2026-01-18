
import httpx
from sqlalchemy.orm import Session
from core.models import ChatHistory
from api.schemas import Citation, ChatResponse
from core.config import settings

class ChatService:
    def __init__(self):
        pass


    async def get_chat_history_list(self, user_id: int, db: Session) -> list[str]:
        """
        Fetches the last 10 conversations from the database and formats them as a list of strings.
        """
        history = db.query(ChatHistory).filter(ChatHistory.user_id == user_id).order_by(ChatHistory.created_at.asc()).limit(10).all()
        return [f"Human: {h.query}\nAI: {h.answer}" for h in history]

    # Simple in-memory storage for feedback for the hackathon "demo"
    # In production, this goes to DB.
    feedback_store = []

    async def save_feedback(self, user_id: int, query: str, corrected_answer: str):
        self.feedback_store.append({
            "user_id": user_id, 
            "query": query, 
            "correction": corrected_answer
        })

    async def save_chat_history(self, user_id: int, query: str, answer: str, db: Session):
        # Add new chat
        new_chat = ChatHistory(user_id=user_id, query=query, answer=answer)
        db.add(new_chat)
        db.commit()
        db.refresh(new_chat)

        # Maintain only 10 latest chats
        subquery = db.query(ChatHistory.id).filter(ChatHistory.user_id == user_id).order_by(ChatHistory.created_at.desc()).limit(10).subquery()
        db.query(ChatHistory).filter(ChatHistory.user_id == user_id, ~ChatHistory.id.in_(subquery)).delete(synchronize_session=False)
        db.commit()

    async def generate_response(self, query: str, user_id: int, db: Session) -> ChatResponse:
        # 1. Get History from DB
        history_list = await self.get_chat_history_list(user_id, db)
        
        # 2. Call Compliance Service (Microservice 4)
        COMPLIANCE_SERVICE_URL = settings.COMPLIANCE_SERVICE_URL
        try:
             async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{COMPLIANCE_SERVICE_URL}/chat",
                    json={
                        "query": query, 
                        "user_id": user_id,
                        "history": history_list
                    }, 
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                
                answer = data.get("answer", "")
                citations_data = data.get("citations", [])
                conflict = data.get("conflict_detected", False)
                
                citations = [Citation(**c) for c in citations_data]

        except Exception as e:
            print(f"Error calling Compliance Service: {e}")
            return ChatResponse(answer="Sorry, I am unable to connect to the Compliance Service at the moment.", citations=[], conflict_detected=False)

        # 3. Save to History
        await self.save_chat_history(user_id, query, answer, db)

        return ChatResponse(
            answer=answer,
            citations=citations,
            conflict_detected=conflict
        )
