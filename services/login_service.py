from core.security import verify_password_service, create_access_token
from repositorys.register_repository import find_by_email

def login_user_service(email: str, password: str) -> dict:
    user = find_by_email(email)
    
    if not user:
        raise ValueError("Email ou mot de passe incorrect")
    
    if not verify_password_service(password, user.get("mot_de_passe")):
        raise ValueError("Email ou mot de passe incorrect")
    
    # Créer le token JWT
    access_token = create_access_token(
        data={"sub": email, "user_id": str(user.get("_id"))}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.get("_id")),
            "name": user.get("nom"),
            "email": user.get("email")
        }
    }
