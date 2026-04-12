from config.database import db # <-- CAMBIA ESTO
from datetime import datetime

class ProgresoUsuario(db.Model):
    __tablename__ = 'progreso_usuario'
    
    id = db.Column(db.Integer, primary_key=True)
    # Importante: Verifica que en usuario.py tu tabla se llame 'usuario'
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False) 
    
    tema = db.Column(db.String(100), nullable=False)
    ejercicios_realizados = db.Column(db.Integer, default=0)
    aciertos = db.Column(db.Integer, default=0)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    dificultad_alcanzada = db.Column(db.String(20))

    def __init__(self, usuario_id, tema, ejercicios_realizados, aciertos, dificultad_alcanzada):
        self.usuario_id = usuario_id
        self.tema = tema
        self.ejercicios_realizados = ejercicios_realizados
        self.aciertos = aciertos
        self.dificultad_alcanzada = dificultad_alcanzada