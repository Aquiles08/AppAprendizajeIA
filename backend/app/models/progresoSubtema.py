from config.database import db

class ProgresoSubtema(db.Model):
    __tablename__ = 'progreso_subtema'
    id_subtema_prog = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_progreso_tema = db.Column(db.Integer, db.ForeignKey('progreso_tema.id_progreso'), nullable=False)
    nombre_subtema = db.Column(db.String(100), nullable=False)
    completado = db.Column(db.Boolean, default=False)
    fecha_completado = db.Column(db.DateTime)

    # Relación para subir al tema padre fácilmente
    tema_padre = db.relationship('ProgresoTema', backref=db.backref('subtemas_progreso', lazy=True))