# app/__init__.py
from flask import Flask
from config.database import db, init_db # Importa ambos
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = 'una_llave_super_secreta_123'
    # En lugar de cargar Config (que puede tener datos viejos), 
    # usamos tu función de database.py
    init_db(app) 
    bcrypt.init_app(app)

    with app.app_context():
        from app.models.usuario import Usuario
        from app.models.progresoTema import ProgresoTema
        from app.models.progresoSubtema import ProgresoSubtema
        from app.models.evaluacion import Evaluacion    
        from app.models.progresoUsuario import ProgresoUsuario
        from app.models.tema import Tema
        from app.models.curso import Curso
        from app.models.respuesta import Respuesta
        from app.models.historialTutor import HistorialTutor    
        from app.controllers.usuario_controller import usuario_bp
        app.register_blueprint(usuario_bp)

    return app