import psycopg2
from Model.Libro import Libro
from Model.Socio import Socio
from Model.Prestamo import Prestamo
from Model.Devolucion import Devolucion
from Model.Bibliotecaria import Bibliotecaria


class BooksDataBase:
    def __init__(self):
        self.connection = psycopg2.connect(host="localhost", database="db_biblioteca_sociosDNI", user="postgres", port="5432",
                                           password="lucas3030")
        self.cursor = self.connection.cursor()

    # BOOK
    def getAllBook(self):
        self.cursor.execute("SELECT * FROM libro ORDER BY id")
        book = self.cursor.fetchall()
        return book

    def insertBook(self, book: Libro):
        SQLinsert = f"insert into libro(descripcion, titulo, autor, numerotopologia, editorial, registronacional, soporte, estanteria, copias, lectura, estado) values ('{book.descripcion}','{book.titulo}','{book.autor}','{book.numerotopologia}','{book.editorial}','{book.registronacional}','{book.soporte}','{book.estanteria}','{book.copias}','{book.lectura}','{book.estado}');"
        self.cursor.execute(SQLinsert)
        self.connection.commit()

    def updateBook(self, book: Libro):
        q = f"UPDATE libro SET descripcion = '{book.descripcion}', titulo = '{book.titulo}', autor = '{book.autor}', numerotopologia = '{book.numerotopologia}', editorial = '{book.editorial}', registronacional = '{book.registronacional}', soporte = '{book.soporte}', estanteria = '{book.estanteria}', copias = '{book.copias}', lectura = '{book.lectura}', estado = '{book.estado}' WHERE id = {book.id}"
        self.cursor.execute(q)
        self.connection.commit()

    def getAllBookForSearching(self):
        self.cursor.execute("SELECT id, descripcion, titulo, autor, editorial, registronacional FROM libro")
        bookFilter = self.cursor.fetchall()
        return bookFilter

    def closeDB(self):
        self.connection.close()

    # MEMBER
    def getAllMember(self):
        self.cursor.execute("SELECT * FROM socio ORDER BY id")
        member = self.cursor.fetchall()
        return member

    def insertMember(self, member: Socio):
        SQLinsert = f"insert into socio(dni, apellido, nombre, email, password, celular, direccion, documentacion, responsable) values ('{member.dni}','{member.apellido}','{member.nombre}','{member.email}','{member.password}','{member.celular}','{member.direccion}','{member.documentacion}','{member.responsable}');"
        self.cursor.execute(SQLinsert)
        self.connection.commit()

    def updateMember(self, member: Socio):
        q = f"UPDATE socio SET dni = '{member.dni}', apellido = '{member.apellido}', nombre = '{member.nombre}', email = '{member.email}', password = '{member.password}', celular = {member.celular}, direccion = '{member.direccion}', documentacion = '{member.documentacion}', responsable = '{member.responsable}' WHERE id = {member.id}"
        self.cursor.execute(q)
        self.connection.commit()


    def deleteMember(self, id):
        self.cursor.execute("DELETE FROM socio WHERE id = {0} ".format(id))
        self.connection.commit()

    # PRÉSTAMO
    def getAllPrestamo(self):
        self.cursor.execute(
            "SELECT prestamo.id, prestamo.iddevolucion, socio.id, socio.apellido, socio.nombre, socio.email, socio.celular, socio.direccion, "
            "socio.documentacion, socio.responsable, bibliotecaria.email, bibliotecaria.nombre, bibliotecaria.apellido, libro.titulo, libro.id, "
            "prestamo.fechainicio, prestamo.fechadevolucion FROM socio, bibliotecaria, libro, prestamo "
            "WHERE socio.id = prestamo.idsocio AND bibliotecaria.email = prestamo.idbibliotecaria AND libro.id = prestamo.idlibro "
            "AND prestamo.iddevolucion IS NULL ORDER BY prestamo.id")
        prestamo = self.cursor.fetchall()
        return prestamo

    def insertPrestamo(self, prestamo: Prestamo):
        SQLinsert = f"insert into prestamo(idsocio, idbibliotecaria, idlibro, fechainicio, fechadevolucion) values ('{prestamo.idsocio}','{prestamo.idbibliotecaria}','{prestamo.idlibro}','{prestamo.fechainicio}','{prestamo.fechadevolucion}');"
        self.cursor.execute(SQLinsert)
        self.connection.commit()    

    def deletePrestamo(self, id):
        self.cursor.execute("DELETE FROM prestamo WHERE id = {0} ".format(id))
        self.connection.commit()

    # get id
    def getMember(self, id):
        q = f"SELECT * from socio where id = {id};"
        self.cursor.execute(q)
        return self.cursor.fetchone()

    # GET LIBRARIAN LOGIN
    def getLibrarian(self, email):
        q = f"SELECT * from bibliotecaria where email = '{email}';"
        self.cursor.execute(q)
        librarian = self.cursor.fetchone()
        if librarian is not None:
            return Bibliotecaria(librarian[0], librarian[1],librarian[2],librarian[3],librarian[4],librarian[5])
        else:
            return None

    # GET SOCIO LOGIN
    def getSocio(self, email):
        q = f"SELECT * from socio where email = '{email}';"
        self.cursor.execute(q)
        socio = self.cursor.fetchone()
        if socio is not None:
            return Socio(socio[0], socio[1], socio[2], socio[3], socio[4], socio[5], socio[6], socio[7], socio[8])
        else:
            return None

    def getDevolucion(self, id):
        q = f"SELECT * from devolucion where id = {id};"
        self.cursor.execute(q)
        return self.cursor.fetchone()

    # DEVOLUCIÓN
    def getAllDevolucion(self):
        self.cursor.execute(
            f"SELECT devolucion.id, socio.nombre, socio.apellido, socio.id, bibliotecaria.nombre, bibliotecaria.apellido, libro.titulo, libro.id, prestamo.fechainicio, devolucion.fechaentrega FROM prestamo, socio, bibliotecaria, libro, devolucion WHERE libro.id = prestamo.idlibro AND bibliotecaria.email = prestamo.idbibliotecaria AND socio.id = prestamo.idsocio AND prestamo.id = devolucion.idprestamo AND prestamo.iddevolucion != 0 ORDER BY devolucion.id")
        devolucion = self.cursor.fetchall()
        return devolucion

    def insertDevolucion(self, devolucion: Devolucion):
        SQLinsert = f"insert into devolucion(fechaentrega, idprestamo) values ('{devolucion.fechaentrega}','{devolucion.idprestamo}') RETURNING id;"
        self.cursor.execute(SQLinsert)
        iddevolucion = self.cursor.fetchone()
        self.updatePrestamo(devolucion.idprestamo, iddevolucion[0])
        self.connection.commit()

    def updatePrestamo(self, idprestamo, iddevolucion):
        self.cursor.execute(f"UPDATE prestamo SET iddevolucion = {iddevolucion} WHERE id = {idprestamo}")
        self.connection.commit()


    # get id
    def getPrestamo(self, id):
        q = f"SELECT * from prestamo where id = {id};"
        self.cursor.execute(q)
        return self.cursor.fetchone()

    # LIBRARIAN
    def getAllLibrarian(self):
        self.cursor.execute("SELECT * FROM bibliotecaria ORDER BY email")
        devolucion = self.cursor.fetchall()
        return devolucion

    def insertLibrarian(self, librarian: Bibliotecaria):
        SQLinsert = f"insert into bibliotecaria (email, nombre, apellido, password, celular, rol) values ('{librarian.email}','{librarian.nombre}','{librarian.apellido}','{librarian.password}','{librarian.celular}','{librarian.rol}');"
        self.cursor.execute(SQLinsert)
        self.connection.commit()

    # get id
    def getBook(self, id):
        q = f"SELECT * from libro where id = {id};"
        self.cursor.execute(q)
        return self.cursor.fetchone()
    
    # Cámbio de Estado en LIBROS al momento de marcarlo como préstamo
    def bookActive(self, idlibro):
        self.cursor.execute(f"UPDATE libro SET estado = 'Prestado' WHERE id = {idlibro}")
        self.connection.commit()

    def bookDevuelto(self, idlibro):
        self.cursor.execute(f"UPDATE libro SET estado = 'Disponible' WHERE id = {idlibro}")
        self.connection.commit()




    def getBookMaxID(self):
        self.cursor.execute("SELECT MAX(id) FROM  libro;")
        bookID = self.cursor.fetchone()
        return bookID[0] + 1

    def getMemberMaxID(self):
        self.cursor.execute("SELECT MAX(id) FROM  socio;")
        socioID = self.cursor.fetchone()
        return socioID[0] + 1

