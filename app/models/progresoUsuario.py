from config.database import db 
from datetime import datetime

class ProgresoUsuario(db.Model):
    __tablename__ = 'progreso_usuario'
    
    id = db.Column(db.Integer, primary_key=True)
    
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False) 
    id_tema = db.Column(db.Integer, nullable=False)
    ejercicios_realizados = db.Column(db.Integer, default=0)
    aciertos = db.Column(db.Integer, default=0)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    dificultad_alcanzada = db.Column(db.String(20))
    tiempo_segundos = db.Column(db.Integer, default=0) # Para el "Tiempo dedicado"
    tipo_error_comun = db.Column(db.String(50))      # Para la "Detección de errores"

    def __init__(self, usuario_id, id_tema, ejercicios_realizados, aciertos, dificultad_alcanzada):
        self.usuario_id = usuario_id
        self.id_tema = id_tema
        self.ejercicios_realizados = ejercicios_realizados
        self.aciertos = aciertos
        self.dificultad_alcanzada = dificultad_alcanzada