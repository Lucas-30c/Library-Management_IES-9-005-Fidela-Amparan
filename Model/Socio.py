from flask_login import UserMixin


class Socio(UserMixin):
    def __init__(self, id=0, dni="", apellido="", nombre="", email="", password="", celular="", direccion="", documentacion="", responsable=""):
        self.id = id
        self.dni = dni
        self.apellido = apellido
        self.nombre = nombre
        self.email = email
        self.password = password
        self.celular = celular
        self.direccion = direccion
        self.documentacion = documentacion
        self.responsable = responsable

    def get_id(self):
        return self.email
