from config.database import db
from datetime import datetime

class HistorialTutor(db.Model):
    __tablename__ = 'historial_tutor'
    
    id = db.Column(db.Integer, primary_key=True)
   
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    es_bot = db.Column(db.Boolean, nullable=False)
    fecha = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    usuario = db.relationship('Usuario', backref=db.backref('historial', lazy=True))