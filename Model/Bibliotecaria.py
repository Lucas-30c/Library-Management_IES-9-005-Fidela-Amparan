from flask_login import UserMixin


class Bibliotecaria(UserMixin):
    def __init__(self, email="", nombre="", apellido="", password="", celular="", rol=""):
        self.email = email
        self.nombre = nombre
        self.apellido = apellido
        self.password = password
        self.celular = celular
        self.rol = rol

    def get_id(self):
        return str(self.email)
