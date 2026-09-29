import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.query import QueryHistory

class QueryRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_by_user(self, user_id: str, limit: int = 20) -> List[QueryHistory]:
        return (
            self.db.query(QueryHistory)
            .filter(QueryHistory.user_id == user_id)
            .order_by(QueryHistory.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_by_id(self, query_id: str, user_id: Optional[str] = None) -> Optional[QueryHistory]:
        q = self.db.query(QueryHistory).filter(QueryHistory.id == query_id)
        if user_id:
            q = q.filter(QueryHistory.user_id == user_id)
        return q.first()

    def get_by_share_token(self, share_token: str) -> Optional[QueryHistory]:
        return self.db.query(QueryHistory).filter(QueryHistory.share_token == share_token).first()

    def create_query(
        self,
        user_id: str,
        query_text: str,
        query_language: str,
        intent: str,
        answer_text: str,
        visualization_data: Optional[str] = None,
        audio_url: Optional[str] = None,
        is_saved: bool = False
    ) -> QueryHistory:
        share_token = f"sh_{uuid.uuid4().hex[:12]}"
        query = QueryHistory(
            user_id=user_id,
            query_text=query_text,
            query_language=query_language,
            intent=intent,
            answer_text=answer_text,
            visualization_data=visualization_data,
            audio_url=audio_url,
            is_saved=is_saved,
            share_token=share_token
        )
        self.db.add(query)
        self.db.commit()
        self.db.refresh(query)
        return query

    def toggle_saved(self, query_id: str, user_id: str) -> Optional[QueryHistory]:
        query = self.get_by_id(query_id, user_id)
        if query:
            query.is_saved = not query.is_saved
            self.db.commit()
            self.db.refresh(query)
        return query
