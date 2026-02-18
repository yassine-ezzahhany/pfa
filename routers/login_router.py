from fastapi import APIRouter, HTTPException
from schemas.user_schema import UserLogin
from services.login_service import login_user_service

login_router = APIRouter()

@login_router.post("")
def login_user_router_handler(userLogin: UserLogin):
    try:
        result = login_user_service(userLogin.email, userLogin.password)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=401,
            detail=str(e)
        )