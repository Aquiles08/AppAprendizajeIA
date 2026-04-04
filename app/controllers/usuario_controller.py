from flask import Blueprint, render_template, request, redirect, url_for, session
from app.models.usuario import Usuario
from app.utils import bcrypt 
from config.database import db 

usuario_bp = Blueprint('usuario', __name__)

# --- LOGIN (GET para ver, POST para entrar) ---
@usuario_bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = request.form.get("correo")
        password_candidata = request.form.get("contrasena")
        
        user = Usuario.query.filter_by(correo=correo).first()
        
        if user and bcrypt.check_password_hash(user.contrasena, password_candidata):
            session['usuario_id'] = user.id_usuario
            session['usuario_nombre'] = user.nombre
            return redirect(url_for('usuario.dashboard'))
        else:
            return "Datos incorrectos o usuario no registrado"
            
    return render_template("login.html")

# --- DASHBOARD ---
@usuario_bp.route("/dashboard")
def dashboard():
    if 'usuario_id' not in session:
        return redirect(url_for('usuario.login'))
    return render_template("dashboard.html")

# --- REGISTRAR ---
@usuario_bp.route("/registrar")
def registro():
    return render_template("registro.html")

# --- CREAR CUENTA ---
@usuario_bp.route("/crear_cuenta", methods=["POST"])
def crear_cuenta():
    nombre = request.form.get("nombre")
    correo = request.form.get("correo")
    password = request.form.get("contrasena") 
    tipo_usuario = request.form.get("tipo_usuario")

    # --- NUEVA VALIDACIÓN ---
    # Buscamos si ya hay alguien con ese correo en la DB
    usuario_existente = Usuario.query.filter_by(correo=correo).first()
    
    if usuario_existente:
        # Si ya existe, detenemos el proceso y le avisamos al usuario
        return "Este correo ya está registrado. Por favor, intenta con otro o inicia sesión."
    # ------------------------

    # Si el correo es nuevo, continuamos normal:
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    nuevo_usuario = Usuario(
        nombre=nombre, 
        correo=correo, 
        contrasena=password_hash,
        tipo_usuario=tipo_usuario 
    )

    db.session.add(nuevo_usuario)
    db.session.commit()

    return redirect(url_for('usuario.login'))

# --- EDITAR ---
@usuario_bp.route("/usuario/editar/<int:id>", methods=["GET", "POST"])
def editar_usuario(id):
    user = Usuario.query.get_or_404(id)
    if request.method == "POST":
        user.nombre = request.form.get("nombre")
        user.correo = request.form.get("correo")
        db.session.commit()
        return redirect(url_for('usuario.dashboard'))
    return render_template("editar_perfil.html", user=user)

# --- ELIMINAR ---
@usuario_bp.route("/usuario/eliminar/<int:id>", methods=["POST"])
def eliminar_usuario(id):
    user = Usuario.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('usuario.login'))

# --- SALIR ---
@usuario_bp.route("/salir")
def salir():
    session.clear()
    return redirect(url_for('usuario.login'))

# --- RUTAS DEL DASHBOARD ---

@usuario_bp.route("/examen")
def examen():
    return render_template("examen.html") 
# --- RUTA PARA PROCESAR LAS RESPUESTAS (La que te falta) ---
@usuario_bp.route("/procesar_examen", methods=["POST"])
def procesar_examen():
    # 1. Aquí recibes lo que el usuario contestó en el formulario
    # Por ejemplo, si tienes un campo 'respuesta1':
    # r1 = request.form.get("respuesta1")
    
    # 2. Por ahora, solo mandamos un mensaje de éxito o redirigimos
    # Puedes crear una página de "gracias" o volver al dashboard
    return "¡Examen enviado con éxito! Estamos analizando tus resultados."

@usuario_bp.route("/ruta")
def ruta():
    # 1. Creamos un diccionario 'ruta' con los datos que espera el HTML
    info_ruta = {
        'nivel_actual': 'Principiante' # Esto es lo que leerá {{ ruta.nivel_actual }}
    }
    
    # 2. Creamos una lista de temas (puedes traerlos de la DB después)
    lista_temas = [
        "Introducción a Redes Neuronales",
        "Lógica Difusa",
        "Algoritmos de Búsqueda"
    ]
    
    # 3. Se los pasamos al HTML con los nombres EXACTOS que usaste allá
    return render_template("ruta.html", ruta=info_ruta, temas=lista_temas)

# --- RUTA PARA MOSTRAR LA PÁGINA DE PRÁCTICA ---
@usuario_bp.route("/practica")
def practica():
    return render_template("practica.html")

# --- RUTA PARA PROCESAR EL RESULTADO (La que soluciona el error) ---
@usuario_bp.route("/procesar_practica", methods=["POST"])
def procesar_practica():
    # 'respuesta_practica' es el name que pusiste en el input del HTML
    respuesta = request.form.get("respuesta_practica")
    
    if respuesta == "12":
        mensaje = "¡Correcto! Eres un crack de las mates."
    else:
        mensaje = f"Casi, pero {respuesta} no es la respuesta. ¡Inténtalo de nuevo!"
    
    # Por ahora solo mostramos el mensaje en pantalla
    return mensaje

@usuario_bp.route("/progreso")
def progreso():
    return render_template("progreso.html")

# --- RUTA PARA MOSTRAR EL TUTOR ---
@usuario_bp.route("/tutor")
def tutor():
    # El HTML espera una variable 'historial'. Se la pasamos vacía al inicio.
    return render_template("tutor.html", historial=None)

# --- RUTA PARA PROCESAR LA PREGUNTA (La que quita el BuildError) ---
@usuario_bp.route("/preguntar_tutor", methods=["POST"])
def preguntar_tutor():
    pregunta = request.form.get("pregunta")
    
    # Simulamos un historial para que veas cómo se ve en el HTML
    historial_simulado = [
        {"rol": "Usuario", "texto": pregunta},
        {"rol": "Tutor IA", "texto": f"Claro, sobre '{pregunta}', mi consejo es que revises las bases de cálculo..."}
    ]
    
    return render_template("tutor.html", historial=historial_simulado)

# --- FIX PARA EL LOGOUT ---
# En tu HTML dice 'usuario.logout', pero en tu Python la función se llama 'salir'
@usuario_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('usuario.login'))