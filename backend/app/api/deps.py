from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.security import decode_access_token
from app.database.session import get_db

auth_scheme = HTTPBearer(auto_error=False)

def get_current_user_id(credentials: Optional[HTTPAuthorizationCredentials] = Depends(auth_scheme)) -> str:
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please provide a valid Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_access_token(credentials.credentials)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload["sub"]

def get_optional_user_id(credentials: Optional[HTTPAuthorizationCredentials] = Depends(auth_scheme)) -> Optional[str]:
    if not credentials or not credentials.credentials:
        return None
    payload = decode_access_token(credentials.credentials)
    if payload and "sub" in payload:
        return payload["sub"]
    return None
