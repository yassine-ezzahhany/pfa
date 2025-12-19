import bcrypt

def hash_password_service(password: str) -> str:
    # Hashe le mot de passe
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

def verify_password_service(plain_password: str, hashed_password: str) -> bool:
    # Vérifie le mot de passe
    return bcrypt.checkpw(plain_password, hashed_password)
