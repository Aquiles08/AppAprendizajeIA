import os

class Config:
    # SECRET_KEY es necesaria para que las sesiones (login) funcionen
    SECRET_KEY = 'tu_llave_secreta_super_segura'
    
    # Estructura: mysql+pymysql://usuario:contraseña@servidor/nombre_base_datos
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:Admin050805@localhost/plataformaia'
    
    # Evita alertas innecesarias de SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False