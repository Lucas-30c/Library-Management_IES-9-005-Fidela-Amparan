from datetime import datetime

from psycopg2 import Date

from Model.Socio import Socio
from Model.Libro import Libro
from Model.Bibliotecaria import Bibliotecaria
from Model.Devolucion import Devolucion

# SELECT prestamo.id, prestamo.iddevolucion ,socio.id, socio.apellido, socio.nombre, socio.email, socio.celular, socio.direccion, "
#  "socio.documentacion, socio.responsable, bibliotecaria.id, bibliotecaria.nombre, bibliotecaria.apellido, libro.titulo, libro.id, "
#  "prestamo.fechainicio, prestamo.fechadevolucion, prestamo.estado


class Prestamo:


    def __init__(self, fechainicio=None, fechadevolucion=None, id=0, idsocio=None, idbliotecaria="", idlibro=None, iddevolucion=None):
        self.id = id
        self.idsocio = idsocio
        self.idbibliotecaria = idbliotecaria
        self.idlibro = idlibro
        self.fechainicio = datetime(fechainicio.year,fechainicio.month,fechainicio.day)
        self.fechadevolucion = datetime(fechadevolucion.year,fechadevolucion.month,fechadevolucion.day)
        self.iddevolucion = iddevolucion

    def getState(self):
        dateNow = datetime.now()

        if self.iddevolucion is not None:
            return "Entregado"

        if self.fechadevolucion < dateNow:
            return "Vencido"
        return "Activo"







# Renovar 7 días en tabla préstamo