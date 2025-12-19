from fastapi import APIRouter
from pymongo import MongoClient
from pydantic import EmailStr
from fastapi import HTTPException
from services.inputs_validator import *
from services.register_service import add_user

register_router = APIRouter()
@register_router.post("")
def ajouterUtilisateur(nom : str, email : EmailStr, motDePasse : str):
    if(validate_name(nom) == False):
        raise HTTPException(
            status_code=400,
            detail="Nom invalid"
        )
    if(validate_password(motDePasse) == False):
        raise HTTPException(
            status_code = 400,
            detail = {
                        "error": "INVALID_PASSWORD",
                        "message": "Le mot de passe ne respecte pas les règles de sécurité.",
                        "rules": [
                            "Au moins 8 caractères",
                            "Au moins une lettre majuscule",
                            "Au moins une lettre minuscule",
                            "Au moins un chiffre",
                            "Au moins un caractère spécial"
                        ]
                    }
        )
    if(add_user(nom, email, motDePasse)):
        return {"message" : "utilisateur ajoute avec succes"}
    raise HTTPException(
        status_code=400,
        detail="Email deja existe"
    )