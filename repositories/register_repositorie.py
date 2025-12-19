from db.connection import db
def is_email_exist(email:str) -> bool:
    return db.users.find_one({"email":email})
def insert_user(name, email, password):
    return db.users.insert_one({"nom" : name, "email" : email, "mot_de_passe" : password})
