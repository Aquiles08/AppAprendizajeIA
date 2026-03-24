from config.database import db

class Usuario(db.Model):
    __tablename__ = 'usuarios' # Nombre de la tabla en MySQL
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), default='estudiante') # estudiante, docente, admin

    def __repr__(self):
        return f'<Usuario {self.nombre}>'