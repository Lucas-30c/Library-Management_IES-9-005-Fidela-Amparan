from Model.Bibliotecaria import Bibliotecaria
from Model.Devolucion import Devolucion
from Model.Libro import Libro
from Model.Prestamo import Prestamo
from Model.Socio import Socio
from db.DataBaseBiblioteca import BooksDataBase


class PrestamoDataView:
    def __init__(self, prestamo, socio, bibliotecaria, libro, devolucion):
        self.prestamo = prestamo
        self.socio = socio
        self.bibliotecaria = bibliotecaria
        self.libro = libro
        self.devolucion = devolucion

class PrestamoDataViewList:

    def __init__(self, prestamosTuples):
        self.list = []
        for p in prestamosTuples:
            prestamo = Prestamo(fechainicio=p[15], fechadevolucion=p[16], id=p[0])
            socio = Socio(p[2], apellido=p[3], nombre=p[4], email=p[5], celular=p[6], direccion=p[7], documentacion=p[8],
                          responsable=p[9])
            libro = Libro(titulo=p[13], id=p[14])
            bibliotecaria = Bibliotecaria(email=p[10], nombre=p[11], apellido=p[12])
            devolucion = Devolucion(id=p[1])
            self.list.append(PrestamoDataView(prestamo, socio,bibliotecaria,libro,devolucion))
