from flask import Flask, request, redirect, url_for, render_template, flash, session
from flask_login import LoginManager, login_user, login_required, logout_user
from Model.Libro import Libro
from Model.PrestamoDataView import PrestamoDataViewList
from Model.Socio import Socio
from Model.Prestamo import Prestamo
from Model.Bibliotecaria import Bibliotecaria
from Model.Devolucion import Devolucion
from Utils.str_functions import build_list
from db.DataBaseBiblioteca import BooksDataBase
from datetime import timedelta, datetime
from werkzeug.security import generate_password_hash, check_password_hash
from Utils.filterBook import FilterBook
from Utils.authorization import authorization_required, LEVEL_2, LEVEL_1, LEVEL_0

login_manager = LoginManager()

app = Flask(__name__)
app.secret_key = 'mysecretkey'
db = BooksDataBase()
login_manager.init_app(app)

@app.route('/not_authorized')
def access_not_authorized():
    usuario = session['_user_id']
    logout_user()
    flash(' Sesión cerrada.', 'error')
    return render_template("not_authorized.html", user_id=usuario)

@login_manager.user_loader
def load_user(user_id):
    librarian = db.getLibrarian(user_id)
    if librarian:
        return librarian
    else:
        socio = db.getSocio(user_id)
        return socio

# -----------  HOME PAGE  -----------
@app.route('/')
def home():
    
    # year copyright
    now = datetime.now()
    yearNow = now.strftime('%Y')
    return render_template('home.html', yearNow=yearNow)


@app.route('/InicioUser')
@login_required
def inicioUser():

    # year copyright
    now = datetime.now()
    yearNow = now.strftime('%Y')
    return render_template("homeUser.html", yearNow=yearNow)


@app.route('/InicioLibrarian')
@login_required
def homeLibrarian():

    # year copyright
    now = datetime.now()
    yearNow = now.strftime('%Y')
    return render_template("homeLibrarian.html", yearNow=yearNow)


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if email and password:
            librarian = db.getLibrarian(email)
            if librarian and check_password_hash(librarian.password, password):
                login_user(librarian)
                session["user_rol"] = librarian.rol
                return redirect(url_for('homeLibrarian'))

            socio = db.getSocio(email)
            if socio and check_password_hash(socio.password, password):
                login_user(socio)
                session["user_rol"] = 'socio'
                return redirect(url_for('inicioUser'))

            flash('Email/Contraseña inválida.', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')


# -----------  CERRAR SESIÓN  -----------
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash(' Sesión cerrada.', 'error')
    return redirect(url_for('login'))


@app.route('/selectionAge')
def selectionAge():
    return render_template("selectionAge.html")


# -----------  REGISTER USER  -----------
@app.route('/formRegister')
def goFormRegister():
    return render_template("formRegister.html")


# -----------  SAVE REGISTER USER MAYOR 18 -----------
@app.route('/formularioRegistro/salvarFormularioRegistro', methods=['POST', 'GET'])
def saveFormPeople():
    if request.method == 'POST':
        password = request.form['password']
        _hashed_password = generate_password_hash(password)

        dni = '------'
        documentacion = 'DEBE ENTREGAR'
        responsable = 'MAYOR DE 18'

        member = Socio(dni=dni, apellido=request.form.get("Apellido"),
                       nombre=request.form.get("Nombre"), email=request.form.get("email"), password=(_hashed_password),
                       celular=request.form.get("Celular"), direccion=request.form.get("direccion"),
                       documentacion=documentacion, responsable=responsable)

        db.insertMember(member=member)
        flash(' Registro completado.', 'success')

    return redirect(url_for('login'))


@app.route('/formRegisterMenor')
def goFormRegisterMenor():
    return render_template("formRegisterMenor.html")


# -----------  SAVE REGISTER USER MENOR 18 -----------
@app.route('/formularioRegistro/salvarFormularioRegistroMenor', methods=['POST', 'GET'])
def saveFormPeopleMenor():
    if request.method == 'POST':
        password = request.form['password']
        _hashed_password = generate_password_hash(password)

        dni = '------'
        documentacion = 'DEBE ENTREGAR'

        member = Socio(dni=dni, apellido=request.form.get("Apellido"),
                       nombre=request.form.get("Nombre"), email=request.form.get("email"), password=(_hashed_password),
                       celular=request.form.get("Celular"), direccion=request.form.get("direccion"),
                       documentacion=documentacion, responsable=request.form.get("responsable"))

        db.insertMember(member=member)
        flash(' Registro completado.', 'success')

    return redirect(url_for('login'))


# --------  CARGAR BIBLITOECARIA    ENCRIPTADA  ---------
@app.route('/registerLibrarianBIBLIOTECA', methods=['POST', 'GET'])
@login_required
def saveFormLibrarian():
    if request.method == 'POST':
        password = request.form['password']

        _hashed_password = generate_password_hash(password)

        librarian = Bibliotecaria(email=request.form.get("email"), nombre=request.form.get("Nombre"),
                                  apellido=request.form.get("Apellido"), password=_hashed_password,
                                  celular=request.form.get("Celular"), rol=request.form.get("Rol"))

        db.insertLibrarian(librarian=librarian)
        flash(' Bibliotecaria cargada.', 'success')
        return redirect(url_for('login'))
    return render_template("registerLibrarian.html")


# -----------  EXPLORAR LIBROS PUBLIC -----------
@app.route('/exploreBooksPublic')
def exploreBooks():
    return render_template("exploreBooksPublic.html")


@app.route('/buscar', methods=['POST'])
def searchingBooksPublic():
    if request.method == 'POST':
        search = request.form['search']
        search_index = FilterBook()
        records = search_index.get_records_by_keys(build_list(search))
        books = []
        for id in records:
            books.append(db.getBook(id))

        return render_template("exploreBooksPublic.html", books=books)

    return render_template("exploreBooksPublic.html")


# -----------  EXPLORAR LIBROS USER -----------
@app.route('/exploreBooksUser')
def exploreBooksUser():
    return render_template("exploreBooksUser.html")


@app.route('/buscarLibros', methods=['POST'])
def searchingBooksUser():
    if request.method == 'POST':
        search = request.form['search']
        search_index = FilterBook()
        records = search_index.get_records_by_keys(build_list(search))
        books = []
        for id in records:
            books.append(db.getBook(id))

        return render_template("exploreBooksUser.html", books=books)

    return render_template("exploreBooksUser.html")


# -----------  EXPLORAR LIBROS LIBRARIAN -----------
@app.route('/exploreBooksLibrarian', endpoint='exploreBooksLibrarian')
@login_required
@authorization_required(level=session, level_required=LEVEL_0, error=access_not_authorized)
def exploreBooksLibrarian():
    return render_template("exploreBooksLibrarian.html", user_rol=session['user_rol'])


@app.route('/buscarLibro', methods=['POST'], endpoint='searchingBooksLibrarian')
@login_required
@authorization_required(level=session, level_required=LEVEL_0, error=access_not_authorized)
def searchingBooksLibrarian():
    if request.method == 'POST':
        search = request.form['search']
        search_index = FilterBook()
        records = search_index.get_records_by_keys(build_list(search))
        books = []
        for id in records:
            books.append(db.getBook(id))

        return render_template("exploreBooksLibrarian.html", books=books, user_rol=session['user_rol'])

    return render_template("exploreBooksLibrarian.html")


# -----------  ABOUT ON  -----------
@app.route('/aboutOn')
def goAboutOn():
    return render_template("aboutOn.html")


@app.route('/aboutOnPublic')
def goAboutOnPublic():
    return render_template("aboutOnPublic.html")


@app.route('/aboutOnLibrarian')
@login_required
def goAboutOnLibrarian():
    return render_template("aboutOnLibrarian.html")


# -------------------------------------------
#            FUNCTIONS LIBRARYAN
# -------------------------------------------

# -----------------------------------------  BOOK  -----------------------------------------
# -----------  SHOW BOOK  -----------
@app.route('/ver_libro/<id>', endpoint='ver_libro')
@login_required
@authorization_required(level=session, level_required=LEVEL_0, error=access_not_authorized)
def ver_libro(id):
    libro = db.getBook(int(id))
    return render_template("show_book.html", book=libro, user_rol=session['user_rol'])


# -----------  UPDATE BOOK  -----------
@app.route('/updateBook/<id>', methods=['GET', 'POST'], endpoint='updateBook')
@login_required
@authorization_required(level=session, level_required=LEVEL_1, error=access_not_authorized)
def updateBook(id):
    if request.method == 'GET':
        book = db.getBook(id)
        return render_template("updateBook.html", book=book)

    if request.method == "POST":
        descripcion = request.form['Descripcion']
        titulo = request.form['Titulo']
        autor = request.form['Autor']
        numerotopologia = request.form['NumeroTopologia']
        editorial = request.form['Editorial']
        registronacional = request.form['NumeroRegistroNacional']
        soporte = request.form['Soporte']
        estanteria = request.form['Estanteria']
        copias = request.form['Copias']
        lectura = request.form['Lectura']
        estado = request.form['Estado']
        newBook = Libro(id, descripcion, titulo, autor, numerotopologia,
                        editorial, registronacional, soporte, estanteria, copias, lectura, estado)
        db.updateBook(newBook)
        flash(' Libro modificado.', 'bookEdit')
        return redirect(url_for('exploreBooksLibrarian'))


# -----------  REGISTER BOOK  -----------
@app.route('/registrarLibros', endpoint='goRegisrerBook')
@login_required
@authorization_required(level=session, level_required=LEVEL_1, error=access_not_authorized)
def goRegisterBook():
    idMaxBook = db.getBookMaxID()
    return render_template("formBook.html", idMaxBook=idMaxBook)


# -----------  SAVE REGISTER BOOK  -----------
@app.route('/registroDeLibros/salvarLibro', methods=['POST', 'GET'], endpoint='saveBook')
@login_required
@authorization_required(level=session, level_required=LEVEL_1, error=access_not_authorized)
def saveBook():
    if request.method == 'POST':
        book = Libro(descripcion=request.form.get("Descripcion"), titulo=request.form.get("Titulo"),
                     autor=request.form.get("Autor"), numerotopologia=request.form.get("NumeroTopologia"),
                     editorial=request.form.get(
                         "Editorial"), registronacional=request.form.get("NumeroRegistroNacional"),
                     soporte=request.form.get("Soporte"), estanteria=request.form.get("Estanteria"),
                     copias=request.form.get("Copias"), lectura=request.form.get("Lectura"), estado=request.form.get("Estado"))
        db.insertBook(book=book)
        flash(' Libro registrado.', 'exitoFormPrestamo')
    return redirect(url_for('exploreBooksLibrarian'))


# -----------------------------------------  MEMBER  -----------------------------------------
# -----------  SHOW MEMBERS  -----------
@app.route('/showMembers', endpoint='showMembers')
@login_required
def showMembers():
    data = db.getAllMember()
    return render_template('show_members.html', members=data, user_rol=session['user_rol'])


# -----------  FORM REGISTER MEMBERS  -----------
@app.route('/formRegisterMember', endpoint='goFormRegisterMember')
@login_required
@authorization_required(level=session, level_required=LEVEL_0, error=access_not_authorized)
def goFormRegisterMember():
    idMaxMember = db.getMemberMaxID()
    return render_template("formRegisterMember.html", idMaxMember=idMaxMember)


# -----------  SAVE REGISTER MEMBER  -----------
@app.route('/salvarFormularioSocios', methods=['POST', 'GET'], endpoint='saveFormPeopleMember')
@login_required
@authorization_required(level=session, level_required=LEVEL_0, error=access_not_authorized)
def saveFormPeopleMember():
    if request.method == 'POST':
        password = request.form['password']

        _hashed_password = generate_password_hash(password)

        member = Socio(dni=request.form.get("dni"), apellido=request.form.get("Apellido"),
                       nombre=request.form.get("Nombre"),
                       email=request.form.get("email"), password=(_hashed_password),
                       celular=request.form.get("Celular"), direccion=request.form.get("direccion"),
                       documentacion=request.form.get("documentacion"), responsable=request.form.get("responsable"))

        db.insertMember(member=member)
        flash(' Registro completado.', 'memberDelete')

    return redirect('/showMembers')


# -----------  UPDATE MEMBER  -----------
@app.route('/updateMember/<id>', methods=['GET', 'POST'], endpoint='updateMember')
@login_required
@authorization_required(level=session, level_required=LEVEL_0, error=access_not_authorized)
def updateMember(id):
    if request.method == 'GET':
        member = db.getMember(id)
        return render_template("updateMember.html", member=member)

    if request.method == "POST":
        password = request.form['password']
        _hashed_password = generate_password_hash(password)

        dni = request.form['dni']
        apellido = request.form['apellido']
        nombre = request.form['nombre']
        email = request.form['email']
        passwordEncriptada = _hashed_password
        celular = request.form['celular']
        direccion = request.form['direccion']
        documentacion = request.form['documentacion']
        responsable = request.form['responsable']
        newMember = Socio(id, dni, apellido, nombre, email,
                          passwordEncriptada, celular, direccion, documentacion, responsable)
        db.updateMember(newMember)
        flash(' Socio actualizado.', 'memberEdit')
    return redirect('/showMembers')


# -----------  DELEETE MEMBER  -----------
@app.route('/deleteMember/<int:id>', methods=['GET'], endpoint='destroyMember')
@login_required
@authorization_required(level=session, level_required=LEVEL_2, error=access_not_authorized)
def destroyMember(id):
    if request.method == 'GET':
        db.deleteMember(id)
        flash(' Socio eliminado.', 'memberDelete')
    return redirect('/showMembers')


# -----------------------------------------  PRESTAMO  -----------------------------------------
# -----------  SHOW PRESTAMO  -----------
# @app.route('/showPrestamo', endpoint='showPrestamo', methods=['GET'])
# @login_required
# def showPrestamo():
#     dataPrestamo = db.getAllPrestamo()
#     prestamo = PrestamoDataViewList(dataPrestamo)
#     return render_template('show_prestamo.html', prestamos=prestamo.list, user_rol=session['user_rol'])

@app.route('/showPrestamo', endpoint='showPrestamo', methods=['GET'])
@login_required
def showPrestamo():
    dataPrestamo = db.getAllPrestamo()
    prestamo = PrestamoDataViewList(dataPrestamo)
    return render_template('show_prestamo.html', prestamos=prestamo.list, user_rol=session['user_rol'])






# -----------  REGISTER PRESTAMO  -----------
@app.route('/formPrestamo/<int:id>', methods=['POST', 'GET'])
@login_required
def formPrestamo(id):
    # ---- DATE NOW ----
    now = datetime.now()
    dateNow = now

    # ---- DATE DEVOLUTION ----
    today_date = datetime.now()
    td = timedelta(days=7)
    a = (today_date + td)
    dateDevolution = a

    socios = db.getAllMember()
    bibliotecaria = db.getLibrarian(session['_user_id'])
    book = db.getBook(id)
    estado = 'Activo'

    if request.method == 'POST':
        prestamo = Prestamo(idsocio=request.form.get('socio'), idbliotecaria=session['_user_id'],
                            idlibro=book[0], fechainicio=dateNow, fechadevolucion=dateDevolution)
        db.insertPrestamo(prestamo)
        db.bookActive(id)
        flash(' Préstamo registrado.', 'exitoFormPrestamo')
        return redirect(url_for('exploreBooksLibrarian'))
    else:
        return render_template("formPrestamo.html", members=socios, bibliotecaria=bibliotecaria, book=book,
                               dateNow=dateNow, dateDevolution=dateDevolution, estado=estado)


# -----------  DELEETE PRESTAMO  -----------
@app.route('/deletePrestamo/<int:id>', endpoint='destroyPrestamo')
@login_required
@authorization_required(level=session, level_required=LEVEL_2, error=access_not_authorized)
def destroyPrestamo(id):
    db.deletePrestamo(id)
    flash('  Préstamo eliminado.', 'exito')
    return redirect('/showPrestamo')




# -----------------------------------------  DEVOLUTION  -----------------------------------------
# -----------  SHOW DEVOLUTION  -----------
@app.route('/showDevolution')
@login_required
def showDevolution():
    dataDevoluciones = db.getAllDevolucion()
    return render_template('show_devolution.html', devolutions=dataDevoluciones)


# -----------  REGISTER DEVOLUTION  -----------
@app.route('/formDevolution/<prestamo_id>/<libro_id>', methods=['POST'])
@login_required
def formDevolution(prestamo_id, libro_id):
    # ---- DATE NOW ----
    now = datetime.now()
    dateNow = now

    # bibliotecaria = db.getLibrarian(session['_user_id'])
    # book = db.getBook(libro_id)

    devolucion = Devolucion(id, fechaentrega=dateNow, idprestamo=prestamo_id)

    db.bookDevuelto(libro_id)
    db.insertDevolucion(devolucion)
    flash(' Devolución registrada.', 'devolutionExito')
    return redirect(url_for('showPrestamo'))




app.run(host = '0.0.0.0', port=5001, debug=True)
    