from config.database import db

class Curso(db.Model):
    __tablename__ = 'curso'
    id_curso = db.Column(db.Integer, primary_key=True)
    nombre_curso = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    nivel = db.Column(db.String(50))
    categoria = db.Column(db.String(50))

    # Relación inversa (opcional, pero recomendada)
    usuarios = db.relationship('Usuario', backref='curso', lazy=True)