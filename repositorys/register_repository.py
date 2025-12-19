from db.connection import db
def is_email_exist_repository(email:str) -> bool:
    return db.users.find_one({"email":email})
def add_user_repository(name, email, password):
    return db.users.insert_one({"nom" : name, "email" : email, "mot_de_passe" : password})
