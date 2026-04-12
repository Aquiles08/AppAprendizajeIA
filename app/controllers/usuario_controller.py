from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify 
from app import db # Importamos la instancia de SQLAlchemy para hacer consultas a la DB
from app.utils import bcrypt # Importamos bcrypt para verificar contraseñas

#Modelos
from app.models.usuario import Usuario # Importamos el modelo Usuario para hacer consultas a la tabla de usuarios
from app.models.curso import Curso # Importamos el modelo Curso para hacer consultas a la tabla de cursos
from app.models.respuesta import Respuesta # Importamos el modelo Respuesta para guardar las respuestas del examen
from app.models.progresoUsuario import ProgresoUsuario # Importamos el modelo ProgresoUsuario para guardar el progreso de los usuarios

#Servicios y lógica
from app.services.usuario_service import UsuarioService # Importamos el servicio de usuario para manejar la lógica de negocio relacionada con los usuarios
from app.logic.motor_ia import MotorIA # Importamos el motor de IA para tomar decisiones en la ruta de práctica
from app.logic.generador import GeneradorEjercicios # Importamos el generador de ejercicios para crear problemas matemáticos personalizados

usuario_bp = Blueprint('usuario', __name__)

# --- LOGIN --- 
@usuario_bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = request.form.get("correo")
        password_candidata = request.form.get("contrasena")
        
        user = Usuario.query.filter_by(correo=correo).first()
        
        if user and bcrypt.check_password_hash(user.contrasena, password_candidata):
            #Guardamos el ID real de la base de datos en las sesion 
            session['usuario_id'] = user.id_usuario
            session['usuario_nombre'] = user.nombre
            session['tipo_usuario'] = user.tipo_usuario
            return redirect(url_for('usuario.dashboard'))
        else:
            flash("Correo o contraseña incorrectos. Inténtalo de nuevo.")
            return redirect(url_for('usuario.login'))
            
    return render_template("login.html")

# --- REGISTRAR ---
@usuario_bp.route("/registrar")
def registro():
    return render_template("registro.html")

# --- Crear Cuenta ---
@usuario_bp.route("/crear_cuenta", methods=["POST"])
def crear_cuenta():
    nombre = request.form.get("nombre")
    correo = request.form.get("correo")
    password = request.form.get("contrasena") 
    tipo_usuario = request.form.get("tipo_usuario")

    # Validacion. Buscamos si ya hay alguien con ese correo en la DB
    usuario_existente = Usuario.query.filter_by(correo=correo).first()
    
    if usuario_existente:
        # Si ya existe, detenemos el proceso y le avisamos al usuario
        return "Este correo ya está registrado. Por favor, intenta con otro o inicia sesión."

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


# --- RUTAS DEL DASHBOARD ---

# --- Dashboard ---
@usuario_bp.route("/dashboard")
def dashboard():
    u_id = session.get('usuario_id')
    if not u_id:
        return redirect(url_for('usuario.login'))
    
    # Objetivo: Mostrar estadísticas reales del usuario en el dashboard 
    user = Usuario.query.get(u_id)  
    stats = UsuarioService.obtener_estadisticas_globales(u_id)
    return render_template("dashboard.html", stats=stats, user=user)

#--- Examen ---
@usuario_bp.route("/examen")
def examen():
    
    return render_template("examen.html") 
# --- Examen: Procesar ---
@usuario_bp.route("/procesar_examen", methods=["POST"])
def procesar_examen():
    u_id = session.get('usuario_id')
    if not u_id:
        return redirect(url_for('usuario.login'))   
    
    # Diccionario con las respuestas correctas para comparar
    correctas = {
        "p1": {"texto": "¿Qué es el Aprendizaje Supervisado?", "ans": "B"},
        "p2": {"texto": "¿Cuál es la función principal de una Red Neuronal?", "ans": "B"},
        "p3": {"texto": "¿Qué significa Overfitting?", "ans": "A"},
        "p4": {"texto": "¿Qué es un Prompt?", "ans": "B"},
        "p5": {"texto": "¿Cuál es un ejemplo de IA Generativa?", "ans": "B"}
    }

    aciertos = 0
    # Recorremos las 5 preguntas
    for i in range(1, 6):
        llave = f"p{i}"
        resp_usuario = request.form.get(llave)
        if not resp_usuario:
            resp_usuario = "No respondida"
        resp_correcta = correctas[llave]["ans"]
        es_correcta = 1 if resp_usuario == resp_correcta else 0
        if es_correcta: aciertos += 1

        # GUARDAR EN TU TABLA 'respuesta'
        nueva_resp = Respuesta(
            id_evaluacion=u_id, # Usamos el ID usuario como referencia
            pregunta=correctas[llave]["texto"],
            respuesta_usuario=resp_usuario,
            respuesta_correcta=resp_correcta,
            resultado=es_correcta
        )
        db.session.add(nueva_resp)

    # Calcular nivel y actualizar tabla Usuario
    puntaje = (aciertos / 5) * 100
    nivel = "Avanzado" if puntaje >= 70 else "Principiante"
    
    #Actualizamos el nivel del usuario en la tabla Usuario
    user = Usuario.query.get(u_id)
    user.nivel = nivel
    db.session.commit()
    
    return render_template("resultado_examen.html", puntaje=puntaje, nivel=nivel, aciertos=aciertos)

#--- Ruta --- 
@usuario_bp.route("/ruta")
def ruta():
    u_id = session.get('usuario_id')
    if not u_id:
        return redirect(url_for('usuario.login'))
    
    # --- 1. DATOS REALES DE LA DB USANDO EL SERVICE ---
    # Reemplazamos obtener_stats por el Service
    stats_globales = UsuarioService.obtener_estadisticas_globales(u_id)
    resueltos = stats_globales['total_ejercicios']
    aciertos_totales = stats_globales['total_aciertos']
    
    # También necesitamos el nivel real del usuario para el Motor IA
    user = Usuario.query.get(u_id)
    
    # --- 2. INSTANCIAMOS EL MOTOR ---
    motor = MotorIA()
    
    # Usamos los datos reales del Service para que la IA decida
    accion_ia = motor.decidir_accion(resueltos, aciertos_totales) 
    
    # --- 3. LÓGICA DE PROGRESIÓN ---
    # (Mantenemos estas variables para que la vista no truene, 
    # pero ya están conectadas al motor real)
    tema_actual = 'Operaciones Básicas' # O el tema que estés manejando
    nivel_visual = user.nivel
    
    # --- 4. GENERACIÓN DE CONFIGURACIÓN ---
    config_sesion = motor.generar_configuracion_ejercicios(nivel_visual, accion_ia)
    
    # --- 5. SIGUIENTE PASO ---
    siguiente_tema = "¡Has terminado todos los temas!"
    if accion_ia == "AVANZAR":
        siguiente_tema = motor.obtener_siguiente_tema(tema_actual)
    elif accion_ia == "REFORZAR":
        siguiente_tema = f"Repasando: {tema_actual}"
    else:
        siguiente_tema = tema_actual

    # --- 6. PREPARAMOS LOS DATOS PARA LA VISTA ---
    info_ruta = {
        'nivel_actual': nivel_visual,
        'estado_ia': accion_ia,
        'proximo_reto': siguiente_tema,
        'config_practica': config_sesion
    }
    
    # Mantenemos los módulos simulados por ahora (Sprint 4 los haremos reales)
    modulos_db = [
        {'id': 1, 'nombre': 'Fundamentos', 'progreso': 100, 'status': 'completado'},
        {'id': 2, 'nombre': 'Operaciones Básicas', 'progreso': 50, 'status': 'en_curso'},
        {'id': 3, 'nombre': 'Ecuaciones de Primer Grado', 'progreso': 0, 'status': 'bloqueado'}
    ]
    
    alerta_refuerzo = True if accion_ia == "REFORZAR" else False

    return render_template(
        "ruta.html", 
        ruta=info_ruta, 
        modulos=modulos_db, 
        alerta=alerta_refuerzo
    )

# --- Práctica ---
@usuario_bp.route("/practica")
def practica():
    
    tema_practicar = "Ecuaciones de Primer Grado" # Esto lo podríamos sacar del Motor IA en el futuro, por ahora lo dejamos fijo para que veas cómo se conecta todo
    # 1. El motor de IA nos da la configuración
    motor = MotorIA()
    config = motor.generar_configuracion_ejercicios('Principiante', 'MANTENER')

    # 2. El generador crea los problemas matemáticos reales
    generador = GeneradorEjercicios()
    ejercicios = generador.crear_sesion(config)

    # 3. Se los mandamos a la pantalla de práctica
    return render_template("practica.html", ejercicios=ejercicios, tema_nombre=tema_practicar)
# --- Practica: Procesar --- 
@usuario_bp.route("/procesar_practica", methods=["POST"])
def procesar_practica():

    respuesta = request.form.get("respuesta_practica")
    
    if respuesta == "12":
        mensaje = "¡Correcto! Eres un crack de las mates."
    else:
        mensaje = f"Casi, pero {respuesta} no es la respuesta. ¡Inténtalo de nuevo!"
    
    return render_template("resultado_practica.html", mensaje=mensaje) 
# --- Practica: Finalizar ---
@usuario_bp.route("/finalizar_practica", methods=['POST'])
def finalizar_practica():
    data = request.get_json()
    u_id = session.get('usuario_id')
    if not u_id:
        return jsonify({"status": "error", "message": "Usuario no autenticado"}), 401
    
    tema_recibido = data.get('tema', 'General')  # Por ahora lo dejamos como "General", pero en el futuro lo enviaremos desde el JS para saber qué tema se practicó
    
    # El Service se encarga de registrar el progreso y también de manejar la lógica de subida de nivel
    UsuarioService.registrar_progreso(
        u_id=u_id,
        tema=tema_recibido,
        total=data.get('total'),
        aciertos=data.get('aciertos'),
        dificultad='Normal'
    )
    
    return jsonify({"status": "success"})  

# --- Resultados ---
@usuario_bp.route("/resultados")
def resultados():
    # Obtenemos los últimos resultados de la DB
    ultimo_progreso = ProgresoUsuario.query.filter_by(usuario_id=session['usuario_id']).order_by(ProgresoUsuario.fecha.desc()).first()
    
    if not ultimo_progreso:
        return redirect(url_for('usuario.dashboard'))

    motor = MotorIA()
    # La IA analiza el último desempeño
    decision = motor.decidir_accion(ultimo_progreso.ejercicios_realizados, ultimo_progreso.aciertos)
    
    return render_template('resultados.html', 
                           progreso=ultimo_progreso, 
                           decision=decision)

# --- Progreso ---
@usuario_bp.route('/progreso')
def progreso():
    u_id = session.get('usuario_id')
    if not u_id:
        return redirect(url_for('usuario.login'))
    
    #Usamos get or_404 para asegurarnos de que el usuario existe antes de mostrar su progreso, si no existe, lanzará un error 404
    user = Usuario.query.get_or_404(u_id)
    
    # Llamamos al servicio para obtener todo el paquete de datos
    datos_reales = UsuarioService.obtener_resumen_progreso(u_id)
    datos_reales['nivel'] = user.nivel
    
    return render_template('progreso.html', stats=datos_reales)

# --- Tutor ---
@usuario_bp.route("/tutor")
def tutor():
    # El HTML espera una variable 'historial'. Se la pasamos vacía al inicio.
    return render_template("tutor.html", historial=None)
# --- Tutor: Preguntar ---
@usuario_bp.route("/preguntar_tutor", methods=["POST"])
def preguntar_tutor():
    pregunta = request.form.get("pregunta")
    
    # Simulamos un historial para que veas cómo se ve en el HTML
    historial_simulado = [
        {"rol": "Usuario", "texto": pregunta},
        {"rol": "Tutor IA", "texto": f"Claro, sobre '{pregunta}', mi consejo es que revises las bases de cálculo..."}
    ]
    
    return render_template("tutor.html", historial=historial_simulado)

# --- Reportes ---
@usuario_bp.route("/reportes")
def reportes():
    # 1. Seguridad: Solo si el usuario es Docente o Admin
    if session.get('tipo_usuario') != 'Docente':
        return "Acceso denegado. Solo los docentes pueden ver reportes.", 403

    # 2. Consultar todos los alumnos que ya hicieron el examen
    # Traemos nombre, correo y nivel
    alumnos = Usuario.query.filter(Usuario.tipo_usuario == 'Estudiante').all()

    return render_template("reportes.html", alumnos=alumnos)

# --- LOGOUT ---
@usuario_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('usuario.login'))