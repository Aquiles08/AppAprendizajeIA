from flask import Blueprint, render_template, request, redirect, url_for, session
from app.models.usuario import Usuario
from app.utils import bcrypt 
from config.database import db 

usuario_bp = Blueprint('usuario', __name__)

# --- LOGIN (GET para ver, POST para entrar) ---
@usuario_bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = request.form.get("correo")
        password_candidata = request.form.get("contrasena")
        
        user = Usuario.query.filter_by(correo=correo).first()
        
        if user and bcrypt.check_password_hash(user.contrasena, password_candidata):
            session['usuario_id'] = user.id_usuario
            session['usuario_nombre'] = user.nombre
            return redirect(url_for('usuario.dashboard'))
        else:
            return "Datos incorrectos o usuario no registrado"
            
    return render_template("login.html")

# --- DASHBOARD ---
@usuario_bp.route("/dashboard")
def dashboard():
    if 'usuario_id' not in session:
        return redirect(url_for('usuario.login'))
    return render_template("dashboard.html")

# --- REGISTRAR ---
@usuario_bp.route("/registrar")
def registro():
    return render_template("registro.html")

# --- CREAR CUENTA ---
@usuario_bp.route("/crear_cuenta", methods=["POST"])
def crear_cuenta():
    return redirect(url_for('usuario.login'))

# --- EDITAR ---
@usuario_bp.route("/usuario/editar/<int:id>", methods=["GET", "POST"])
def editar_usuario(id):
    user = Usuario.query.get_or_404(id)
    if request.method == "POST":
        user.nombre = request.form.get("nombre")
        user.correo = request.form.get("correo")
        db.session.commit()
        return redirect(url_for('usuario.dashboard'))
    return render_template("editar_perfil.html", user=user)

# --- ELIMINAR ---
@usuario_bp.route("/usuario/eliminar/<int:id>", methods=["POST"])
def eliminar_usuario(id):
    user = Usuario.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('usuario.login'))

# --- SALIR ---
@usuario_bp.route("/salir")
def salir():
    session.clear()
    return redirect(url_for('usuario.login'))