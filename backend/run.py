from app import create_app

app = create_app()

if __name__ == "__main__":
    # El debug=True es vital para que veas los errores en consola mientras programas
    app.run(host='0.0.0.0',debug=True, port=5000)