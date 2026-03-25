from flask import Blueprint, render_template, request, redirect, url_for
from app.models.usuario import Usuario
from app.utils import bcrypt # <--- AHORA VIENE DE UTILS

usuario_bp = Blueprint('usuario', __name__)

@usuario_bp.route("/")
def login():
    return render_template("login.html")

@usuario_bp.route("/entrar", methods=["POST"])
def entrar():
    correo = request.form["correo"]
    password = request.form["password"]

    user = Usuario.query.filter_by(correo=correo).first()

    if user and bcrypt.check_password_hash(user.password, password):
        return redirect(url_for('usuario.dashboard'))
    else:
        return "Datos incorrectos o usuario no registrado"

@usuario_bp.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")