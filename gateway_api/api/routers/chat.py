from fastapi import APIRouter, Depends, HTTPException
from api.schemas import ChatRequest, ChatResponse, FeedbackRequest
from api.services.chat import ChatService
from api.routers.auth import get_current_user  # Assuming auth router exposes this or we use a common dependency

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, service: ChatService = Depends(ChatService)):
    """
    Endpoint for the Compliance Intelligence Service.
    Receives a query, calls the Ingestion Service for context, 
    and uses LLM to generate an answer with conflict detection.
    """
    if not request.token:
         raise HTTPException(status_code=401, detail="Missing token")
         
    return await service.generate_response(request.query, request.user_id)

@router.post("/feedback")
async def feedback_endpoint(request: FeedbackRequest, service: ChatService = Depends(ChatService)):
    """
    Endpoint for users to provide feedback on answers.
    The Memory Agent stores this to improve future responses.
    """
    await service.save_feedback(request.user_id, request.query, request.corrected_answer)
    return {"message": "Feedback received and memorized."}
