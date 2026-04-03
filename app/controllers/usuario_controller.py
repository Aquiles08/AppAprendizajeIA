from flask import Blueprint, render_template, request, redirect, url_for, session
from app.models.usuario import Usuario
from app.utils import bcrypt 
# Importamos db para poder hacer consultas si es necesario
from config.database import db 

usuario_bp = Blueprint('usuario', __name__)

@usuario_bp.route("/")
def login():
    return render_template("login.html")

@usuario_bp.route("/", methods=["GET", "POST"]) # <--- AGREGA ESTO
def login():
    if request.method == "POST":
        # Aquí va la lógica que ya tienes de 'entrar'
        correo = request.form.get("correo")
        password_candidata = request.form.get("contrasena")
        
        user = Usuario.query.filter_by(correo=correo).first()
        
        if user and bcrypt.check_password_hash(user.contrasena, password_candidata):
            session['usuario_id'] = user.id_usuario
            session['usuario_nombre'] = user.nombre
            return redirect(url_for('usuario.dashboard'))
        else:
            return "Datos incorrectos o usuario no registrado"
            
    # Si es GET, simplemente muestra la página
    return render_template("login.html")

# --- EDITAR (Update) ---
@usuario_bp.route("/usuario/editar/<int:id>", methods=["GET", "POST"])
def editar_usuario(id):
    user = Usuario.query.get_or_404(id)
    if request.method == "POST":
        user.nombre = request.form.get("nombre")
        user.correo = request.form.get("correo")
        db.session.commit()
        return redirect(url_for('usuario.dashboard'))
    return render_template("editar_perfil.html", user=user)

# --- ELIMINAR (Delete) ---
@usuario_bp.route("/usuario/eliminar/<int:id>", methods=["POST"])
def eliminar_usuario(id):
    user = Usuario.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('usuario.login'))

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