from repositories.register_repositorie import is_email_exist, insert_user
def add_user(name : str, email : str, password : str) -> bool:
    if(is_email_exist(email)):
        return False
    return insert_user(name, email, password)
