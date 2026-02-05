from services.inputs_validator_service import validate_name_service, validate_password_service
from core.security import hash_password_service, verify_password_service
from repositorys.register_repository import find_by_email, add_user_repository
def add_user_service(name : str, email : str, password : str) -> bool:
    #verifier le nom :
    if(validate_name_service(name) == False):
        raise ValueError("Nom invalid")
    #verifier le mot de passe :
    if(validate_password_service(password) == False):
        raise ValueError("Le mot de passe ne respecte pas les règles de sécurité")
    #verifier l'unicite d'email :
    if(find_by_email(email)):
        raise ValueError("Email deja existe")
    #hasher le mot de passe :
    try:
        password = hash_password_service(password)
    except Exception as e:
        raise ValueError("erreur hashage de mot de passe", str(e))
    #verifier la persistence :
    if not add_user_repository(name, email, password):
        raise ValueError("Erreur lors de l'insertion dans la base de donnees")
