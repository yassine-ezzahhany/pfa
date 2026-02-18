from core.connection import db

def find_by_email(email:str) -> dict:
    return db.users.find_one({"email":email})

def add_user_repository(name, email, password):
    return db.users.insert_one({"nom" : name, "email" : email, "mot_de_passe" : password})
