from fastapi import APIRouter, HTTPException
from schemas.user_schema import UserRegister
from services.inputs_validator_service import *
from services.register_service import add_user_service

register_router = APIRouter()
@register_router.post("")
def add_user_router(user_register : UserRegister):
    try:
        add_user_service(user_register.name, user_register.email, user_register.password)
        return {"message" : "utilisateur ajoute avec succes"}
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail = str(e)
        )