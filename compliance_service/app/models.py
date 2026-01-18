from pydantic import BaseModel
from typing import List, Optional, Dict

class ChatRequest(BaseModel):
    query: str
    user_id: Optional[int] = 1
    token: Optional[str] = "demo-token"
    history: List[str] = []

class Citation(BaseModel):
    page: int
    text: str
    source: str
    score: float

class ChatResponse(BaseModel):
    answer: str
    citations: List[Citation]
    conflict_detected: bool = False
    usage: Optional[Dict] = None
