from pydantic import BaseModel, EmailStr, Field
from datetime import datetime 
from typing import Optional

# ===================== SCHEMAS RELATED TO USERS ==================================

# schema for the user creation
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    class Config:
        from_attributes = True

# schema for the user login information
class UserLogin(BaseModel):
    identifier: str
    password: str

# ===================== TOKEN DATA SCHEMAS ===================

class Token(BaseModel):
    access_token: str
    token_type: str

class Token_data(BaseModel):
    id: Optional[int] = None

# ====================== CHAT HISTORY SCHEMAS ========================

class ChatHistoryCreate(BaseModel):
    query: str
    answer: str

class ChatHistoryResponse(BaseModel):
    id: int
    query: str
    answer: str
    created_at: datetime
    class Config:
        from_attributes = True

# ====================== CHAT SCHEMAS ========================

class ChatRequest(BaseModel):
    query: str
    user_id: int
    token: str

class Citation(BaseModel):
    page: Optional[int] = None
    text: str

class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]
    conflict_detected: bool

class FeedbackRequest(BaseModel):
    user_id: int
    query: str
    corrected_answer: str
    token: str

