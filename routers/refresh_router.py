from fastapi import APIRouter, HTTPException
from schemas.user_schema import RefreshTokenRequest
from services.login_service import refresh_access_token_service

refresh_router = APIRouter()


@refresh_router.post("")
def refresh_token_router_handler(payload: RefreshTokenRequest):
    try:
        return refresh_access_token_service(payload.refresh_token)
    except ValueError as e:
        raise HTTPException(
            status_code=401,
            detail=str(e)
        )
