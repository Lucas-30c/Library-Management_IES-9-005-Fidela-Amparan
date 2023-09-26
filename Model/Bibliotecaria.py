from flask_login import UserMixin


class Bibliotecaria(UserMixin):
    def __init__(self, email="", nombre="", apellido="", password="", celular="", rol="", cuenta=""):
        self.email = email
        self.nombre = nombre
        self.apellido = apellido
        self.password = password
        self.celular = celular
        self.rol = rol
        self.cuenta = cuenta

    def get_id(self):
        return str(self.email)
