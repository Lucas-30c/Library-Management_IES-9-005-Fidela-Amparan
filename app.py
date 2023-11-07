from flask import Flask, request, redirect, url_for, render_template, flash, session
from flask_login import LoginManager, login_user, login_required, logout_user
from flask_mail import Mail, Message
from Model.Libro import Libro
from Model.PrestamoDataView import PrestamoDataViewList
from Model.Socio import Socio
from Model.Prestamo import Prestamo
from Model.Bibliotecaria import Bibliotecaria
from Model.Devolucion import Devolucion
from Model.ServiceRating import ServiceRating
from Utils.codeGenerator import generate_confirmation_code
from Utils.str_functions import build_list
from db.DataBaseBiblioteca import BooksDataBase
from datetime import timedelta, datetime
import pytz
from werkzeug.security import generate_password_hash, check_password_hash
from Utils.filterBook import FilterBook
from Utils.authorization import authorization_required, LEVEL_3, LEVEL_2, LEVEL_1, LEVEL_0


app = Flask(__name__)
app.secret_key = 'key_ñ_ProjecT_ñ_BiBLi0Te_CA'


# -----------  CONFING FLASK-MAIL  -----------
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'bibliotecadusselnotificaciones@gmail.com'
app.config['MAIL_PASSWORD'] = 'lscb tylx kztz omck'
app.config['MAIL_DEFAULT_SENDER'] = 'bibliotecadusselnotificaciones@gmail.com'
mail = Mail(app)

db = BooksDataBase()
login_manager = LoginManager()
login_manager.init_app(app)


# -----------  ROUTE NOT AUTHORIZED  -----------
@app.route('/not_authorized')
def access_not_authorized():
    usuario = session['_user_id']
    logout_user()
    session.clear()
    flash(' Sesión cerrada.', 'warning')
    return render_template("not_authorized.html", user_id=usuario)


# -----------  USERS  -----------
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
    session.clear()
    # year copyright
    now = datetime.now()
    yearNow = now.strftime('%Y')
    return render_template('home.html', yearNow=yearNow)


# -----------  HOME USER  -----------
@app.route('/InicioUser')
@login_required
def inicioUser():
    # year copyright
    now = datetime.now()
    yearNow = now.strftime('%Y')
    return render_template("homeUser.html", yearNow=yearNow)


# -----------  HOME LIBRARIAN  -----------
@app.route('/InicioLibrarian', endpoint='homeLibrarian')
@login_required
def homeLibrarian():
    # year copyright
    now = datetime.now()
    yearNow = now.strftime('%Y')
    return render_template("homeLibrarian.html", yearNow=yearNow, user_rol=session['user_rol'])


# -----------  DECORADOR NOT AUTHORIZED FLASK-LOGIN -- REDIRECT LOGIN  -----------
@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('login'))


# -----------  LOGIN  -----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        session.clear()

        if email and password: # Verificar si email and password estan vaciós
            librarian = db.getLibrarian(email)
            if librarian and check_password_hash(librarian.password, password):
                if librarian.cuenta == "ACTIVA":
                    login_user(librarian)
                    session["user_rol"] = librarian.rol
                    return redirect(url_for('homeLibrarian'))
                else:
                    flash(' Cuenta suspendida!', 'error')
                    return redirect(url_for('login'))

            socio = db.getSocio(email)
            if socio and check_password_hash(socio.password, password):
                login_user(socio)
                session["user_rol"] = 'socio'
                return redirect(url_for('inicioUser'))

            flash('Email/Contraseña inválida.', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')


# -----------  LOG OUT  -----------
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    session.clear()
    flash(' Sesión cerrada.', 'warning')
    return redirect(url_for('login'))


# -----------  FORGOT PASSWORD  -----------
@app.route('/forgotPassword', methods=['GET', 'POST'])
def forgotPassword():
    if request.method == 'POST':
        email = request.form['email']

        librarian = db.getLibrarian(email)
        socio = db.getSocio(email)

        if librarian or socio:
            confirmation_code = generate_confirmation_code()

            session['reset_email'] = email
            session['confirmation_code'] = confirmation_code
            session['timestamp'] = datetime.now(pytz.UTC)

            msg = Message('Confirmación de Restablecimiento de Contraseña',
                          sender='bibliotecadusselnotificaciones@gmail.com', recipients=[email])
            msg.body = f'Tu código de confirmación es: {confirmation_code}'
            mail.send(msg)
            return redirect(url_for('confirmationCode'))

        else:
            flash('El correo ingresado no existe en nuestros registros.', 'error')
            return redirect(url_for('forgotPassword'))

    return render_template('forgotPassword.html')


# -----------  CONFIRMATION CODE  -----------
@app.route('/confirmationCode', methods=['GET', 'POST'])
def confirmationCode():
    stored_confirmation_code = session.get('confirmation_code')
    timestamp = session.get('timestamp')
    
    if stored_confirmation_code is None:
        session.clear()
        flash('Acceso no autorizado.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        code_part1 = request.form['code_part1']
        code_part2 = request.form['code_part2']
        code_part3 = request.form['code_part3']
        code_part4 = request.form['code_part4']
        code_part5 = request.form['code_part5']
        user_confirmation_code = code_part1 + code_part2 + code_part3 + code_part4 + code_part5

        if 'failed_attempts' not in session:
            session['failed_attempts'] = 0

        if session['failed_attempts'] >= 3:
            session.clear()
            flash('Acceso no autorizado.', 'error')
            return redirect(url_for('login'))

        current_time = datetime.now(pytz.UTC)
        time_difference = current_time - timestamp

        if time_difference.total_seconds() > 900:
            session.clear()
            flash('Código de confirmación caducado.', 'error')
            return redirect(url_for('login'))
        elif user_confirmation_code == stored_confirmation_code:
            session['reset_password'] = True
            session['failed_attempts'] = 0
            return redirect(url_for('setNewPassword'))
        else:
            session['failed_attempts'] += 1
            flash('Código de confirmación incorrecto. Intenta nuevamente!', 'error')
    return render_template('confirmationCode.html')


# -----------  SET NEW PASSWORD  -----------
@app.route('/setNewPassword', methods=['GET', 'POST'])
def setNewPassword():
    stored_confirmation_code = session.get('confirmation_code')
    stored_reset_password = session.get('reset_password')
    stored_reset_email = session.get('reset_email')

    if stored_confirmation_code is None or stored_reset_password is None or stored_reset_password is False:
        session.clear()
        flash('Acceso no autorizado.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        new_password = request.form['new_password']
        new_password = generate_password_hash(new_password)

        librarian = db.getLibrarian(stored_reset_email)
        member = db.getSocio(stored_reset_email)
       
        if librarian:
            librarianAccount = db.getLibrarian(stored_reset_email)
            if librarianAccount:
                email = librarianAccount.email
                nombre = librarianAccount.nombre
                apellido = librarianAccount.apellido
                celular = librarianAccount.celular
                rol = librarianAccount.rol
                cuenta = librarianAccount.cuenta
                
                newPasswordLibrarian = Bibliotecaria(email, nombre, apellido, new_password, celular, rol, cuenta)
                db.updateLibrarian(newPasswordLibrarian)

        elif member:
            memberAccount = db.getSocio(stored_reset_email)
            if memberAccount:
                id = memberAccount.id
                dni = memberAccount.nombre
                apellido = memberAccount.apellido
                nombre = memberAccount.nombre
                email = memberAccount.email
                celular = memberAccount.celular
                direccion = memberAccount.direccion
                documentacion = memberAccount.documentacion
                responsable = memberAccount.responsable
                
                newPasswordMember = Socio(id, dni, apellido, nombre, email, new_password, celular, direccion, documentacion, responsable)
                db.updateMember(newPasswordMember)

        else:
            session.clear()
            flash('Algo salió mal.', 'error')
            return redirect(url_for('login'))

        session.pop('reset_password', None)
        session.pop('reset_email', None)
        session.pop('timestamp', None)
        session.pop('confirmation_code', None)
        session.clear()
        flash('Contraseña restablecida.', 'success')
        return redirect(url_for('login'))

    return render_template('setNewPassword.html')


# -----------  SELECTION AGE  -----------
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


# --------  REGISTER LIBRARIAN  ---------
@app.route('/registerLibrarianBIBLIOTECA', methods=['POST', 'GET'], endpoint='saveFormLibrarian',)
@login_required
@authorization_required(level=session, level_required=LEVEL_3, error=access_not_authorized)
def saveFormLibrarian():
    if request.method == 'POST':
        password = request.form['password']

        _hashed_password = generate_password_hash(password)
        cuenta = 'ACTIVA'

        librarian = Bibliotecaria(email=request.form.get("email"), nombre=request.form.get("Nombre"),
                                  apellido=request.form.get("Apellido"), password=_hashed_password,
                                  celular=request.form.get("Celular"), rol=request.form.get("Rol"), cuenta=cuenta)

        db.insertLibrarian(librarian=librarian)
        flash(' Bibliotecaria cargada.', 'succesAccount')
        return redirect(url_for('showLibrarian'))
    return render_template("registerLibrarian.html", user_rol=session['user_rol'])


# -----------  EXPLORAR LIBROS PUBLIC -----------
@app.route('/exploreBooksPublic')
def exploreBooks():
    return render_template("exploreBooksPublic.html")


# -----------  SEARCH BOOKS PUBLIC  -----------
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


# -----------  SEARCH BOOK LIBRARIAN  -----------
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


# -----------  ABOUT ON PUBLIC  -----------
@app.route('/aboutOnPublic')
def goAboutOnPublic():
    return render_template("aboutOnPublic.html")


# -----------  ABOUT ON LIBRARIAN  -----------
@app.route('/aboutOnLibrarian', endpoint='goAboutOnLibrarian')
@login_required
def goAboutOnLibrarian():
    return render_template("aboutOnLibrarian.html", user_rol=session['user_rol'])



# --------- FUNCTIONS LIBRARYAN ---------
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
@authorization_required(level=session, level_required=LEVEL_3, error=access_not_authorized)
def destroyMember(id):
    if request.method == 'GET':
        db.deleteMember(id)
        flash(' Socio eliminado.', 'memberDelete')
    return redirect('/showMembers')


# -----------------------------------------  PRESTAMO  -----------------------------------------
# -----------  SHOW PRESTAMO  -----------
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
    copiasBook = book[9]
    print("copias-----", copiasBook)
    estadoBook = book[11]
    estado = 'Activo'

    if request.method == 'POST':
        socio_id = int(request.form.get('socio'))
        socio = db.getMember(socio_id)
        documentacion_estado = socio[8]

        if documentacion_estado == 'ENTREGADA' and copiasBook > 0:
            copiasBook -= 1
            # Actualizamos el estado del libro según la disponibilidad
            estadoBook = 'Disponible' if copiasBook > 0 else 'Prestado'
            db.updateBookAvailability(id=book[0], copias=copiasBook, estado=estadoBook)
            prestamo = Prestamo(idsocio=socio_id, idbliotecaria=session['_user_id'],
                            idlibro=book[0], fechainicio=dateNow, fechadevolucion=dateDevolution)
            db.insertPrestamo(prestamo)
            flash(' Préstamo registrado.', 'exitoFormPrestamo')
            return redirect(url_for('exploreBooksLibrarian'))
        elif documentacion_estado != 'ENTREGADA':
            flash(' Socio sin la documentación entregada.', 'errorFormPrestamo')
        else:
            flash(' No hay copias disponibles para el libro.', 'errorCopiesBook')

        return redirect(url_for('formPrestamo', id=id))
    else:
        return render_template("formPrestamo.html", members=socios, bibliotecaria=bibliotecaria, book=book,
                            dateNow=dateNow, dateDevolution=dateDevolution, estado=estado)


# -----------------------------------------  DEVOLUTION  -----------------------------------------
# -----------  SHOW DEVOLUTION  -----------
@app.route('/showDevolution', endpoint='showDevolution')
@login_required
def showDevolution():
    dataDevoluciones = db.getAllDevolucion()
    return render_template('show_devolution.html', devolutions=dataDevoluciones, user_rol=session['user_rol'])


# -----------  REGISTER DEVOLUTION  -----------
@app.route('/formDevolution/<prestamo_id>/<libro_id>', methods=['POST'])
@login_required
def formDevolution(prestamo_id, libro_id):
    # ---- DATE NOW ----
    now = datetime.now()
    dateNow = now

    devolucion = Devolucion(id, fechaentrega=dateNow, idprestamo=prestamo_id)

    libro = db.getBook(libro_id)
    copiasBook = libro[9]
    copiasBook += 1

    db.updateBookAvailability(libro_id, copiasBook, estado='Disponible')
    db.bookDevuelto(libro_id)
    db.insertDevolucion(devolucion)
    flash(' Devolución registrada.', 'devolutionExito')
    return redirect(url_for('showPrestamo'))


# -----------------------------------------  LIBRARIAN  -----------------------------------------
# -----------  SHOW LIBRARIAN  -----------
@app.route('/showLibrarian', endpoint='showLibrarian')
@login_required
def showLibrarian():
    dataLibrarian = db.getAllLibrarian()
    return render_template('show_librarian.html', librarians=dataLibrarian, user_rol=session['user_rol'])


# -----------  UPDATE LIBRARIAN  -----------
@app.route('/updateLibrarian/<email>', methods=['GET', 'POST'], endpoint='updateLibrarian')
@login_required
@authorization_required(level=session, level_required=LEVEL_2, error=access_not_authorized)
def updateLibrarian(email):
    if request.method == 'GET':
        librarian = db.getLibrarianByEmail(email)
        return render_template("updateLibrarian.html", librarian=librarian)

    if request.method == 'POST':

        nombre = request.form['nombre']
        apellido = request.form['apellido']
        celular = request.form['celular']
        cuenta = request.form['cuenta']

        librarian = db.getLibrarianByEmail(email)
        password = librarian[3]
        rol = librarian[5]

        newLibrarian = Bibliotecaria(
            email, nombre, apellido, password, celular, rol, cuenta)
        db.updateLibrarian(newLibrarian)
        flash('Bibliotecaria actualizada.', 'librarianEdit')
        return redirect(url_for('showLibrarian'))

    return redirect(url_for('showLibrarian'))


# -----------  SUSPEND ACCOUNT LIBRARIAN  -----------
@app.route('/suspendLibrarian/<email>', methods=['POST'])
def suspendLibrarian(email):
    db.suspendLibrarian(email)
    flash('Cuenta suspendida!', 'suspendAccount')
    return redirect(url_for('showLibrarian'))


# -----------  RECOVER ACCOUNT LIBRARIAN  -----------
@app.route('/recoverLibrarian/<email>', methods=['POST'])
def recoverLibrarian(email):
    db.recoverLibrarian(email)
    flash('Cuenta recuperada !', 'succesAccount')
    return redirect(url_for('showLibrarian'))


# -----------  EMAIL - SERVICE RATING  -----------
@app.route('/emailServiceRating', methods=['POST'])
def emailServiceRating():
    if request.method == 'POST':
        emailServiceRating = request.form.get('emailServiceRating')
        socio = db.getSocio(emailServiceRating)

        if socio and socio.documentacion == "ENTREGADA":
            # Almacenar email user
            session['emailServiceRating'] = emailServiceRating
            return redirect('/serviceRating')
        else:
            user_rol = session.get('user_rol')
            if user_rol == 'socio':
                return redirect('/InicioUser')
    return redirect('/')

    
# ----------- PAGE SERVICE RATING  -----------
@app.route('/serviceRating')
def serviceRating():
    emailServiceRating = session.get('emailServiceRating')

    if emailServiceRating is None or emailServiceRating.strip() == "":
        user_rol = session.get('user_rol')

        if user_rol == 'socio':
            return redirect('/InicioUser')
        return redirect('/')

    user_rol = session.get('user_rol')
    if user_rol == 'socio':
        # Botón volver para socio
        return render_template('serviceRating.html', user_rol=user_rol)
    else:
        # Botón volver para invitado
        user_rol = 'invitado'
        return render_template('serviceRating.html', user_rol=user_rol)
    

# -----------  SEND SERVICE RATING  -----------
@app.route('/sendServiceRating', methods=['POST'])
def sendServiceRating():
    if request.method == 'POST':
        emailServiceRating = session.get('emailServiceRating')
        serviceRating = ServiceRating(member=emailServiceRating, star=request.form.get("number_stars"), comment=request.form.get("comment"))
        db.insertServiceRating(serviceRating=serviceRating)
   
    user_rol = session.get('user_rol')
    if user_rol == 'socio':
        flash(' Comentario enviado !', 'succesServiceRating')
        return redirect('/InicioUser')
    return redirect('/')
    

# -----------  SHOW SERVICE RATING  -----------
@app.route('/showServiceRating', endpoint='showServiceRating')
@login_required
@authorization_required(level=session, level_required=LEVEL_3, error=access_not_authorized)
def showServiceRating():
    dataServiceRating = db.getAllServiceRating()
    return render_template('show_ServiceRating.html', serviceRatings=dataServiceRating, user_rol=session['user_rol'])


# -----------  TEMPLATE MENU - SERVICE AND LIBRARIAN  -----------
@app.route('/managmentMenu', endpoint='managmentMenu')
@login_required
@authorization_required(level=session, level_required=LEVEL_3, error=access_not_authorized)
def managmentMenu():
    return render_template('managmentMenu.html', user_rol=session['user_rol'])
    



app.run(host='0.0.0.0', port=5002, debug=True)
