from config.database import db

class Respuesta(db.Model):
    __tablename__ = 'respuesta' # El nombre que tienes en MySQL
    id_respuesta = db.Column(db.Integer, primary_key=True)
    id_evaluacion = db.Column(db.Integer)
    pregunta = db.Column(db.Text)
    respuesta_usuario = db.Column(db.Text)
    respuesta_correcta = db.Column(db.Text)
    resultado = db.Column(db.Integer) # tinyint(1) se maneja como Integer o Boolean en SQLAlchemy