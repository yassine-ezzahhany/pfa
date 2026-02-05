from pydantic import EmailStr
class User :
    _id : int
    name : str
    email : EmailStr
    password : str
    def __init__(self, id, name, email, password):
        self._id = id
        self.email = email
        self.password = password
        self.name = name