import os
from flask import Flask, flash, redirect, request, render_template, send_file, session, url_for
import sqlite3
from datetime import datetime

import traceback
import sys
from flask_login import LoginManager, login_user

import json
from user import User
from admitido import Admitido

app = Flask(__name__, static_folder='static', template_folder='templates')

app.config['SECRET_KEY'] = 'your_secret_key'
UPLOAD_FOLDER = 'static/titulos'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
UPLOAD_FOLDER2 = 'static/fotos'
app.config['UPLOAD_FOLDER2'] = UPLOAD_FOLDER2

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Load user data from users.json
with open('static/users.json', 'r') as file:
    users_data = json.load(file)

# Create instances of the User class
users = [User(user['id'], user['username'], user['password'],user['type']) for user in users_data]

@app.route("/")
def entry_home():
    return render_template('home.html')

@app.route("/formulario", endpoint='formulario')
def entry_form():
    if 'username' in session:
        persona_validar = Admitido("","","","","","","","","","","","","")
        # User is logged in, you can render the page or redirect as needed
        return render_template('form.html',persona_validar=persona_validar)
    else:
        # User is not logged in, redirect to the login page
        return redirect(url_for('login'))
        
    

@app.route("/intro", methods=['POST'])
def intro_form():
    #definimos la variable que dará redirección
    errorForm = []
    
    # VALIDAR LA INFO RECIBIDA
    nombre = request.form["nombre"]
    apellidos = request.form["apellidos"]
    dni = request.form["dni"]
    cp = request.form["cp"]
    nacimiento = request.form["nacimiento"]
    telefono = request.form["telefono"]
    email = request.form["email"]
    gender = request.form.get("gender")
    servicio_activo = request.form["servicio_activo"]
    grado = request.form["grado"]
    equivalencia = request.form["equivalencia"]
    
    categoria = request.form["categoria"]
    # Guardamos la persona para, en caso de error, volver a recuperar sus datos en el formulario
    persona_validar=Admitido(nombre,apellidos,dni,gender,cp,nacimiento,telefono,email,10,servicio_activo,grado,categoria,equivalencia)
    
    #PRIMERA VALIDACIÓN, QUE NO ESTÉ REPETIDO EL CP
    try:
        with sqlite3.connect("/Users/carlosvillarino/Desktop/Rufo/new-repository/data/admision.db") as con:
            cur = con.cursor()
            query = "SELECT nombre FROM admision_2023 where CP="+cp
            cur.execute(query)
            cp_BD = cur.fetchall()
            print(cp_BD)
            if len(cp_BD)!=0:
                errorForm.append("La persona que está intentando dar de alta ya está registrada")
                for item in errorForm:
                    flash(item)
                return render_template("form.html",persona_validar=persona_validar)
    except Exception as e:
        print(e)
        return "Error al intentar validar el CP"
    
    # TODO validar variables
    # edad < 60
    try:
        limit = datetime.now()
        n = datetime.strptime(nacimiento, "%Y-%m-%d")
        edad = limit.year - n.year
        if edad > 60:
            errorForm.append("DEMASIADO MAYOR")
        if edad == 60:
            if limit.month < n.month:
                errorForm.append("DEMASIADO MAYOR")
            elif limit.month == n.month and limit.day >= n.day:
                errorForm.append("DEMASIADO MAYOR")
        
    except:
        errorForm.append("La fecha de nacimiento no se ha recibido con el formato esperado. Consulte con la administración")

    # categoria == oficial
    if categoria != "oficial":
        errorForm.append("Necesita ser oficial para poder acceder")

    # Elegir Género
    if gender not in ['Hombre', 'Mujer']:
        error = 'Invalid gender'
        errorForm.append("Tiene que seleccionar un género")

    # Equivalencia
    if equivalencia != "si":
         errorForm.append("Necesita tener una equivalencia para poder matricularse.")
    
    # grado  == no
    if grado != "no":
        errorForm.append("Si ya tiene un grado no puede matricularse.")

    # servicio activo != otro
    if servicio_activo == "otro":
       errorForm.append("Su situación administrativa no es válida")

    # titulo
    if 'titulo' not in request.files:
        errorForm.append('Se ha producido un problema con la subida de ficheros, contacte con el administrador. Disculpe las molestias.')

    titulo = request.files['titulo']

    if titulo.filename == '':
        errorForm.append('No se ha adjuntado documento de título')
    
    
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    titulo.save(os.path.join(app.config['UPLOAD_FOLDER'], cp+"_"+titulo.filename))

    # fotografia
    if 'fotografia' not in request.files:
        errorForm.append('Se ha producido un problema con la subida de ficheros, contacte con el administrador. Disculpe las molestias.')

    foto = request.files['fotografia']

    if foto.filename == '':
        errorForm.append('No se ha adjuntado fotografía')
    
    
    if not os.path.exists(app.config['UPLOAD_FOLDER2']):
        os.makedirs(app.config['UPLOAD_FOLDER2'])

    foto.save(os.path.join(app.config['UPLOAD_FOLDER2'], cp+"_"+foto.filename))
    
    # REPORTAR OK
    if not errorForm:
         # ESCRIBIRLO EN LA BD
        try:
            with sqlite3.connect("/Users/carlosvillarino/Desktop/Rufo/new-repository/data/admision.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO admision_2023 (nombre,apellidos,DNI,CP,fecha_nacimiento,telefono,email,escalafon,situacion_servicio,grado,categoria_profesional,equivalencia_titulo,gender) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",(nombre,apellidos,dni,cp,nacimiento,telefono,email,10,servicio_activo,grado,categoria,equivalencia,gender) )
                con.commit()
        except Exception as e:
            print(e)
            con.rollback()
            errorForm.append("Error del servidor, pruebe más tarde.")
        
        return render_template("formExito.html")
    else:
        for item in errorForm:
            flash(item)
        return render_template("form.html",persona_validar=persona_validar)

@app.route("/consulta", endpoint='consulta')
def dump_db():
    if 'username' in session:
        try:
            with sqlite3.connect("/Users/carlosvillarino/Desktop/Rufo/new-repository/data/admision.db") as con:
                cur = con.cursor()
                
                cur.execute("SELECT * FROM admision_2023 ORDER BY escalafon DESC;")
                result = cur.fetchall()


                print(result)
                return render_template("datos.html", result=result)
            
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            # or
            print(sys.exc_info()[2])
            print("except")
            return "Error1"
    else:
        return redirect(url_for('login'))
    
def get_user_by_id(user_id):
    for user in users:
        if user.id == user_id:
            return user
    return None
    
@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    session.clear()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Find the user in the list
        user = next((u for u in users if u.username == username), None)

        if user and user.check_password(password):
            # Log in the user
            login_user(user)
            session['username'] = username
            if(user.type=='user'):
                return redirect(url_for('formulario'))
            else:
                return redirect(url_for('consulta'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
            return render_template('login.html')
    else:
        return render_template('login.html')
    
@app.route('/logout')
def logout():
    return render_template('logout.html')

@app.route('/confirmLogout')
def confirmLogout():
    session.pop('username', None)
    return render_template('home.html')

@app.route('/detalles/<int:item_CP>', endpoint='detalles')
def detalles(item_CP):
    if 'username' in session:
        try:
            with sqlite3.connect("/Users/carlosvillarino/Desktop/Rufo/new-repository/data/admision.db") as con:
                cur = con.cursor()
                query = "SELECT nombre, apellidos, DNI, gender, CP, fecha_nacimiento, telefono, email, escalafon, situacion_servicio, grado, categoria_profesional, equivalencia_titulo FROM admision_2023 where CP="+str(item_CP)
                cur.execute(query)
                result = cur.fetchall()
                
                search_string = str(item_CP)
                image_search = find_matching_files_foto(search_string)
                titulo_search = find_matching_files_titulo(search_string)
                for item in image_search:
                    image_name = item
                for item in titulo_search:
                    titulo_name = item
                print(image_name)
                print(result)
                for row in result:
                    admitido = Admitido(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12])
            return render_template('detalle.html',admitido=admitido,image_name=image_name,titulo_name=titulo_name)
        except Exception as e:
            print(e)
            return "Error1"
    else:
        return render_template('login.html')
    
def find_matching_files_foto(search_string):
    matching_files = []

    # Get the current directory of the Flask app
    app_root = os.path.dirname(os.path.abspath(__file__))
    
    # Define the path to the static/images directory
    images_path = os.path.join(app_root, 'static', 'fotos')

    # Check if the path exists
    if os.path.exists(images_path):
        # Iterate through files in the static/images directory
        for root, dirs, files in os.walk(images_path):
            for file in files:
                if search_string in file:
                    # Add the file name to the list if it contains the search string
                    matching_files.append(file)
    else:
        print(f"The path {images_path} does not exist.")

    return matching_files
def find_matching_files_titulo(search_string):
    matching_files = []

    # Get the current directory of the Flask app
    app_root = os.path.dirname(os.path.abspath(__file__))
    
    # Define the path to the static/images directory
    images_path = os.path.join(app_root, 'static', 'titulos')

    # Check if the path exists
    if os.path.exists(images_path):
        # Iterate through files in the static/images directory
        for root, dirs, files in os.walk(images_path):
            for file in files:
                if search_string in file:
                    # Add the file name to the list if it contains the search string
                    matching_files.append(file)
    else:
        print(f"The path {images_path} does not exist.")

    return matching_files

@app.route('/download_file', methods=['POST'])
def download_file():
    dynamic_filename = request.form.get('dynamic_filename')

    # Assuming the file is located in the static folder
    file_path = os.path.join(app.root_path, 'static', 'titulos', dynamic_filename)
    
    # Check if the file exists
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return render_template('file_not_found.html', filename=dynamic_filename)

@app.route('/detalles/modEscalafon', methods=['POST'])
def modifEsc():
    try:
        escalafon = request.form.get("escalafon")
        cp = request.form.get("cp_mod")
        print(request.form)
        print(escalafon)
        print(cp)
        with sqlite3.connect("/Users/carlosvillarino/Desktop/Rufo/new-repository/data/admision.db") as con:
            cur = con.cursor()
            query = "UPDATE admision_2023 SET escalafon = ? WHERE CP = ?"
            cur.execute(query, (escalafon, cp))
            con.commit()
            
    except Exception as e:
        print(e)
        
    return render_template("formExito.html")
        
    