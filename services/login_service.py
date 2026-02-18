from core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from repositorys.auth_repository import find_by_email

def login_user_service(email: str, password: str) -> dict:
    user = find_by_email(email)
    
    if not user or not verify_password(password, user.get("mot_de_passe")):
        raise ValueError("Email ou mot de passe incorrect")
     
    # Créer le token JWT
    access_token = create_access_token(
        data={"sub": email, "user_id": str(user.get("_id"))}
    )
    refresh_token = create_refresh_token(
        data={"sub": email, "user_id": str(user.get("_id"))}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.get("_id")),
            "name": user.get("nom"),
            "email": user.get("email")
        }
    }


def refresh_access_token_service(refresh_token: str) -> dict:
    payload, token_error = decode_refresh_token(refresh_token)

    if payload is None:
        if token_error == "expired":
            raise ValueError("Refresh token expiré")
        raise ValueError("Refresh token invalide")

    email = payload.get("sub")
    user_id = payload.get("user_id")

    if not email or not user_id:
        raise ValueError("Refresh token invalide")

    new_access_token = create_access_token(
        data={"sub": email, "user_id": str(user_id)}
    )

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }
