from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.farm import StructuredVisualization

class QueryRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Farmer natural language query or transcribed text")
    language: str = Field("mr", pattern="^(en|hi|mr)$", description="Language code: en, hi, mr")
    crop: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class QueryResponse(BaseModel):
    id: str
    query: str
    language: str
    intent: str
    answer: str
    source: str = "mock"
    visualization: Optional[StructuredVisualization] = None
    sources: List[str] = Field(default_factory=list)
    share_token: Optional[str] = None
    created_at: datetime

class ConversationItem(BaseModel):
    id: str
    query_text: str
    query_language: str
    intent: Optional[str]
    answer_text: str
    visualization_data: Optional[Dict[str, Any]] = None
    is_saved: bool
    share_token: Optional[str]
    created_at: datetime
