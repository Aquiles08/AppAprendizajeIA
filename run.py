from app import create_app

app = create_app()

if __name__ == "__main__":
    # El debug=True es vital para que veas los errores en consola mientras programas
    app.run(debug=True, port=5000)