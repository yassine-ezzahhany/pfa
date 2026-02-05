import bcrypt
import os

from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


# ==========================
# PASSWORD HASHING
# ==========================

def hash_password_service(password: str) -> str:
    """
    Hash un mot de passe et retourne une STRING
    (compatible stockage DB)
    """
    hashed: bytes = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    )
    return hashed.decode("utf-8")  # bytes -> str


def verify_password_service(password: str, hashed_password) -> bool:
    """
    Vérifie un mot de passe, accepte hash en str ou bytes
    """
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode("utf-8")

    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed_password
    )



def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Crée un JWT signé
    """
    to_encode = data.copy()

    expire = datetime.utcnow() + (
        expires_delta
        if expires_delta
        else timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)))
    )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        os.getenv("SECRET_KEY"),
        algorithm="HS256"
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Décode et valide un JWT
    """
    try:
        payload = jwt.decode(
            token,
            os.getenv("SECRET_KEY"),
            algorithms=["HS256"]
        )
        return payload
    except JWTError:
        return None


# ==========================
# FASTAPI SECURITY (BEARER)
# ==========================

security = HTTPBearer()


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Dépendance FastAPI pour protéger les routes
    """
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )

    email = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload
