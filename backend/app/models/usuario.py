from config.database import db
from datetime import datetime

class Usuario(db.Model):
    __tablename__ = 'usuario'
    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(150), unique=True, nullable=False)
    contrasena = db.Column(db.String(255), nullable=False)
    tipo_usuario = db.Column(db.Enum('Estudiante', 'Docente', 'Administrador'), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    id_curso = db.Column(db.Integer, db.ForeignKey('curso.id_curso'), nullable=True)
    nivel = db.Column(db.String(50), default="Sin realizar examen")
    tutor_mode = db.Column(db.String(20), default='paciente')
    enfoque_temas = db.Column(db.String(255), default='Algebra,Ecuaciones')
    
    def __repr__(self):
        return f'<Usuario {self.nombre}>'