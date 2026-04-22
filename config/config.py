import os
from dotenv import load_dotenv

load_dotenv()  # Carga las variables de entorno desde el archivo .env

class Config:
    # Carga la clave de la API de Gemini desde las variables de entorno
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # SECRET_KEY es necesaria para que las sesiones (login) funcionen
    SECRET_KEY = 'tu_llave_secreta_super_segura'
    
    # Estructura: mysql+pymysql://usuario:contraseña@servidor/nombre_base_datos
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:Admin050805@localhost/plataformaia'
    
    # Evita alertas innecesarias de SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    