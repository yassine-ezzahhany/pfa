from core.connection import db

def find_user_by_email_repository(email:str) -> dict:
    return db.users.find_one({"email":email})

def add_user_repository(name, email, password_hash):
    return db.users.insert_one({"name": name, "email": email, "password_hash": password_hash})
