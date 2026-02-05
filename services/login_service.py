from core.security import verify_password_service, create_access_token
from models.User import User
from repositorys.register_repository import find_by_email

def login_user_service(email: str, password: str) -> dict:
    """
    Authentifie un utilisateur et retourne un JWT
    """
    # Chercher l'utilisateur par email
    data = find_by_email(email)
    
    if not data:
        raise ValueError("Email ou mot de passe incorrect")
    user = User(
    id=data["_id"],
    email=data["email"],
    password=data["mot_de_passe"],
    name=data["nom"]
)
    
    # Vérifier le mot de passe (la base de données stocke "mot_de_passe")
    if not verify_password_service(password, user.password):
        raise ValueError("Email ou mot de passe incorrect")
    
    # Créer le token JWT
    access_token = create_access_token(
        data={"sub": email, "user_id": str(user._id)}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user._id),
            "name": (user.name),
            "email": (user.email)
        }
    }
