from flask import Flask
from config.database import db, init_db

app = Flask(__name__)

# Inicializar la base de datos
init_db(app)

@app.route('/')
def hola():
    return "Servidor Backend de Aprendizaje IA funcionando"

if __name__ == '__main__':
    # Esto crea las tablas en MySQL automáticamente si no existen
    with app.app_context():
        db.create_all() 
    app.run(debug=True)