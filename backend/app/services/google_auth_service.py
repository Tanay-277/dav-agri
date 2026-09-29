import logging
from typing import Dict, Any, Optional
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)

class GoogleAuthService:
    @staticmethod
    def verify_id_token(id_token_str: str) -> Dict[str, Any]:
        """Verify Google ID token against Google's tokeninfo API.
        Falls back to deterministic mock ID in development when GOOGLE_CLIENT_ID is unset.
        """
        token = id_token_str.strip()
        if not token:
            raise ValueError("Google ID token cannot be empty")

        if settings.GOOGLE_CLIENT_ID:
            url = f"https://oauth2.googleapis.com/tokeninfo?id_token={token}"
            try:
                with httpx.Client(timeout=6.0) as client:
                    resp = client.get(url)
                    if resp.status_code != 200:
                        logger.warning(f"Google tokeninfo rejected token: {resp.status_code} {resp.text}")
                        raise ValueError("Invalid Google authentication token")

                    payload = resp.json()
                    aud = payload.get("aud")
                    if aud != settings.GOOGLE_CLIENT_ID:
                        logger.error(f"Google token audience mismatch: expected {settings.GOOGLE_CLIENT_ID}, got {aud}")
                        raise ValueError("Token audience does not match configured Google Client ID")

                    sub = payload.get("sub")
                    if not sub:
                        raise ValueError("Missing Google subject identifier in token payload")

                    return {
                        "google_id": f"g_{sub}",
                        "email": payload.get("email", ""),
                        "name": payload.get("name", "Google User"),
                        "picture": payload.get("picture", "")
                    }
            except httpx.HTTPError as e:
                logger.error(f"Network error verifying Google ID token: {e}")
                raise ValueError("Failed to reach Google token verification service")
        else:
            # Development Mode fallback when credentials are not yet configured
            logger.info("[AUTH] GOOGLE_CLIENT_ID unset. Using development mock Google token resolution.")
            mock_sub = f"g_{abs(hash(token))}"
            return {
                "google_id": mock_sub,
                "email": "farmer@dav.local",
                "name": "Raj Patil",
                "picture": ""
            }
