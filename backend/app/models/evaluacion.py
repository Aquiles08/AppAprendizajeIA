from config.database import db

class Evaluacion(db.Model):
    __tablename__ = 'evaluacion'
    id_evaluacion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_usuario = db.Column(db.Integer, nullable=False)
    id_tema = db.Column(db.Integer, nullable=False)
    puntuacion = db.Column(db.Numeric(5, 2))
    fecha = db.Column(db.DateTime)
    tipo_evaluacion = db.Column(db.Enum('Quiz', 'Examen', 'Practica'))