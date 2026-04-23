from config.database import db
from datetime import datetime

class Respuesta(db.Model):
    __tablename__ = 'respuesta'
    id_respuesta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_evaluacion = db.Column(db.Integer, db.ForeignKey('evaluacion.id_evaluacion'), nullable=False)
    pregunta = db.Column(db.Text, nullable=True)
    respuesta_usuario = db.Column(db.Text, nullable=True)
    respuesta_correcta = db.Column(db.Text, nullable=True)
    resultado = db.Column(db.Boolean, nullable=True)
    metadatos_ia = db.Column(db.JSON, nullable=True)

    def __repr__(self):
        return f'<Respuesta {self.id_respuesta}>'