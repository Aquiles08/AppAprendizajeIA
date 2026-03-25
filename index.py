from flask import Flask
from config.database import db, init_db
from app.utils import bcrypt # Importamos desde el nuevo lugar
from app.controllers.usuario_controller import usuario_bp

app = Flask(__name__, template_folder='app/views')
app.config['SECRET_KEY'] = 'mi_llave_secreta_123'

# Inicializamos todo
init_db(app)
bcrypt.init_app(app) # Lo unimos a la app aquí

# Registramos el blueprint
app.register_blueprint(usuario_bp)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)