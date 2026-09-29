from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.api.deps import get_current_user_id, get_optional_user_id
from app.services.query_service import QueryService
from app.schemas.common import APIResponse
from app.schemas.query import QueryRequest, QueryResponse, ConversationItem

router = APIRouter(prefix="/query", tags=["Query & Agricultural Intelligence"])

@router.post("", response_model=APIResponse[QueryResponse])
def execute_query(
    payload: QueryRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    service = QueryService(db)
    try:
        response = service.process_query(user_id, payload)
        return APIResponse.ok(response)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Query failed: {str(e)}")

@router.get("/history", response_model=APIResponse[List[ConversationItem]])
def get_history(
    limit: int = Query(10, ge=1, le=50),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    service = QueryService(db)
    items = service.get_conversation_history(user_id, limit=limit)
    return APIResponse.ok(items)

@router.get("/share/{share_token}", response_model=APIResponse[QueryResponse])
def get_shared_query(
    share_token: str,
    db: Session = Depends(get_db)
):
    service = QueryService(db)
    res = service.get_shared_query(share_token)
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shared record not found")
    return APIResponse.ok(res)
