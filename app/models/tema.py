from config.database import db

class Tema(db.Model):
    __tablename__ = 'tema'
    id_tema = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_curso = db.Column(db.Integer, db.ForeignKey('curso.id_curso'), nullable=False)
    nombre_tema = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    nivel_dificultad = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f'<Tema {self.nombre_tema}>'