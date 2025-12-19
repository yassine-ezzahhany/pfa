from fastapi import APIRouter, HTTPException
from pydantic import EmailStr
from services.inputs_validator_service import *
from services.register_service import add_user_service

register_router = APIRouter()
@register_router.post("")
def add_user_router(name : str, email : EmailStr, password : str):
    try:
        add_user_service(name, email, password)
        return {"message" : "utilisateur ajoute avec succes"}
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail = str(e)
        )