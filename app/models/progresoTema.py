from config.database import db

class ProgresoTema(db.Model):
    __tablename__ = 'progreso_tema'
    
    id_progreso = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False)
    id_tema = db.Column(db.Integer, nullable=False)
    nombre_tema = db.Column(db.String(100), nullable=False)
    
    # Recuerda que definimos estos 3 estados en el ENUM de MySQL
    estado = db.Column(db.Enum('Bloqueado', 'Disponible', 'Completado'), default='Bloqueado')
    
    puntuacion_max = db.Column(db.Numeric(5, 2), default=0.00)

    # Esto te permitirá hacer: usuario.progresos para ver todos sus temas
    usuario = db.relationship('Usuario', backref=db.backref('progresos', lazy=True))

    def __repr__(self):
        return f'<ProgresoTema {self.nombre_tema} - {self.estado}>'