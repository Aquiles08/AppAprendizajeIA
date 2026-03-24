from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    # Reemplaza con tus datos reales de MySQL
    # Formato: mysql+mysqlconnector://USUARIO:CONTRASEÑA@LOCALHOST/NOMBRE_DB
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:password@localhost/aprendizaje_ia_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)