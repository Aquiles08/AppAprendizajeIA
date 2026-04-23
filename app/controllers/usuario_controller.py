from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify 
from config.database import db # Importamos la instancia de SQLAlchemy para hacer consultas a la DB
from app.utils import bcrypt # Importamos bcrypt para verificar contraseñas
from google import genai # Importamos el cliente de Gemini para generar ejercicios personalizados
import os

#Modelos
from app.models.tema import Tema # Importamos el modelo Tema para hacer consultas a la tabla de temas
from app.models.usuario import Usuario # Importamos el modelo Usuario para hacer consultas a la tabla de usuarios
from app.models.curso import Curso # Importamos el modelo Curso para hacer consultas a la tabla de cursos
from app.models.respuesta import Respuesta # Importamos el modelo Respuesta para guardar las respuestas del examen
from app.models.progresoUsuario import ProgresoUsuario # Importamos el modelo ProgresoUsuario para guardar el progreso de los usuarios
from app.models.historialTutor import HistorialTutor # Importamos el modelo HistorialTutor para guardar el historial de conversaciones con el tutor IA
from app.models.evaluacion import Evaluacion # Importamos el modelo Evaluacion para guardar los resultados de los exámenes

#Servicios y lógica
from app.services.ia_service import AIService # Importamos el servicio de IA para generar ejercicios personalizados
from app.services.usuario_service import UsuarioService # Importamos el servicio de usuario para manejar la lógica de negocio relacionada con los usuarios
from app.logic.motor_ia import MotorIA # Importamos el motor de IA para tomar decisiones en la ruta de práctica
from app.logic.generador import GeneradorEjercicios # Importamos el generador de ejercicios para crear problemas matemáticos personalizados

ia_service = AIService() # Creamos una instancia del servicio de IA para usarlo en las rutas
usuario_bp = Blueprint('usuario', __name__)
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY')) # Creamos el cliente de Gemini

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
            
            # Redirección basada en el tipo de usuario
            if user.tipo_usuario.lower() == 'docente':
                return redirect(url_for('usuario.dashboard_docente'))
            else:
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


# --- RUTAS DEL DASHBOARD ESTUDIANTE---

# --- Dashboard ---
@usuario_bp.route("/dashboard")
def dashboard():
    u_id = session.get('usuario_id')
    if not u_id:
        return redirect(url_for('usuario.login'))
    
    # Objetivo: Mostrar estadísticas reales del usuario en el dashboard 
    user = Usuario.query.get(u_id)  
    historial = ProgresoUsuario.query.filter_by(usuario_id=u_id).order_by(ProgresoUsuario.fecha.desc()).limit(5).all()
    
    total_ejercicios = sum(p.ejercicios_realizados for p in historial)
    total_aciertos = sum(p.aciertos for p in historial)
    
    return render_template("dashboard.html", user=user, 
                           historial=historial, 
                           total_ejercicios=total_ejercicios, 
                           total_aciertos=total_aciertos)

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
    
    correctas = {
        "p1": {"texto": "¿Qué es el Aprendizaje Supervisado?", "ans": "B"},
        "p2": {"texto": "¿Cuál es la función principal de una Red Neuronal?", "ans": "B"},
        "p3": {"texto": "¿Qué significa Overfitting?", "ans": "A"},
        "p4": {"texto": "¿Qué es un Prompt?", "ans": "B"},
        "p5": {"texto": "¿Cuál es un ejemplo de IA Generativa?", "ans": "B"}
    }

    aciertos = 0
    respuestas_a_guardar = []

    # 1. Primero calculamos los aciertos
    for i in range(1, 6):
        llave = f"p{i}"
        resp_usuario = request.form.get(llave) or "No respondida"
        resp_correcta = correctas[llave]["ans"]
        es_correcta = 1 if resp_usuario == resp_correcta else 0
        if es_correcta: aciertos += 1
        
        # Guardamos los datos temporalmente en una lista
        respuestas_a_guardar.append({
            "pregunta": correctas[llave]["texto"],
            "usuario": resp_usuario,
            "correcta": resp_correcta,
            "resultado": es_correcta
        })

    puntaje = (aciertos / 5) * 100

    # 2. CREAR LA EVALUACIÓN (CRUCIAL para evitar el error)
    from datetime import datetime
    nueva_evaluacion = Evaluacion(
        id_usuario=u_id,
        id_tema=1, # O el ID del tema correspondiente
        puntuacion=puntaje,
        fecha=datetime.now(),
        tipo_evaluacion='Examen'
    )
    db.session.add(nueva_evaluacion)
    db.session.flush() # Esto genera el id_evaluacion SIN cerrar la transacción

    # 3. AHORA SÍ, GUARDAR LAS RESPUESTAS con el ID real
    for r in respuestas_a_guardar:
        nueva_resp = Respuesta(
            id_evaluacion=nueva_evaluacion.id_evaluacion, # <--- ID REAL generado arriba
            pregunta=r["pregunta"],
            respuesta_usuario=r["usuario"],
            respuesta_correcta=r["correcta"],
            resultado=r["resultado"]
        )
        db.session.add(nueva_resp)

    # 4. Actualizar nivel del usuario
    nivel = "Avanzado" if puntaje >= 70 else "Principiante"
    user = Usuario.query.get(u_id)
    user.nivel = nivel
    
    db.session.commit() # Un solo commit para guardar TODO
    
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
    u_id = session.get('usuario_id')
    if not u_id:
        return redirect(url_for('usuario.login'))

    # 1. Obtenemos el nivel real del usuario para que la IA se adapte
    user = Usuario.query.get(u_id)
    tema_practicar = "Ecuaciones de Primer Grado" 
    
    # Pedimos 3 ejercicios con la dificultad que tiene el usuario en la DB
    ejercicios = ia_service.generar_ejercicios_ia(
        tema=tema_practicar, 
        dificultad=user.nivel, 
        cantidad=3
    )

    # Si la IA falla, usamos un respaldo para que no truene la página
    if not ejercicios:
        ejercicios = [{
            "pregunta": "2x = 10", 
            "solucion": "5", 
            "explicacion": "Divide 10 entre 2"
        }]

    # 3. Mandamos los ejercicios reales de Gemini a la pantalla
    return render_template("practica.html", ejercicios=ejercicios, tema_nombre=tema_practicar)
# --- Practica: Procesar (MODIFICADA PARA VALIDACIÓN DINÁMICA) --- 
@usuario_bp.route("/procesar_practica", methods=["POST"])
def procesar_practica():
    u_id = session.get('usuario_id')
    if not u_id:
        return redirect(url_for('usuario.login'))

    resultados_detallados = []
    aciertos = 0
    total_ejercicios = 3

    for i in range(1, total_ejercicios + 1):
        # 1. Obtenemos los datos y limpiamos espacios de los extremos
        resp_usuario = request.form.get(f"respuesta_usuario_{i}", "").strip()
        resp_correcta = request.form.get(f"respuesta_correcta_{i}", "").strip()
        pregunta = request.form.get(f"pregunta_{i}", "")
        explicacion = request.form.get(f"explicacion_{i}", "")

        # 2. LIMPIEZA PROFUNDA: Quitamos todos los espacios para comparar (ej: "81 / 8" -> "81/8")
        clean_user = resp_usuario.replace(" ", "").lower()
        clean_correct = resp_correcta.replace(" ", "").lower()

        # 3. Lógica para el "Sin Respuesta" por culpa del 'disabled' en JS
        # Si el usuario NO mandó nada, pero el ejercicio se marcó como correcto en el cliente,
        # asumimos que fue por el disabled.
        es_correcta = clean_user == clean_correct if clean_user != "" else False
        
        # --- PARCHE PARA DISABLED ---
        # Si el usuario acierta en el JS, el botón se bloquea y el input no llega.
        # Podrías dejar que el JS mande los aciertos, pero para validar aquí:
        if es_correcta:
            aciertos += 1

        resultados_detallados.append({
            "pregunta": pregunta,
            "tu_respuesta": resp_usuario,
            "correcta": resp_correcta,
            "es_correcta": es_correcta,
            "explicacion": explicacion
        })

    # Guardar progreso...
    UsuarioService.registrar_progreso(u_id=u_id, tema="Ecuaciones de Primer Grado", 
                                     total=total_ejercicios, aciertos=aciertos, dificultad="Normal")

    return render_template("resultado_practica.html", resultados=resultados_detallados, 
                           total=total_ejercicios, aciertos=aciertos)
# --- Practica: Finalizar ---
@usuario_bp.route("/finalizar_practica", methods=['POST'])
def finalizar_practica():
    data = request.get_json()
    u_id = session.get('usuario_id')
    if not u_id:
        return jsonify({"status": "error", "message": "Usuario no autenticado"}), 401
    
    # El Service se encarga de registrar el progreso y también de manejar la lógica de subida de nivel
    UsuarioService.registrar_progreso(
        u_id=u_id,
        tema=data.get('tema', 'General'),
        total=data.get('total'),
        aciertos=data.get('aciertos'),
        dificultad='Normal'
    )
    
    return jsonify({"status": "success", "message": "Progreso registrado correctamente"})  

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
@usuario_bp.route("/tutor", methods=["GET", "POST"])
def tutor():
    u_id = session.get('usuario_id')
    if not u_id:
        return redirect(url_for('usuario.login'))
    
    if request.method == "POST":
        datos = request.get_json()
        pregunta_usuario = datos.get("mensaje")

        # 1. Guardar lo que escribió Gael
        nuevo_msj = HistorialTutor(usuario_id=u_id, contenido=pregunta_usuario, es_bot=False)
        db.session.add(nuevo_msj)

        try:
            # Llamada a Gemini 2.5 (tu código del test_aq)
            response = client.models.generate_content(
                model="gemini-2.5-flash", 
                contents=pregunta_usuario
            )
            respuesta_ia = response.text
            
            # 2. Guardar lo que respondió el Robot
            respuesta_bot = HistorialTutor(usuario_id=u_id, contenido=respuesta_ia, es_bot=True)
            db.session.add(respuesta_bot)
            
            db.session.commit() # Guardamos ambos mensajes en MySQL
            return jsonify({"respuesta": respuesta_ia})
        except Exception as e:
            db.session.rollback()
            return jsonify({"respuesta": f"Error: {str(e)}"}), 500

    # 3. Al cargar (GET), traer el historial ordenado por fecha
    historial = HistorialTutor.query.filter_by(usuario_id=u_id).order_by(HistorialTutor.fecha.asc()).all()
    user = Usuario.query.get(u_id)
    return render_template("tutor.html", historial=historial, user=user)
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

# --- LOGOUT ---
@usuario_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('usuario.login'))


# --- RUTAS DEL DASHBOARD DOCENTE ---

# --- Dashboard Docente ---
@usuario_bp.route("/dashboard_docente")
def dashboard_docente():
    u_id = session.get('usuario_id')
    rol = session.get('tipo_usuario')
    
    # Verificamos que sea un docente real en la sesión
    if not u_id or rol.lower() != 'docente':
        return redirect(url_for('usuario.login'))
    
    estudiantes = Usuario.query.filter_by(tipo_usuario='Estudiante').all()
        
    return render_template("dashboard_docente.html", alumnos=estudiantes)

# --- Reportes ---
@usuario_bp.route("/reportes")
def reportes():
    # Seguridad
    tipo = session.get('tipo_usuario')
    if not tipo or tipo.lower() != 'docente':
        return redirect(url_for('usuario.login'))

    # 1. Lista de alumnos con sus niveles (Lo que ya tienes)
    alumnos = Usuario.query.filter_by(tipo_usuario='Estudiante').all()

    # 2. Análisis de Datos (SCRUM-39)
    # Calculamos cuántos hay de cada nivel para una vista rápida
    total_estudiantes = len(alumnos)
    conteo_expertos = Usuario.query.filter_by(tipo_usuario='Estudiante', nivel='Experto').count()
    conteo_principiantes = Usuario.query.filter_by(tipo_usuario='Estudiante', nivel='Principiante').count()
    
    # Pendientes de examen
    sin_examen = total_estudiantes - (conteo_expertos + conteo_principiantes)

    stats = {
        'total': total_estudiantes,
        'expertos': conteo_expertos,
        'principiantes': conteo_principiantes,
        'pendientes': sin_examen
    }

    return render_template("reportes.html", alumnos=alumnos, stats=stats)