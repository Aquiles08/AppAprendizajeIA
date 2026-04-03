from flask import Blueprint, render_template, request, redirect, url_for, session
from app.models.usuario import Usuario
from app.utils import bcrypt 
# Importamos db para poder hacer consultas si es necesario
from config.database import db 

usuario_bp = Blueprint('usuario', __name__)

@usuario_bp.route("/")
def login():
    return render_template("login.html")

@usuario_bp.route("/entrar", methods=["POST"])
def entrar():
    # 1. 'correo' coincide con el name="correo" de tu login.html
    correo = request.form.get("correo")
    # 2. 'contrasena' coincide con el name="contrasena" que ajustamos en el HTML
    password_candidata = request.form.get("contrasena")

    # Buscamos en la tabla 'usuario' de PlataformaIA.sql
    user = Usuario.query.filter_by(correo=correo).first()

    # 3. Verificamos la contraseña usando el nombre de columna del SQL: 'contrasena'
    if user and bcrypt.check_password_hash(user.contrasena, password_candidata):
        # GUARDAR EN SESIÓN: Vital para que dashboard.html diga "Bienvenido, Aquiles"
        session['usuario_id'] = user.id_usuario
        session['usuario_nombre'] = user.nombre
        return redirect(url_for('usuario.dashboard'))
    else:
        return "Datos incorrectos o usuario no registrado"

@usuario_bp.route("/dashboard")
def dashboard():
    # Verificamos que el usuario esté logueado antes de mostrar el dashboard
    if 'usuario_id' not in session:
        return redirect(url_for('usuario.login'))
    return render_template("dashboard.html")

@usuario_bp.route("/registrar")
def registro():
    return render_template("registro.html")

@usuario_bp.route("/crear_cuenta", methods=["POST"])
def crear_cuenta():
    # Aquí irá la lógica para guardar en la base de datos más adelante
    # Por ahora solo redireccionamos al login
    return redirect(url_for('usuario.login'))

@usuario_bp.route("/salir")
def salir():
    session.clear() # Borra el id y el nombre de la sesión
    return redirect(url_for('usuario.login'))