from fastapi import APIRouter, Depends, HTTPException
from api.schemas import ChatRequest, ChatResponse, FeedbackRequest, ChatHistoryResponse
from api.services.chat import ChatService
from api.oauth2 import get_current_user
from sqlalchemy.orm import Session
from core.database import get_db
from typing import List

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, service: ChatService = Depends(ChatService), db: Session = Depends(get_db)):
    """
    Endpoint for the Compliance Intelligence Service.
    Receives a query, calls the Ingestion Service for context, 
    and uses LLM to generate an answer with conflict detection.
    """
    if not request.token:
         raise HTTPException(status_code=401, detail="Missing token")
         
    return await service.generate_response(request.query, request.user_id, db)

@router.get("/history/{user_id}", response_model=List[ChatHistoryResponse])
async def get_history(user_id: int, service: ChatService = Depends(ChatService), db: Session = Depends(get_db)):
    """
    Endpoint to retrieve the last 10 chats for a user.
    """
    # We can reuse the service logic or query directly. Service logic returns formatted string.
    # Let's query directly or add a method in service to return objects.
    # For simplicity, checking service first. Service.get_chat_history returns string.
    # So I will query directly here or add a new method.
    from core.models import ChatHistory
    history = db.query(ChatHistory).filter(ChatHistory.user_id == user_id).order_by(ChatHistory.created_at.desc()).limit(10).all()
    return history

@router.post("/feedback")
async def feedback_endpoint(request: FeedbackRequest, service: ChatService = Depends(ChatService)):
    """
    Endpoint for users to provide feedback on answers.
    The Memory Agent stores this to improve future responses.
    """
    await service.save_feedback(request.user_id, request.query, request.corrected_answer)
    return {"message": "Feedback received and memorized."}
