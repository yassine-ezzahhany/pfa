from typing import Optional
from pydantic import BaseModel, EmailStr

class User(BaseModel):
    id: Optional[int] = None       # champ facultatif
    nom: str
    email: EmailStr                # validation automatique email
    password: Optional[str] = None # champ facultatif