from flask import Flask
from config.config import Config
from config.database import db
from flask_bcrypt import Bcrypt

# Inicializamos herramientas fuera para evitar errores circulares
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Conectamos la DB y Bcrypt a la app
    db.init_app(app)
    bcrypt.init_app(app)

    # REGISTRO DE RUTAS
    from app.controllers.usuario_controller import usuario_bp
    app.register_blueprint(usuario_bp)

    return app