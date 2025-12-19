import re

def validate_name(name : str) -> bool:
    if not re.match(r"^[A-Za-zÀ-ÖØ-öø-ÿ\s\-]+$", name):
            return False
    return name.strip().title()

def validate_password(password: str) -> bool:
    """
    Vérifie si le mot de passe est valide
    """
    if len(password) < 8:
        return False

    if not re.search(r"[A-Z]", password):
        return False

    if not re.search(r"[a-z]", password):
        return False

    if not re.search(r"[0-9]", password):
        return False

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False

    return True
